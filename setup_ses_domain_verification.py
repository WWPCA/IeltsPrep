"""
Amazon SES Domain Verification Setup
Sets up domain verification for ieltsaiprep.com to enable email services
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class SESVerificationManager:
    """Manages Amazon SES domain verification process"""
    
    def __init__(self):
        """Initialize SES client"""
        self.ses_client = boto3.client(
            'ses',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        self.domain = 'ieltsaiprep.com'
    
    def initiate_domain_verification(self):
        """Start domain verification process"""
        try:
            # Verify domain identity
            response = self.ses_client.verify_domain_identity(Domain=self.domain)
            verification_token = response['VerificationToken']
            
            logger.info(f"Domain verification initiated for {self.domain}")
            logger.info(f"Verification token: {verification_token}")
            
            return {
                'success': True,
                'domain': self.domain,
                'verification_token': verification_token,
                'txt_record': f"amazonses:{verification_token}",
                'instructions': self._get_verification_instructions(verification_token)
            }
            
        except ClientError as e:
            logger.error(f"Failed to initiate domain verification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_verification_status(self):
        """Check current verification status"""
        try:
            response = self.ses_client.get_identity_verification_attributes(
                Identities=[self.domain]
            )
            
            attributes = response.get('VerificationAttributes', {})
            domain_attributes = attributes.get(self.domain, {})
            
            verification_status = domain_attributes.get('VerificationStatus', 'NotStarted')
            verification_token = domain_attributes.get('VerificationToken', '')
            
            return {
                'domain': self.domain,
                'status': verification_status,
                'token': verification_token,
                'verified': verification_status == 'Success'
            }
            
        except ClientError as e:
            logger.error(f"Failed to check verification status: {e}")
            return {
                'domain': self.domain,
                'status': 'Error',
                'error': str(e)
            }
    
    def setup_dkim_authentication(self):
        """Set up DKIM authentication for the domain"""
        try:
            # Get DKIM tokens for the domain
            response = self.ses_client.verify_domain_dkim(Domain=self.domain)
            dkim_tokens = response['DkimTokens']
            
            # Enable DKIM for the domain
            self.ses_client.put_identity_dkim_attributes(
                Identity=self.domain,
                DkimEnabled=True
            )
            
            logger.info(f"DKIM enabled for {self.domain}")
            
            return {
                'success': True,
                'domain': self.domain,
                'dkim_tokens': dkim_tokens,
                'dkim_records': [f"{token}._domainkey.{self.domain}" for token in dkim_tokens]
            }
            
        except ClientError as e:
            logger.error(f"Failed to setup DKIM: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_verification_instructions(self, verification_token):
        """Get DNS configuration instructions"""
        return {
            'txt_record': {
                'name': f'_amazonses.{self.domain}',
                'value': verification_token,
                'type': 'TXT'
            },
            'steps': [
                f"1. Log into your DNS provider (where {self.domain} is registered)",
                f"2. Add a new TXT record:",
                f"   - Name: _amazonses.{self.domain}",
                f"   - Value: {verification_token}",
                f"   - Type: TXT",
                "3. Save the DNS record",
                "4. Wait for DNS propagation (can take up to 72 hours)",
                "5. Amazon will automatically verify the domain once the record is detected"
            ]
        }

def setup_domain_verification():
    """Main function to set up domain verification"""
    manager = SESVerificationManager()
    
    # Check current status
    print("Checking current verification status...")
    status = manager.check_verification_status()
    print(f"Domain: {status['domain']}")
    print(f"Status: {status['status']}")
    
    if status['verified']:
        print("✅ Domain is already verified!")
        return status
    
    # Initiate verification if not already verified
    print("\nInitiating domain verification...")
    result = manager.initiate_domain_verification()
    
    if result['success']:
        print("✅ Domain verification initiated successfully!")
        print(f"\nDNS Configuration Required:")
        print(f"TXT Record Name: _amazonses.{result['domain']}")
        print(f"TXT Record Value: {result['verification_token']}")
        print(f"\nInstructions:")
        for step in result['instructions']['steps']:
            print(step)
    else:
        print(f"❌ Failed to initiate verification: {result['error']}")
    
    # Setup DKIM
    print("\nSetting up DKIM authentication...")
    dkim_result = manager.setup_dkim_authentication()
    
    if dkim_result['success']:
        print("✅ DKIM authentication enabled!")
        print("DKIM CNAME Records needed:")
        for i, token in enumerate(dkim_result['dkim_tokens'], 1):
            print(f"  {i}. Name: {token}._domainkey.{result['domain']}")
            print(f"     Value: {token}.dkim.amazonses.com")
    else:
        print(f"❌ DKIM setup failed: {dkim_result['error']}")
    
    return result

if __name__ == "__main__":
    setup_domain_verification()