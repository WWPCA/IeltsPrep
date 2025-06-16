"""
AWS Mock Services Configuration for .replit Environment
Simulates DynamoDB, ElastiCache, and CloudWatch for local testing
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class MockDynamoDBTable:
    """Simulates DynamoDB AuthTokens table with TTL support"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.items = {}
        self.gsi_indexes = {}
    
    def put_item(self, item: Dict[str, Any]) -> bool:
        """Store item with automatic TTL cleanup"""
        item_key = item.get('token_id', item.get('session_id'))
        if not item_key:
            return False
        
        # Add DynamoDB metadata
        item['_created_at'] = time.time()
        item['_table'] = self.table_name
        
        self.items[item_key] = item
        self._cleanup_expired_items()
        
        print(f"[DYNAMODB] PUT {self.table_name}: {item_key}")
        return True
    
    def get_item(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve item if not expired"""
        self._cleanup_expired_items()
        item = self.items.get(key)
        
        if item:
            print(f"[DYNAMODB] GET {self.table_name}: {key} -> Found")
            return item
        else:
            print(f"[DYNAMODB] GET {self.table_name}: {key} -> Not Found")
            return None
    
    def delete_item(self, key: str) -> bool:
        """Delete item"""
        if key in self.items:
            del self.items[key]
            print(f"[DYNAMODB] DELETE {self.table_name}: {key}")
            return True
        return False
    
    def update_item(self, key: str, updates: Dict[str, Any]) -> bool:
        """Update existing item"""
        if key in self.items:
            self.items[key].update(updates)
            print(f"[DYNAMODB] UPDATE {self.table_name}: {key}")
            return True
        return False
    
    def scan(self, filter_expression: Optional[str] = None) -> list:
        """Scan table with optional filtering"""
        self._cleanup_expired_items()
        items = list(self.items.values())
        print(f"[DYNAMODB] SCAN {self.table_name}: {len(items)} items")
        return items
    
    def _cleanup_expired_items(self):
        """Remove items past their TTL"""
        current_time = time.time()
        expired_keys = []
        
        for key, item in self.items.items():
            ttl = item.get('ttl', item.get('expires_at'))
            if ttl and current_time > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.items[key]
            print(f"[DYNAMODB] TTL_EXPIRED {self.table_name}: {key}")

class MockElastiCache:
    """Simulates ElastiCache Redis for session storage"""
    
    def __init__(self):
        self.cache = {}
        self.expirations = {}
    
    def set(self, key: str, value: Any, ex: int = 3600) -> bool:
        """Set key with expiration"""
        self.cache[key] = value
        self.expirations[key] = time.time() + ex
        print(f"[ELASTICACHE] SET {key} (expires in {ex}s)")
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """Get key if not expired"""
        self._cleanup_expired()
        value = self.cache.get(key)
        
        if value:
            print(f"[ELASTICACHE] GET {key} -> Found")
            return value
        else:
            print(f"[ELASTICACHE] GET {key} -> Not Found")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key"""
        if key in self.cache:
            del self.cache[key]
            if key in self.expirations:
                del self.expirations[key]
            print(f"[ELASTICACHE] DELETE {key}")
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and not expired"""
        self._cleanup_expired()
        exists = key in self.cache
        print(f"[ELASTICACHE] EXISTS {key} -> {exists}")
        return exists
    
    def ttl(self, key: str) -> int:
        """Get time to live for key"""
        if key not in self.expirations:
            return -1
        
        remaining = int(self.expirations[key] - time.time())
        return max(0, remaining)
    
    def _cleanup_expired(self):
        """Remove expired keys"""
        current_time = time.time()
        expired_keys = []
        
        for key, expiry in self.expirations.items():
            if current_time > expiry:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            del self.expirations[key]
            print(f"[ELASTICACHE] EXPIRED {key}")

class MockCloudWatch:
    """Simulates CloudWatch logging and metrics"""
    
    def __init__(self):
        self.log_groups = {}
        self.metrics = []
    
    def put_log_events(self, log_group: str, log_stream: str, events: list):
        """Store log events"""
        if log_group not in self.log_groups:
            self.log_groups[log_group] = {}
        
        if log_stream not in self.log_groups[log_group]:
            self.log_groups[log_group][log_stream] = []
        
        for event in events:
            log_entry = {
                'timestamp': event.get('timestamp', int(time.time() * 1000)),
                'message': event.get('message', ''),
                'ingestionTime': int(time.time() * 1000)
            }
            self.log_groups[log_group][log_stream].append(log_entry)
        
        print(f"[CLOUDWATCH] LOGS {log_group}/{log_stream}: {len(events)} events")
    
    def put_metric_data(self, namespace: str, metric_data: list):
        """Store metrics"""
        for metric in metric_data:
            metric_entry = {
                'namespace': namespace,
                'metric_name': metric.get('MetricName'),
                'value': metric.get('Value'),
                'unit': metric.get('Unit', 'Count'),
                'timestamp': metric.get('Timestamp', datetime.utcnow()),
                'dimensions': metric.get('Dimensions', [])
            }
            self.metrics.append(metric_entry)
        
        print(f"[CLOUDWATCH] METRICS {namespace}: {len(metric_data)} metrics")
    
    def get_recent_logs(self, log_group: str, limit: int = 100) -> list:
        """Get recent log entries"""
        if log_group not in self.log_groups:
            return []
        
        all_logs = []
        for stream_logs in self.log_groups[log_group].values():
            all_logs.extend(stream_logs)
        
        # Sort by timestamp and return most recent
        all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_logs[:limit]

class AWSMockServices:
    """Central configuration for all AWS mock services"""
    
    def __init__(self):
        # DynamoDB Tables
        self.auth_tokens_table = MockDynamoDBTable('ielts-genai-prep-auth-tokens')
        self.users_table = MockDynamoDBTable('ielts-genai-prep-users')
        self.user_sessions_table = MockDynamoDBTable('ielts-genai-prep-user-sessions')
        self.purchase_records_table = MockDynamoDBTable('ielts-genai-prep-purchases')
        self.assessment_results_table = MockDynamoDBTable('ielts-genai-prep-assessment-results')
        self.assessment_rubrics_table = MockDynamoDBTable('ielts-genai-prep-assessment-rubrics')
        self.user_progress_table = MockDynamoDBTable('ielts-genai-prep-user-progress')
        
        # ElastiCache
        self.session_cache = MockElastiCache()
        
        # CloudWatch
        self.cloudwatch = MockCloudWatch()
        
        # Environment simulation
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        self.account_id = '123456789012'  # Mock account ID
        
        # Initialize IELTS assessment rubrics
        self._setup_assessment_data()
        
        print(f"[AWS_MOCK] Services initialized for region: {self.region}")
    
    def _setup_assessment_data(self):
        """Initialize IELTS assessment rubrics for Nova Sonic and Nova Micro"""
        
        # IELTS Speaking Assessment Rubrics (for Nova Sonic)
        speaking_rubrics = {
            'academic_speaking': {
                'rubric_id': 'ielts_academic_speaking_v2024',
                'assessment_type': 'speaking',
                'criteria': {
                    'fluency_and_coherence': {
                        'band_9': 'Speaks fluently with only rare repetition or self-correction. Develops topics coherently and appropriately.',
                        'band_8': 'Speaks fluently with only occasional repetition or self-correction. Develops topics coherently.',
                        'band_7': 'Speaks at length without noticeable effort or loss of coherence. Uses linking words effectively.',
                        'band_6': 'Speaks at length though may show hesitation. Generally coherent but may lack progression.',
                        'band_5': 'Usually maintains flow but uses repetition and hesitation. Over-uses linking words.',
                        'band_4': 'Cannot respond without noticeable pauses. Speech may be slow with frequent repetition.',
                        'descriptors': ['flow', 'pace', 'coherence', 'topic_development', 'linking_devices']
                    },
                    'lexical_resource': {
                        'band_9': 'Uses vocabulary with full flexibility and precise usage in all topics.',
                        'band_8': 'Uses wide range of vocabulary fluently and flexibly to convey precise meanings.',
                        'band_7': 'Uses vocabulary resource flexibly to discuss variety of topics.',
                        'band_6': 'Has wide enough vocabulary to discuss topics at length.',
                        'band_5': 'Manages to talk about familiar topics but uses vocabulary inappropriately.',
                        'band_4': 'Limited vocabulary prevents discussion of unfamiliar topics.',
                        'descriptors': ['range', 'accuracy', 'flexibility', 'appropriacy', 'paraphrase_ability']
                    },
                    'grammatical_range_and_accuracy': {
                        'band_9': 'Uses wide range of structures with full flexibility and accuracy.',
                        'band_8': 'Uses wide range of structures flexibly with majority error-free.',
                        'band_7': 'Uses range of complex structures with some flexibility.',
                        'band_6': 'Uses mix of simple and complex structures with some errors.',
                        'band_5': 'Uses basic sentence forms with reasonable accuracy.',
                        'band_4': 'Uses only basic sentence forms with frequent errors.',
                        'descriptors': ['complexity', 'range', 'accuracy', 'error_frequency', 'communication_impact']
                    },
                    'pronunciation': {
                        'band_9': 'Uses wide range of pronunciation features with precise control.',
                        'band_8': 'Uses wide range of pronunciation features flexibly.',
                        'band_7': 'Shows all positive features and sustained ability.',
                        'band_6': 'Uses range of pronunciation features with mixed control.',
                        'band_5': 'Shows some effective use of features but not sustained.',
                        'band_4': 'Limited range of pronunciation features.',
                        'descriptors': ['individual_sounds', 'word_stress', 'sentence_stress', 'intonation', 'chunking']
                    }
                },
                'nova_sonic_prompts': {
                    'system_prompt': 'You are Maya, an experienced IELTS examiner conducting a speaking assessment. Follow IELTS speaking test format with Part 1 (familiar topics), Part 2 (long turn), and Part 3 (abstract discussion). Evaluate based on fluency, vocabulary, grammar, and pronunciation.',
                    'part_1_topics': ['work', 'studies', 'hometown', 'family', 'hobbies', 'food', 'transport', 'weather'],
                    'part_2_structure': 'Give candidate cue card with topic, 1 minute preparation, 2 minutes speaking',
                    'part_3_approach': 'Ask abstract questions related to Part 2 topic, probe deeper understanding'
                }
            },
            'general_speaking': {
                'rubric_id': 'ielts_general_speaking_v2024',
                'assessment_type': 'speaking',
                'criteria': {
                    # Same criteria as academic but with different topics and contexts
                    'fluency_and_coherence': {
                        'band_9': 'Speaks fluently with only rare repetition or self-correction. Develops topics coherently and appropriately.',
                        'band_8': 'Speaks fluently with only occasional repetition or self-correction. Develops topics coherently.',
                        'band_7': 'Speaks at length without noticeable effort or loss of coherence. Uses linking words effectively.',
                        'band_6': 'Speaks at length though may show hesitation. Generally coherent but may lack progression.',
                        'band_5': 'Usually maintains flow but uses repetition and hesitation. Over-uses linking words.',
                        'band_4': 'Cannot respond without noticeable pauses. Speech may be slow with frequent repetition.',
                        'descriptors': ['flow', 'pace', 'coherence', 'topic_development', 'linking_devices']
                    }
                },
                'nova_sonic_prompts': {
                    'system_prompt': 'You are Maya, an IELTS examiner for General Training. Focus on everyday situations, practical English usage, and social contexts.',
                    'part_1_topics': ['daily_routine', 'shopping', 'travel', 'entertainment', 'sports', 'technology'],
                    'part_2_structure': 'Practical topics like describing experiences, places, people',
                    'part_3_approach': 'Discuss practical implications and everyday applications'
                }
            }
        }
        
        # IELTS Writing Assessment Rubrics (for Nova Micro)
        writing_rubrics = {
            'academic_writing': {
                'rubric_id': 'ielts_academic_writing_v2024',
                'assessment_type': 'writing',
                'task_1': {
                    'task_achievement': {
                        'band_9': 'Fully satisfies all requirements. Clearly presents fully developed response.',
                        'band_8': 'Covers requirements sufficiently. Clearly presents well-developed response.',
                        'band_7': 'Covers requirements. Clearly presents key features/bullet points.',
                        'band_6': 'Addresses requirements with some omissions. Format appropriate.',
                        'band_5': 'Generally addresses requirements. Format may be inappropriate.',
                        'band_4': 'Attempts to address requirements but fails to cover all.',
                        'descriptors': ['completeness', 'appropriacy', 'accuracy', 'overview', 'key_features']
                    }
                },
                'task_2': {
                    'task_response': {
                        'band_9': 'Fully addresses all parts. Develops clear, comprehensive arguments.',
                        'band_8': 'Sufficiently addresses all parts. Develops relevant arguments.',
                        'band_7': 'Addresses all parts though some more than others.',
                        'band_6': 'Addresses all parts but some may be more developed.',
                        'band_5': 'Addresses the task only partially. Limited development.',
                        'band_4': 'Responds to task but in limited way.',
                        'descriptors': ['position_clarity', 'argument_development', 'examples', 'conclusion']
                    }
                },
                'nova_micro_prompts': {
                    'system_prompt': 'You are an IELTS Academic Writing examiner. Evaluate Task Achievement/Response, Coherence and Cohesion, Lexical Resource, and Grammatical Range and Accuracy. Provide band scores (1-9) and detailed feedback.',
                    'task_1_requirements': 'Describe visual information (graphs, charts, diagrams). Minimum 150 words. Academic tone.',
                    'task_2_requirements': 'Present argument or discussion. Minimum 250 words. Academic essay structure.'
                }
            }
        }
        
        # Store rubrics in database
        for speaking_type, rubric in speaking_rubrics.items():
            self.assessment_rubrics_table.put_item(rubric)
            
        for writing_type, rubric in writing_rubrics.items():
            self.assessment_rubrics_table.put_item(rubric)
            
        print("[AWS_MOCK] IELTS assessment rubrics initialized")
    
    def store_qr_token(self, token_data: Dict[str, Any]) -> bool:
        """Store QR token in AuthTokens table"""
        return self.auth_tokens_table.put_item(token_data)
    
    def get_qr_token(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve QR token from AuthTokens table"""
        return self.auth_tokens_table.get_item(token_id)
    
    def invalidate_qr_token(self, token_id: str) -> bool:
        """Mark QR token as used"""
        return self.auth_tokens_table.update_item(token_id, {
            'used': True,
            'used_at': datetime.utcnow().isoformat()
        })
    
    def create_session(self, session_data: Dict[str, Any]) -> bool:
        """Create session in ElastiCache"""
        session_id = session_data['session_id']
        return self.session_cache.set(session_id, session_data, ex=3600)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from ElastiCache"""
        return self.session_cache.get(session_id)
    
    def log_event(self, log_group: str, message: str, level: str = 'INFO'):
        """Log event to CloudWatch"""
        self.cloudwatch.put_log_events(log_group, 'lambda-stream', [{
            'timestamp': int(time.time() * 1000),
            'message': f"[{level}] {message}"
        }])
    
    def record_metric(self, metric_name: str, value: float, unit: str = 'Count'):
        """Record metric to CloudWatch"""
        self.cloudwatch.put_metric_data('IELTS/GenAI/Prep', [{
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow()
        }])
    
    def get_assessment_rubric(self, assessment_type: str) -> Optional[Dict[str, Any]]:
        """Get IELTS assessment rubric from DynamoDB for Nova Sonic/Micro"""
        return self.assessment_rubrics_table.get_item(assessment_type)
    
    def store_assessment_result(self, result_data: Dict[str, Any]) -> bool:
        """Store assessment result in DynamoDB"""
        return self.assessment_results_table.put_item(result_data)
    
    def get_user_assessments(self, user_email: str) -> list:
        """Get all assessments for a user from DynamoDB"""
        return self.assessment_results_table.scan(f"user_email = '{user_email}'")
    
    def update_user_progress(self, user_email: str, progress_data: Dict[str, Any]) -> bool:
        """Update user progress in DynamoDB"""
        return self.user_progress_table.put_item({
            'user_email': user_email,
            'progress_data': progress_data,
            'updated_at': datetime.utcnow().isoformat()
        })
    
    def get_nova_sonic_prompts(self, assessment_type: str) -> Optional[Dict[str, Any]]:
        """Get Nova Sonic system prompts from DynamoDB rubrics"""
        rubric = self.get_assessment_rubric(assessment_type)
        return rubric.get('nova_sonic_prompts') if rubric else None
    
    def get_nova_micro_prompts(self, assessment_type: str) -> Optional[Dict[str, Any]]:
        """Get Nova Micro system prompts from DynamoDB rubrics"""
        rubric = self.get_assessment_rubric(assessment_type)
        return rubric.get('nova_micro_prompts') if rubric else None

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health"""
        return {
            'dynamodb_tables': {
                'auth_tokens': len(self.auth_tokens_table.items),
                'users': len(self.users_table.items),
                'user_sessions': len(self.user_sessions_table.items),
                'purchase_records': len(self.purchase_records_table.items),
                'assessment_results': len(self.assessment_results_table.items),
                'assessment_rubrics': len(self.assessment_rubrics_table.items),
                'user_progress': len(self.user_progress_table.items)
            },
            'elasticache': {
                'active_sessions': len(self.session_cache.cache)
            },
            'cloudwatch': {
                'log_groups': len(self.cloudwatch.log_groups),
                'metrics_recorded': len(self.cloudwatch.metrics)
            },
            'region': self.region,
            'status': 'healthy'
        }

# Global instance for use across the application
aws_mock = AWSMockServices()

# Environment variable simulation
MOCK_ENV_VARS = {
    'AWS_REGION': 'us-east-1',
    'DYNAMODB_AUTH_TOKENS_TABLE': 'ielts-genai-prep-auth-tokens',
    'DYNAMODB_USER_SESSIONS_TABLE': 'ielts-genai-prep-user-sessions',
    'ELASTICACHE_ENDPOINT': 'mock-elasticache.replit.internal',
    'CLOUDWATCH_LOG_GROUP': '/aws/lambda/ielts-genai-prep'
}

def get_mock_env(key: str, default: str = None) -> str:
    """Get environment variable with mock fallback"""
    return os.environ.get(key, MOCK_ENV_VARS.get(key, default))