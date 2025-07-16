"""
AWS Mock Services Configuration for .replit Environment
Simulates DynamoDB, ElastiCache, and CloudWatch for mobile-first authentication
"""

import os
import json
import time
import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class MockDynamoDBTable:
    """Simulates DynamoDB table with TTL support"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.items = {}
        self.gsi_indexes = {}
    
    def put_item(self, item: Dict[str, Any]) -> bool:
        """Store item with automatic TTL cleanup"""
        # For users table, use email as key; for others, use their primary key
        if self.table_name == 'ielts-genai-prep-users':
            item_key = item.get('email')
        else:
            item_key = item.get('user_id', item.get('session_id', item.get('email')))
        
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
    
    def query(self, key_condition: str, index_name: Optional[str] = None) -> list:
        """Query table with key condition"""
        self._cleanup_expired_items()
        items = list(self.items.values())
        print(f"[DYNAMODB] QUERY {self.table_name}: {len(items)} items")
        return items
    
    def _cleanup_expired_items(self):
        """Remove expired items based on TTL"""
        current_time = time.time()
        expired_keys = []
        
        for key, item in self.items.items():
            # Check for TTL expiration
            if 'ttl' in item and current_time > item['ttl']:
                expired_keys.append(key)
            # Check for session expiration (1 hour)
            elif '_created_at' in item and current_time - item['_created_at'] > 3600:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.items[key]
            print(f"[DYNAMODB] EXPIRED {self.table_name}: {key}")

class MockElastiCacheRedis:
    """Simulates ElastiCache Redis for session storage"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get cached value"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                print(f"[REDIS] GET {key} -> Hit")
                return value
            else:
                del self.cache[key]
                print(f"[REDIS] GET {key} -> Expired")
                return None
        print(f"[REDIS] GET {key} -> Miss")
        return None
    
    def set(self, key: str, value: str, ex: int = 3600) -> bool:
        """Set cached value with expiration"""
        expiry = time.time() + ex
        self.cache[key] = (value, expiry)
        print(f"[REDIS] SET {key} -> TTL: {ex}s")
        return True
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        if key in self.cache:
            del self.cache[key]
            print(f"[REDIS] DELETE {key}")
            return True
        return False

class MockCloudWatch:
    """Simulates CloudWatch for logging"""
    
    def __init__(self):
        self.logs = []
    
    def put_log_events(self, log_group: str, log_stream: str, events: List[Dict[str, Any]]) -> bool:
        """Store log events"""
        timestamp = datetime.utcnow().isoformat()
        for event in events:
            log_entry = {
                'timestamp': timestamp,
                'log_group': log_group,
                'log_stream': log_stream,
                'message': event.get('message', ''),
                'level': event.get('level', 'INFO')
            }
            self.logs.append(log_entry)
            print(f"[CLOUDWATCH] {log_entry['level']}: {log_entry['message']}")
        return True
    
    def get_logs(self, log_group: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent logs"""
        filtered_logs = [log for log in self.logs if log['log_group'] == log_group]
        return filtered_logs[-limit:]

class MockAWSServices:
    """Main AWS services mock for .replit environment"""
    
    def __init__(self):
        self.dynamodb_tables = {
            'ielts-genai-prep-users': MockDynamoDBTable('ielts-genai-prep-users'),
            'ielts-genai-prep-sessions': MockDynamoDBTable('ielts-genai-prep-sessions'),
            'ielts-assessment-results': MockDynamoDBTable('ielts-assessment-results'),
            'ielts-assessment-questions': MockDynamoDBTable('ielts-assessment-questions'),
            'ielts-assessment-rubrics': MockDynamoDBTable('ielts-assessment-rubrics'),
            'ielts-genai-prep-purchases': MockDynamoDBTable('ielts-genai-prep-purchases'),
            'ielts-genai-prep-gdpr-requests': MockDynamoDBTable('ielts-genai-prep-gdpr-requests')
        }
        self.redis = MockElastiCacheRedis()
        self.cloudwatch = MockCloudWatch()
        
        # Initialize with production-like data
        self._initialize_production_data()
    
    def _initialize_production_data(self):
        """Initialize with production-like assessment data"""
        print("[AWS_MOCK] IELTS assessment rubrics initialized")
        
        # Add test user
        test_user = {
            'email': 'test@ieltsgenaiprep.com',
            'password_hash': bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'first_name': 'Test',
            'last_name': 'User',
            'profile_image_url': None,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'user_id': str(uuid.uuid4()),
            'assessment_attempts': {
                'academic_writing': 4,
                'general_writing': 4,
                'academic_speaking': 4,
                'general_speaking': 4
            }
        }
        self.dynamodb_tables['ielts-genai-prep-users'].put_item(test_user)
        
        # Add production test user
        prod_test_user = {
            'email': 'prodtest@ieltsgenaiprep.com',
            'password_hash': bcrypt.hashpw('prodtest123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'first_name': 'Production',
            'last_name': 'Test',
            'profile_image_url': None,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'user_id': str(uuid.uuid4()),
            'assessment_attempts': {
                'academic_writing': 4,
                'general_writing': 4,
                'academic_speaking': 4,
                'general_speaking': 4
            }
        }
        self.dynamodb_tables['ielts-genai-prep-users'].put_item(prod_test_user)
        
        # Initialize GDPR compliance tables
        print("[AWS_MOCK] GDPR compliance tables initialized")
        
        print("[AWS_MOCK] Services initialized for region: us-east-1")
        print("[AWS_MOCK] Test user created: test@ieltsgenaiprep.com / testpassword123")
    
    def get_dynamodb_table(self, table_name: str) -> MockDynamoDBTable:
        """Get DynamoDB table instance"""
        return self.dynamodb_tables.get(table_name)
    
    def get_redis_client(self) -> MockElastiCacheRedis:
        """Get Redis client instance"""
        return self.redis
    
    def get_cloudwatch_client(self) -> MockCloudWatch:
        """Get CloudWatch client instance"""
        return self.cloudwatch
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all mock services"""
        return {
            'dynamodb': {
                'status': 'healthy',
                'tables': len(self.dynamodb_tables),
                'total_items': sum(len(table.items) for table in self.dynamodb_tables.values())
            },
            'redis': {
                'status': 'healthy',
                'cached_items': len(self.redis.cache)
            },
            'cloudwatch': {
                'status': 'healthy',
                'log_entries': len(self.cloudwatch.logs)
            }
        }

# Global instance for use throughout the application
aws_mock = MockAWSServices()