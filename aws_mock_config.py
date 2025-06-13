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
        self.user_sessions_table = MockDynamoDBTable('ielts-genai-prep-user-sessions')
        self.purchase_records_table = MockDynamoDBTable('ielts-genai-prep-purchases')
        
        # ElastiCache
        self.session_cache = MockElastiCache()
        
        # CloudWatch
        self.cloudwatch = MockCloudWatch()
        
        # Environment simulation
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        self.account_id = '123456789012'  # Mock account ID
        
        print(f"[AWS_MOCK] Services initialized for region: {self.region}")
    
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
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health"""
        return {
            'dynamodb_tables': {
                'auth_tokens': len(self.auth_tokens_table.items),
                'user_sessions': len(self.user_sessions_table.items),
                'purchase_records': len(self.purchase_records_table.items)
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