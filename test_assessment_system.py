"""
Comprehensive Unit Tests for Assessment System
Implements all testing recommendations from the technical review.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from flask import Flask
from flask_testing import TestCase

from app import app, db
from models import User, Assessment, UserAssessmentAssignment, UserAssessmentAttempt
from enhanced_nova_assessment import EnhancedNovaAssessment, InputValidator
from assessment_assignment_service import assign_assessments_to_user, get_user_accessible_assessments
from enhanced_browser_speech_routes import process_speaking_response_pipeline

class AssessmentSystemTestCase(TestCase):
    """Base test case for assessment system"""
    
    def create_app(self):
        """Create test application"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        return app
    
    def setUp(self):
        """Set up test database"""
        db.create_all()
        
        # Create test user
        self.test_user = User(
            email='test@example.com',
            assessment_package_status='Academic Writing',
            account_activated=True,
            email_verified=True
        )
        db.session.add(self.test_user)
        
        # Create test assessments
        self.test_assessment = Assessment(
            title='Test Academic Writing Assessment',
            assessment_type='academic_writing',
            status='active'
        )
        db.session.add(self.test_assessment)
        
        db.session.commit()
    
    def tearDown(self):
        """Clean up test database"""
        db.session.remove()
        db.drop_all()

class TestInputValidator(AssessmentSystemTestCase):
    """Test input validation functionality"""
    
    def test_valid_writing_input(self):
        """Test validation of valid writing input"""
        text = "This is a valid essay with more than 150 characters. " * 3
        is_valid, error_msg = InputValidator.validate_writing_input(text)
        
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_short_writing_input(self):
        """Test validation of too short writing input"""
        text = "Too short"
        is_valid, error_msg = InputValidator.validate_writing_input(text)
        
        self.assertFalse(is_valid)
        self.assertIn("at least 150 characters", error_msg)
    
    def test_long_writing_input(self):
        """Test validation of too long writing input"""
        text = "x" * 6000
        is_valid, error_msg = InputValidator.validate_writing_input(text)
        
        self.assertFalse(is_valid)
        self.assertIn("not exceed 5000 characters", error_msg)
    
    def test_malicious_writing_input(self):
        """Test validation against malicious content"""
        text = "<script>alert('xss')</script>" + "x" * 200
        is_valid, error_msg = InputValidator.validate_writing_input(text)
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid content detected", error_msg)
    
    def test_valid_audio_input(self):
        """Test validation of valid audio input"""
        audio_data = b"valid audio data"
        is_valid, error_msg = InputValidator.validate_audio_input(audio_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_empty_audio_input(self):
        """Test validation of empty audio input"""
        audio_data = None
        is_valid, error_msg = InputValidator.validate_audio_input(audio_data)
        
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", error_msg)
    
    def test_large_audio_input(self):
        """Test validation of oversized audio input"""
        audio_data = b"x" * (11 * 1024 * 1024)  # 11MB
        is_valid, error_msg = InputValidator.validate_audio_input(audio_data)
        
        self.assertFalse(is_valid)
        self.assertIn("too large", error_msg)

class TestEnhancedNovaAssessment(AssessmentSystemTestCase):
    """Test enhanced Nova assessment functionality"""
    
    def setUp(self):
        """Set up Nova assessment tests"""
        super().setUp()
        self.patcher = patch('enhanced_nova_assessment.boto3.client')
        self.mock_bedrock = self.patcher.start()
        
        # Mock successful AWS response
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': json.dumps({
                'overall_score': 7.0,
                'task_achievement': 7.0,
                'coherence_cohesion': 6.5,
                'lexical_resource': 7.5,
                'grammatical_range': 7.0,
                'feedback': 'Good essay with clear structure',
                'justification': 'Meets Band 7 criteria'
            })}]
        }).encode()
        
        self.mock_bedrock.return_value.invoke_model.return_value = mock_response
        
        self.nova_assessment = EnhancedNovaAssessment()
    
    def tearDown(self):
        """Clean up Nova assessment tests"""
        super().tearDown()
        self.patcher.stop()
    
    @patch('enhanced_nova_assessment.get_writing_criteria')
    def test_assess_writing_with_rag_success(self, mock_criteria):
        """Test successful writing assessment with RAG"""
        mock_criteria.return_value = "IELTS Writing Criteria"
        
        essay_text = "This is a well-structured essay with clear arguments. " * 10
        result = self.nova_assessment.assess_writing_with_rag(
            essay_text=essay_text,
            task_type='task2',
            specific_question='Discuss environmental protection',
            user_id=self.test_user.id
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['overall_score'], 7.0)
        self.assertIn('TrueScore®', result['assessment_type'])
        self.assertEqual(result['user_id'], self.test_user.id)
    
    def test_assess_writing_invalid_input(self):
        """Test writing assessment with invalid input"""
        essay_text = "Too short"
        result = self.nova_assessment.assess_writing_with_rag(
            essay_text=essay_text,
            task_type='task2',
            user_id=self.test_user.id
        )
        
        self.assertFalse(result['success'])
        self.assertIn('at least 150 characters', result['error'])
    
    @patch('enhanced_nova_assessment.get_speaking_criteria')
    def test_assess_speaking_with_rag_success(self, mock_criteria):
        """Test successful speaking assessment with RAG"""
        mock_criteria.return_value = "IELTS Speaking Criteria"
        
        conversation_history = [
            {'role': 'examiner', 'content': 'Tell me about your hometown'},
            {'role': 'candidate', 'content': 'I come from a beautiful city with rich history'}
        ]
        
        # Mock speaking assessment response
        self.mock_bedrock.return_value.invoke_model.return_value['body'].read.return_value = json.dumps({
            'content': [{'text': json.dumps({
                'overall_score': 6.5,
                'fluency_coherence': 6.0,
                'lexical_resource': 7.0,
                'grammatical_range': 6.5,
                'pronunciation': 7.0,
                'feedback': 'Good speaking performance',
                'justification': 'Meets Band 6.5 criteria'
            })}]
        }).encode()
        
        result = self.nova_assessment.assess_speaking_with_rag(
            conversation_history=conversation_history,
            part_number=1,
            user_id=self.test_user.id
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['overall_score'], 6.5)
        self.assertIn('ClearScore®', result['assessment_type'])
    
    def test_aws_api_retry_logic(self):
        """Test AWS API retry logic with throttling"""
        from botocore.exceptions import ClientError
        
        # Mock throttling error followed by success
        error_response = {'Error': {'Code': 'ThrottlingException'}}
        throttle_error = ClientError(error_response, 'invoke_model')
        
        self.mock_bedrock.return_value.invoke_model.side_effect = [
            throttle_error,  # First call fails
            self.mock_bedrock.return_value.invoke_model.return_value  # Second call succeeds
        ]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            essay_text = "This is a test essay. " * 20
            result = self.nova_assessment.assess_writing_with_rag(
                essay_text=essay_text,
                task_type='task2',
                user_id=self.test_user.id
            )
        
        self.assertTrue(result['success'])
        self.assertEqual(self.mock_bedrock.return_value.invoke_model.call_count, 2)

