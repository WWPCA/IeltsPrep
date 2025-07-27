# AWS Email Migration Guide for ieltsaiprep.com

## Overview
This guide helps you migrate email hosting from Namecheap to AWS for complete unified management with your domain and web hosting.

## Current Status
- ✅ Domain: Transferred to AWS Route 53
- ✅ Web hosting: AWS Lambda + CloudFront
- ✅ Transactional emails: AWS SES (already configured)
- ❓ Email hosting: Still with Namecheap (needs migration)

## Migration Options

### Option 1: AWS SES + Simple Email Forwarding (Recommended)
**Best for:** Basic email needs, cost-effective
**Cost:** ~$1-2/month for light usage

#### Benefits:
- Integrates with existing SES setup
- Very affordable
- Perfect for business contact emails
- Already configured for app notifications

#### Setup Steps:
1. **Verify domain in SES console**
2. **Configure MX records in Route 53**
3. **Set up email forwarding rules**
4. **Test email delivery**

### Option 2: AWS WorkMail (Full Business Email)
**Best for:** Multiple email accounts, advanced features
**Cost:** $4/user/month

#### Benefits:
- Full business email solution
- Calendar integration
- Mobile app support
- Web-based interface

## Step-by-Step Migration Process

### Phase 1: AWS SES Domain Verification
```bash
# 1. Go to AWS SES Console
# 2. Navigate to "Verified identities"
# 3. Click "Create identity"
# 4. Select "Domain"
# 5. Enter: ieltsaiprep.com
# 6. Choose "Easy DKIM" (recommended)
```

### Phase 2: DNS Configuration in Route 53
Add these records to your Route 53 hosted zone:

```dns
# MX Record (for receiving emails)
Type: MX
Name: ieltsaiprep.com
Value: 10 mail.ieltsaiprep.com

# TXT Record (for SPF)
Type: TXT
Name: ieltsaiprep.com
Value: "v=spf1 include:amazonses.com ~all"

# CNAME Records (for DKIM - AWS will provide these)
Type: CNAME
Name: [AWS-provided-selector1]._domainkey.ieltsaiprep.com
Value: [AWS-provided-value1]

Type: CNAME
Name: [AWS-provided-selector2]._domainkey.ieltsaiprep.com
Value: [AWS-provided-value2]
```

### Phase 3: Email Addresses Setup

#### Essential Business Emails:
- `admin@ieltsaiprep.com` - Main admin contact
- `support@ieltsaiprep.com` - Customer support
- `noreply@ieltsaiprep.com` - Already configured for app
- `welcome@ieltsaiprep.com` - Already configured for app

#### SES Email Forwarding Configuration:
```python
# Example Lambda function for email forwarding
import boto3
import email
from email.mime.text import MIMEText

def lambda_handler(event, context):
    # Forward emails to your personal email
    ses = boto3.client('ses')
    
    # Parse incoming email
    mail = email.message_from_string(event['Records'][0]['ses']['mail']['source'])
    
    # Forward to your personal email
    response = ses.send_email(
        Source='admin@ieltsaiprep.com',
        Destination={'ToAddresses': ['your-personal-email@gmail.com']},
        Message={
            'Subject': {'Data': f"Forwarded: {mail['Subject']}"},
            'Body': {'Text': {'Data': mail.get_payload()}}
        }
    )
```

### Phase 4: Update App Configuration
Your app already uses these email addresses:
```python
# In app.py - already configured
WELCOME_EMAIL = "welcome@ieltsaiprep.com"
NO_REPLY_EMAIL = "noreply@ieltsaiprep.com"
```

### Phase 5: Testing Checklist
- [ ] Send test email to `admin@ieltsaiprep.com`
- [ ] Verify email forwarding works
- [ ] Test app registration emails still work
- [ ] Confirm DKIM signing is active
- [ ] Check spam folder compliance

### Phase 6: Namecheap Cancellation
1. **Backup any existing emails**
2. **Cancel Namecheap email service**
3. **Remove old MX records** (if any remain)
4. **Update any email signatures/business cards**

## Cost Comparison

### Current Namecheap Email
- Cost: ~$10-20/year

### AWS SES Option
- Cost: ~$1-2/month ($12-24/year)
- 62,000 emails per month free (sent from EC2)
- $0.10 per 1,000 additional emails

### AWS WorkMail Option
- Cost: $4/user/month ($48/year per user)
- Full business email features

## Security Benefits

### Enhanced Security with AWS:
- **DKIM signing** - Email authentication
- **SPF records** - Sender verification
- **DMARC compliance** - Email spoofing protection
- **Encryption in transit** - All emails encrypted
- **Integration with CloudTrail** - Full email audit logs

## Migration Timeline

### Week 1 (This Week):
- [ ] Set up SES domain verification
- [ ] Configure DNS records
- [ ] Test email delivery

### Week 2:
- [ ] Monitor email delivery
- [ ] Set up forwarding rules
- [ ] Update business communications

### Week 3:
- [ ] Cancel Namecheap email
- [ ] Final verification tests

## Support Contacts

### AWS Support Resources:
- SES Documentation: https://docs.aws.amazon.com/ses/
- Route 53 Email Setup: https://docs.aws.amazon.com/route53/
- WorkMail Setup: https://docs.aws.amazon.com/workmail/

## Next Steps for Monday

1. **Review this guide**
2. **Choose between SES or WorkMail**
3. **Access AWS SES Console**
4. **Begin domain verification process**
5. **Configure DNS records in Route 53**

## Benefits Summary

✅ **Unified AWS ecosystem** - Everything in one place
✅ **Cost savings** - More affordable than Namecheap
✅ **Better integration** - Works with existing SES setup
✅ **Enhanced security** - DKIM, SPF, DMARC compliance
✅ **Scalability** - Grows with your business
✅ **Professional setup** - Matches your serverless architecture

This migration will complete your full AWS hosting setup and provide better email management for your IELTS platform.