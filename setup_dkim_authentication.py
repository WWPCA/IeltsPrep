"""
DKIM Authentication Setup for AWS SES
This script helps configure DKIM authentication for improved email deliverability.
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DKIMSetup:
    def __init__(self):
        """Initialize AWS SES client for DKIM setup."""
        try:
            self.region = os.environ.get('AWS_REGION', 'us-east-1')
            self.ses_client = boto3.client(
                'ses',
                region_name=self.region,
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"AWS SES client initialized for DKIM setup in region: {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize AWS SES client: {e}")
            raise

    def check_domain_verification(self, domain):
        """Check if domain is verified in AWS SES."""
        try:
            response = self.ses_client.list_verified_email_addresses()
            verified_emails = response.get('VerifiedEmailAddresses', [])
            
            # Check for domain verification
            response = self.ses_client.get_identity_verification_attributes(
                Identities=[domain]
            )
            
            verification_attrs = response.get('VerificationAttributes', {})
            domain_status = verification_attrs.get(domain, {})
            
            return {
                'domain': domain,
                'verification_status': domain_status.get('VerificationStatus', 'Not Found'),
                'verification_token': domain_status.get('VerificationToken', 'N/A'),
                'verified_emails': verified_emails
            }
            
        except ClientError as e:
            logger.error(f"Error checking domain verification: {e}")
            return None

    def verify_domain(self, domain):
        """Verify a domain with AWS SES."""
        try:
            response = self.ses_client.verify_domain_identity(Domain=domain)
            verification_token = response.get('VerificationToken')
            
            logger.info(f"Domain verification initiated for {domain}")
            logger.info(f"Verification token: {verification_token}")
            
            return {
                'success': True,
                'domain': domain,
                'verification_token': verification_token,
                'next_steps': f"Add TXT record '_amazonses.{domain}' with value '{verification_token}' to your DNS"
            }
            
        except ClientError as e:
            logger.error(f"Error verifying domain: {e}")
            return {'success': False, 'error': str(e)}

    def check_dkim_status(self, domain):
        """Check DKIM status for a domain."""
        try:
            response = self.ses_client.get_identity_dkim_attributes(
                Identities=[domain]
            )
            
            dkim_attrs = response.get('DkimAttributes', {})
            domain_dkim = dkim_attrs.get(domain, {})
            
            return {
                'domain': domain,
                'dkim_enabled': domain_dkim.get('DkimEnabled', False),
                'dkim_verification_status': domain_dkim.get('DkimVerificationStatus', 'Not Found'),
                'dkim_tokens': domain_dkim.get('DkimTokens', [])
            }
            
        except ClientError as e:
            logger.error(f"Error checking DKIM status: {e}")
            return None

    def enable_dkim(self, domain):
        """Enable DKIM for a domain."""
        try:
            # First, enable DKIM
            response = self.ses_client.put_identity_dkim_attributes(
                Identity=domain,
                DkimEnabled=True
            )
            
            # Get DKIM tokens
            dkim_response = self.ses_client.get_identity_dkim_attributes(
                Identities=[domain]
            )
            
            dkim_attrs = dkim_response.get('DkimAttributes', {})
            domain_dkim = dkim_attrs.get(domain, {})
            dkim_tokens = domain_dkim.get('DkimTokens', [])
            
            logger.info(f"DKIM enabled for {domain}")
            
            dns_records = []
            for token in dkim_tokens:
                dns_records.append({
                    'name': f"{token}._domainkey.{domain}",
                    'type': 'CNAME',
                    'value': f"{token}.dkim.amazonses.com"
                })
            
            return {
                'success': True,
                'domain': domain,
                'dkim_enabled': True,
                'dkim_tokens': dkim_tokens,
                'dns_records': dns_records,
                'next_steps': 'Add the CNAME records to your domain DNS settings'
            }
            
        except ClientError as e:
            logger.error(f"Error enabling DKIM: {e}")
            return {'success': False, 'error': str(e)}

    def get_comprehensive_status(self, domain):
        """Get comprehensive status of domain and DKIM setup."""
        try:
            # Check domain verification
            domain_status = self.check_domain_verification(domain)
            
            # Check DKIM status
            dkim_status = self.check_dkim_status(domain)
            
            # Check sending quota and statistics
            quota_response = self.ses_client.get_send_quota()
            stats_response = self.ses_client.get_send_statistics()
            
            return {
                'domain_verification': domain_status,
                'dkim_status': dkim_status,
                'sending_quota': {
                    'max_24_hour_send': quota_response.get('Max24HourSend', 0),
                    'sent_last_24_hours': quota_response.get('SentLast24Hours', 0),
                    'max_send_rate': quota_response.get('MaxSendRate', 0)
                },
                'recent_sending_stats': stats_response.get('SendDataPoints', [])[-5:] if stats_response.get('SendDataPoints') else []
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {'error': str(e)}

def main():
    """Main function to setup DKIM authentication."""
    domain = "ieltsaiprep.com"
    
    try:
        dkim_setup = DKIMSetup()
        
        print(f"\n=== DKIM Setup for {domain} ===\n")
        
        # Get current status
        print("1. Checking current status...")
        status = dkim_setup.get_comprehensive_status(domain)
        
        if 'error' in status:
            print(f"Error getting status: {status['error']}")
            return
        
        # Print domain verification status
        domain_verification = status.get('domain_verification', {})
        print(f"Domain Verification Status: {domain_verification.get('verification_status', 'Unknown')}")
        
        # Print DKIM status
        dkim_status = status.get('dkim_status', {})
        print(f"DKIM Enabled: {dkim_status.get('dkim_enabled', False)}")
        print(f"DKIM Verification Status: {dkim_status.get('dkim_verification_status', 'Unknown')}")
        
        # If domain not verified, verify it first
        if domain_verification.get('verification_status') != 'Success':
            print(f"\n2. Domain {domain} is not verified. Initiating verification...")
            verify_result = dkim_setup.verify_domain(domain)
            if verify_result.get('success'):
                print(f"Domain verification initiated!")
                print(f"Add this TXT record to your DNS:")
                print(f"Name: _amazonses.{domain}")
                print(f"Value: {verify_result.get('verification_token')}")
            else:
                print(f"Failed to initiate domain verification: {verify_result.get('error')}")
                return
        
        # Enable DKIM if not already enabled
        if not dkim_status.get('dkim_enabled'):
            print(f"\n3. Enabling DKIM for {domain}...")
            dkim_result = dkim_setup.enable_dkim(domain)
            
            if dkim_result.get('success'):
                print("DKIM enabled successfully!")
                print("\nAdd these CNAME records to your DNS:")
                for record in dkim_result.get('dns_records', []):
                    print(f"Name: {record['name']}")
                    print(f"Type: {record['type']}")
                    print(f"Value: {record['value']}")
                    print("---")
            else:
                print(f"Failed to enable DKIM: {dkim_result.get('error')}")
        else:
            print(f"\n3. DKIM is already enabled for {domain}")
            if dkim_status.get('dkim_tokens'):
                print("CNAME records needed:")
                for token in dkim_status.get('dkim_tokens', []):
                    print(f"Name: {token}._domainkey.{domain}")
                    print(f"Type: CNAME")
                    print(f"Value: {token}.dkim.amazonses.com")
                    print("---")
        
        # Print sending quota info
        quota = status.get('sending_quota', {})
        print(f"\n4. Current Sending Limits:")
        print(f"Daily limit: {quota.get('max_24_hour_send', 0)}")
        print(f"Sent today: {quota.get('sent_last_24_hours', 0)}")
        print(f"Sending rate: {quota.get('max_send_rate', 0)} emails/second")
        
        print(f"\n=== Next Steps ===")
        print("1. Add the DNS records shown above to your domain registrar")
        print("2. Wait for DNS propagation (up to 72 hours)")
        print("3. AWS will automatically verify the records")
        print("4. Your email deliverability will improve significantly")
        
    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    main()