class TestAssessmentAssignmentService(AssessmentSystemTestCase):
    """Test assessment assignment service functionality"""
    
    def test_assign_assessments_success(self):
        """Test successful assessment assignment"""
        assigned_ids, success = assign_assessments_to_user(
            user_id=self.test_user.id,
            assessment_type='academic',
            num_assessments=1
        )
        
        self.assertTrue(success)
        self.assertEqual(len(assigned_ids), 1)
        self.assertIn(self.test_assessment.id, assigned_ids)
    
    def test_assign_assessments_invalid_count(self):
        """Test assignment with invalid assessment count"""
        with self.assertRaises(ValueError):
            assign_assessments_to_user(
                user_id=self.test_user.id,
                assessment_type='academic',
                num_assessments=5  # Invalid count
            )
    
    def test_assign_assessments_invalid_type(self):
        """Test assignment with invalid assessment type"""
        with self.assertRaises(ValueError):
            assign_assessments_to_user(
                user_id=self.test_user.id,
                assessment_type='invalid',
                num_assessments=1
            )
    
    def test_prevent_duplicate_assignments(self):
        """Test prevention of duplicate assessment assignments"""
        # First assignment
        assigned_ids_1, success_1 = assign_assessments_to_user(
            user_id=self.test_user.id,
            assessment_type='academic',
            num_assessments=1
        )
        
        self.assertTrue(success_1)
        
        # Create another assessment for second assignment
        assessment_2 = Assessment(
            title='Test Academic Writing Assessment 2',
            assessment_type='academic_writing',
            status='active'
        )
        db.session.add(assessment_2)
        db.session.commit()
        
        # Second assignment should not include previously assigned assessment
        assigned_ids_2, success_2 = assign_assessments_to_user(
            user_id=self.test_user.id,
            assessment_type='academic',
            num_assessments=1
        )
        
        self.assertTrue(success_2)
        self.assertNotEqual(assigned_ids_1, assigned_ids_2)
    
    def test_insufficient_unique_assessments(self):
        """Test assignment when insufficient unique assessments available"""
        # Assign the only available assessment
        assign_assessments_to_user(
            user_id=self.test_user.id,
            assessment_type='academic',
            num_assessments=1
        )
        
        # Try to assign more assessments than available
        assigned_ids, success = assign_assessments_to_user(
            user_id=self.test_user.id,
            assessment_type='academic',
            num_assessments=2
        )
        
        self.assertFalse(success)
        self.assertEqual(len(assigned_ids), 0)
    
    def test_get_user_accessible_assessments(self):
        """Test retrieval of user accessible assessments"""
        # Assign assessments first
        assigned_ids, success = assign_assessments_to_user(
            user_id=self.test_user.id,
            assessment_type='academic',
            num_assessments=1
        )
        self.assertTrue(success)
        
        # Get accessible assessments
        accessible = get_user_accessible_assessments(
            user_id=self.test_user.id,
            assessment_type='academic_writing'
        )
        
        self.assertEqual(len(accessible), 1)
        self.assertEqual(accessible[0].id, self.test_assessment.id)

