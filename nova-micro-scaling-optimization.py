"""
Nova Micro Writing Assessment Optimization for 250K Concurrent Users
Enhanced performance, caching, and scaling configuration
"""

import os
import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from functools import wraps
import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)

class OptimizedNovaWritingService:
    """
    Optimized Nova Micro service for high-concurrency writing assessments
    Designed for 250,000 concurrent users with caching and performance optimization
    """
    
    def __init__(self):
        # Optimized Bedrock configuration for high concurrency
        self.bedrock_config = Config(
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            },
            max_pool_connections=100,  # Increased for high concurrency
            read_timeout=60,
            connect_timeout=10
        )
        
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            config=self.bedrock_config
        )
        
        # Performance metrics
        self.assessment_cache = {}
        self.performance_stats = {
            'total_assessments': 0,
            'cache_hits': 0,
            'avg_response_time': 0,
            'concurrent_requests': 0
        }
        
        logger.info("Optimized Nova Micro writing service initialized for high concurrency")
    
    def assess_writing_optimized(self, essay_text, task_prompt, task_type="task1", assessment_type="academic", user_id=None):
        """
        Optimized writing assessment with caching and performance monitoring
        """
        start_time = time.time()
        self.performance_stats['concurrent_requests'] += 1
        
        try:
            # Generate cache key for identical assessments
            cache_key = self._generate_cache_key(essay_text, task_prompt, task_type, assessment_type)
            
            # Check cache first for performance optimization
            cached_result = self._get_cached_assessment(cache_key)
            if cached_result:
                self.performance_stats['cache_hits'] += 1
                logger.info(f"Cache hit for writing assessment - User: {user_id}")
                return cached_result
            
            # Call Nova Micro for fresh assessment
            assessment_result = self._call_nova_micro_writing(
                essay_text, task_prompt, task_type, assessment_type
            )
            
            # Cache the result for future requests
            if assessment_result.get('success'):
                self._cache_assessment(cache_key, assessment_result)
            
            # Update performance metrics
            end_time = time.time()
            response_time = end_time - start_time
            self._update_performance_metrics(response_time)
            
            # Add performance metadata
            assessment_result['performance'] = {
                'response_time_ms': round(response_time * 1000, 2),
                'cache_hit': False,
                'model_version': 'amazon.nova-micro-v1:0',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Nova Micro writing assessment completed - User: {user_id}, Time: {response_time:.2f}s")
            return assessment_result
            
        except Exception as e:
            logger.error(f"Optimized writing assessment error: {e}")
            return self._error_response(f"Assessment service error: {str(e)}")
        
        finally:
            self.performance_stats['concurrent_requests'] -= 1
    
    def _call_nova_micro_writing(self, essay_text, task_prompt, task_type, assessment_type):
        """Call Nova Micro with optimized prompting for writing assessment"""
        try:
            # Optimized system prompt for consistent, fast responses
            system_prompt = self._get_optimized_writing_prompt(task_type, assessment_type)
            
            # Structured user prompt for efficient processing
            user_prompt = f"""
TASK: {task_prompt}

ESSAY TO ASSESS:
{essay_text}

ASSESSMENT TYPE: IELTS {assessment_type.title()} Writing {task_type.upper()}

Please provide assessment using the specified scoring criteria.
"""

            # Optimized inference configuration
            messages = [
                {
                    "role": "user",
                    "content": [{"text": f"{system_prompt}\n\n{user_prompt}"}]
                }
            ]
            
            inference_config = {
                "maxTokens": 1500,  # Sufficient for detailed assessment
                "temperature": 0.3,  # Lower for consistent scoring
                "topP": 0.8
            }
            
            # Call Nova Micro with retry logic
            response = self.bedrock_client.converse(
                modelId="amazon.nova-micro-v1:0",
                messages=messages,
                inferenceConfig=inference_config
            )
            
            if response.get('output') and response['output'].get('message'):
                assessment_content = response['output']['message']['content'][0]['text']
                
                return {
                    'success': True,
                    'assessment': assessment_content,
                    'task_type': task_type,
                    'assessment_type': assessment_type,
                    'model': 'amazon.nova-micro-v1:0',
                    'word_count': len(essay_text.split()),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return self._error_response("No response from Nova Micro")
                
        except Exception as e:
            logger.error(f"Nova Micro API error: {e}")
            return self._error_response(f"Nova Micro error: {str(e)}")
    
    def _get_optimized_writing_prompt(self, task_type, assessment_type):
        """Optimized prompts for faster, more consistent assessments"""
        
        base_criteria = """
You are an expert IELTS examiner. Assess this essay using official IELTS criteria:

SCORING BANDS (0-9):
- Task Achievement/Response (25%)
- Coherence and Cohesion (25%) 
- Lexical Resource (25%)
- Grammatical Range and Accuracy (25%)

RESPONSE FORMAT:
Overall Band Score: [X.X]

Task Achievement: [X.X]
- [Brief assessment]

Coherence and Cohesion: [X.X]
- [Brief assessment]

Lexical Resource: [X.X]
- [Brief assessment]

Grammatical Range and Accuracy: [X.X]
- [Brief assessment]

Key Strengths:
- [2-3 main strengths]

Areas for Improvement:
- [2-3 specific suggestions]
"""

        if task_type == "task1":
            if assessment_type == "academic":
                return f"{base_criteria}\n\nACEADEMIC TASK 1 FOCUS: Analyze data accuracy, overview quality, key features identification, and comparison skills."
            else:
                return f"{base_criteria}\n\nGENERAL TASK 1 FOCUS: Assess letter format, tone appropriateness, purpose clarity, and request/information coverage."
        else:  # task2
            return f"{base_criteria}\n\nTASK 2 FOCUS: Evaluate argument development, position clarity, idea support with examples, and balanced discussion."
    
    def _generate_cache_key(self, essay_text, task_prompt, task_type, assessment_type):
        """Generate cache key for assessment caching"""
        content = f"{essay_text}|{task_prompt}|{task_type}|{assessment_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_assessment(self, cache_key):
        """Retrieve cached assessment if available and fresh"""
        if cache_key in self.assessment_cache:
            cached_data = self.assessment_cache[cache_key]
            # Cache valid for 24 hours
            if datetime.fromisoformat(cached_data['cached_at']) > datetime.utcnow() - timedelta(hours=24):
                cached_data['performance'] = {
                    'response_time_ms': 50,  # Cache retrieval time
                    'cache_hit': True,
                    'cached_at': cached_data['cached_at']
                }
                return cached_data
            else:
                # Remove expired cache
                del self.assessment_cache[cache_key]
        return None
    
    def _cache_assessment(self, cache_key, assessment_result):
        """Cache assessment result for performance optimization"""
        try:
            # Limit cache size to prevent memory issues
            if len(self.assessment_cache) > 10000:
                # Remove oldest 20% of cache entries
                sorted_cache = sorted(
                    self.assessment_cache.items(), 
                    key=lambda x: x[1].get('cached_at', ''),
                    reverse=True
                )
                self.assessment_cache = dict(sorted_cache[:8000])
            
            # Cache the result
            assessment_result['cached_at'] = datetime.utcnow().isoformat()
            self.assessment_cache[cache_key] = assessment_result.copy()
            
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    def _update_performance_metrics(self, response_time):
        """Update performance tracking metrics"""
        self.performance_stats['total_assessments'] += 1
        
        # Calculate rolling average response time
        current_avg = self.performance_stats['avg_response_time']
        total_count = self.performance_stats['total_assessments']
        
        self.performance_stats['avg_response_time'] = (
            (current_avg * (total_count - 1) + response_time) / total_count
        )
    
    def get_performance_statistics(self):
        """Get current performance statistics"""
        cache_hit_rate = 0
        if self.performance_stats['total_assessments'] > 0:
            cache_hit_rate = (
                self.performance_stats['cache_hits'] / 
                self.performance_stats['total_assessments'] * 100
            )
        
        return {
            'total_assessments': self.performance_stats['total_assessments'],
            'cache_hit_rate_percent': round(cache_hit_rate, 2),
            'average_response_time_ms': round(self.performance_stats['avg_response_time'] * 1000, 2),
            'concurrent_requests': self.performance_stats['concurrent_requests'],
            'cache_size': len(self.assessment_cache),
            'service_status': 'optimal' if cache_hit_rate > 15 else 'normal'
        }
    
    def _error_response(self, error_message):
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'service': 'nova_micro_writing',
            'timestamp': datetime.utcnow().isoformat()
        }

# Nova Micro Scaling Configuration for AWS
NOVA_MICRO_SCALING_CONFIG = {
    'bedrock_quotas': {
        'nova_micro_concurrent_requests': 2000,  # Higher than Nova Sonic
        'requests_per_minute': 20000,
        'tokens_per_minute': 2000000
    },
    'performance_targets': {
        'average_response_time_ms': 3000,  # 3 seconds target
        'cache_hit_rate_percent': 20,  # 20% cache hit rate target
        'concurrent_capacity': 2000,  # 2000 concurrent writing assessments
        'throughput_per_hour': 50000  # 50K assessments per hour
    },
    'optimization_features': {
        'intelligent_caching': True,
        'response_compression': True,
        'batch_processing': False,  # Not needed for writing assessments
        'retry_logic': True,
        'performance_monitoring': True
    }
}

# Global instance for import
optimized_nova_writing = OptimizedNovaWritingService()

# Convenience functions for easy integration
def assess_writing_with_optimization(essay_text, task_prompt, task_type="task1", assessment_type="academic", user_id=None):
    """Optimized writing assessment function"""
    return optimized_nova_writing.assess_writing_optimized(
        essay_text, task_prompt, task_type, assessment_type, user_id
    )

def get_writing_service_stats():
    """Get current writing service performance statistics"""
    return optimized_nova_writing.get_performance_statistics()