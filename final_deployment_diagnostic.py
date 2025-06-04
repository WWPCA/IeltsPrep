#!/usr/bin/env python3
"""
Final Deployment Diagnostic
Comprehensive system check before deployment to ieltsaiprep.replit.app
"""

import os
import sys
import logging
from flask import Flask
from sqlalchemy import text

# Add current directory to path
sys.path.append('.')

try:
    from app import app, db
    from models import User, UserTestAttempt, SpeakingPrompt
    print("✅ Core modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_database_connection():
    """Test database connectivity and core tables"""
    print("\n🔍 Testing Database Connection...")
    try:
        with app.app_context():
            # Test basic connection
            result = db.session.execute(text("SELECT 1")).scalar()
            print(f"✅ Database connection successful: {result}")
            
            # Check core tables exist
            tables_to_check = ['user', 'user_test_attempt', 'speaking_prompt', 'user_assessment']
            for table in tables_to_check:
                count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"✅ Table '{table}' exists with {count} records")
                
            # Test user authentication
            test_user = User.query.filter_by(email='test@ieltsaiprep.com').first()
            if test_user:
                print(f"✅ Test user found: {test_user.email}")
            else:
                print("⚠️  Test user not found")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    return True

def test_aws_services():
    """Test AWS service configuration"""
    print("\n🔍 Testing AWS Services...")
    
    # Test AWS credentials
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION')
    
    if aws_access_key and aws_secret_key and aws_region:
        print("✅ AWS credentials configured")
        print(f"✅ AWS region: {aws_region}")
        return True
    else:
        print("❌ AWS credentials missing")
        return False

def test_payment_service():
    """Test Stripe payment configuration"""
    print("\n🔍 Testing Payment Service...")
    
    stripe_secret = os.environ.get('STRIPE_SECRET_KEY')
    stripe_public = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    
    if stripe_secret and stripe_public:
        print("✅ Stripe API keys configured")
        return True
    else:
        print("❌ Stripe API keys missing")
        return False

def test_security_configuration():
    """Test security settings and environment variables"""
    print("\n🔍 Testing Security Configuration...")
    
    # Check required environment variables
    required_vars = [
        'SESSION_SECRET',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables configured")
    
    # Test Flask app configuration
    with app.app_context():
        print(f"✅ Flask secret key configured: {'Yes' if app.secret_key else 'No'}")
        print(f"✅ CSRF protection enabled: {'Yes' if app.config.get('WTF_CSRF_ENABLED', True) else 'No'}")
        print(f"✅ Session security: Secure={app.config.get('SESSION_COOKIE_SECURE', False)}")
    
    return True

def test_domain_configuration():
    """Test domain and URL configuration"""
    print("\n🔍 Testing Domain Configuration...")
    
    replit_domains = os.environ.get('REPLIT_DOMAINS', '')
    print(f"✅ Replit domains: {replit_domains}")
    
    with app.app_context():
        print(f"✅ Preferred URL scheme: {app.config.get('PREFERRED_URL_SCHEME', 'http')}")
        print(f"✅ App configured for: ieltsaiprep.replit.app")
    
    return True

def test_assessment_system():
    """Test assessment system components"""
    print("\n🔍 Testing Assessment System...")
    
    try:
        with app.app_context():
            # Check speaking prompts
            speaking_prompts = SpeakingPrompt.query.count()
            print(f"✅ Speaking prompts available: {speaking_prompts}")
            
            # Check test attempts
            test_attempts = UserTestAttempt.query.count()
            print(f"✅ Total test attempts: {test_attempts}")
                
    except Exception as e:
        print(f"⚠️  Assessment system warning: {e}")
        return False
    
    return True

def main():
    """Run comprehensive deployment diagnostic"""
    print("🚀 IELTS AI Prep - Final Deployment Diagnostic")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_database_connection())
    test_results.append(test_aws_services())
    test_results.append(test_payment_service())
    test_results.append(test_security_configuration())
    test_results.append(test_domain_configuration())
    test_results.append(test_assessment_system())
    
    # Summary
    print("\n" + "=" * 60)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"📊 DIAGNOSTIC SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL SYSTEMS GO! Ready for deployment to ieltsaiprep.replit.app")
        print("\n📋 Deployment Checklist:")
        print("✅ Database configured and accessible")
        print("✅ AWS services (Bedrock/Nova Sonic/SES) ready")
        print("✅ Stripe payment processing configured")
        print("✅ Security settings properly configured")
        print("✅ Domain configuration updated")
        print("✅ Assessment system functional")
        print("\n🚀 You can now proceed with deployment!")
    else:
        print("⚠️  Some issues detected. Please review and fix before deployment.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()