class TestBrowserSpeechRoutes(AssessmentSystemTestCase):
    """Test enhanced browser speech routes"""
    
    def setUp(self):
        """Set up browser speech tests"""
        super().setUp()
        self.client = self.app.test_client()
        
        # Mock login
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user.id)
            sess['speech_consent'] = True
    
    @patch('enhanced_browser_speech_routes.nova_assessment')
    def test_process_speaking_response_pipeline(self, mock_assessment):
        """Test complete speaking response processing pipeline"""
        # Mock Nova assessment responses
        mock_assessment.create_enhanced_speaking_session.return_value = {
            'success': True,
            'examiner_response': 'Please tell me about your hometown'
        }
        
        mock_assessment.assess_speaking_with_rag.return_value = {
            'success': True,
            'overall_score': 7.0,
            'fluency_coherence': 7.0,
            'lexical_resource': 6.5,
            'grammatical_range': 7.5,
            'pronunciation': 7.0,
            'detailed_feedback': 'Excellent speaking performance',
            'band_justification': 'Strong Band 7 performance'
        }
        
        result = process_speaking_response_pipeline(
            transcript="I come from a beautiful coastal city with rich cultural heritage",
            question_id="hometown_question",
            user_id=self.test_user.id,
            part_number=1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['overall_score'], 7.0)
        
        # Verify both services were called
        mock_assessment.create_enhanced_speaking_session.assert_called_once()
        mock_assessment.assess_speaking_with_rag.assert_called_once()
    
    def test_pipeline_short_transcript(self):
        """Test pipeline with too short transcript"""
        result = process_speaking_response_pipeline(
            transcript="Short",
            question_id="test_question",
            user_id=self.test_user.id
        )
        
        self.assertFalse(result['success'])
        self.assertIn('too short', result['error'])

class TestSecurityValidation(AssessmentSystemTestCase):
    """Test security validation features"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection pattern detection"""
        from security_manager import SecurityManager
        
        security_mgr = SecurityManager()
        
        # Test various SQL injection patterns
        malicious_queries = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "UNION SELECT * FROM passwords",
            "admin'--",
            "1'; DELETE FROM assessments; --"
        ]
        
        for query in malicious_queries:
            is_malicious = security_mgr.check_sql_injection(query)
            self.assertTrue(is_malicious, f"Failed to detect SQL injection in: {query}")
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        from security_manager import SecurityManager
        
        security_mgr = SecurityManager()
        
        # Test control character removal
        dirty_input = "Hello\x00\x01World\x7f"
        clean_input = security_mgr.sanitize_input(dirty_input)
        self.assertEqual(clean_input, "HelloWorld")
        
        # Test length limiting
        long_input = "x" * 20000
        limited_input = security_mgr.sanitize_input(long_input)
        self.assertEqual(len(limited_input), 10000)

class TestPerformanceOptimizations(AssessmentSystemTestCase):
    """Test performance optimization features"""
    
    @patch('assessment_assignment_service.logger')
    def test_bulk_assignment_logging(self, mock_logger):
        """Test bulk assignment with proper logging"""
        # Create additional assessments for bulk testing
        for i in range(3):
            assessment = Assessment(
                title=f'Test Assessment {i}',
                assessment_type='academic_writing',
                status='active'
            )
            db.session.add(assessment)
        db.session.commit()
        
        # Create additional test users
        users = []
        for i in range(2):
            user = User(
                email=f'test{i}@example.com',
                assessment_package_status='Academic Writing',
                account_activated=True,
                email_verified=True
            )
            db.session.add(user)
            users.append(user)
        db.session.commit()
        
        # Perform bulk assignment
        assignment_requests = [
            {'user_id': user.id, 'assessment_type': 'academic', 'num_assessments': 1}
            for user in users
        ]
        
        from assessment_assignment_service import bulk_assign_assessments
        results = bulk_assign_assessments(assignment_requests)
        
        # Verify logging was called
        self.assertTrue(mock_logger.info.called)
        
        # Verify results
        self.assertEqual(len(results['successful']), 2)
        self.assertEqual(len(results['failed']), 0)

def run_all_tests():
    """Run all assessment system tests"""
    import unittest
    
    test_classes = [
        TestInputValidator,
        TestEnhancedNovaAssessment,
        TestAssessmentAssignmentService,
        TestBrowserSpeechRoutes,
        TestSecurityValidation,
        TestPerformanceOptimizations
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)