# Manual Route 53 Migration Steps for ieltsaiprep.com

## Step-by-Step AWS Console Migration

### Step 1: Create Route 53 Hosted Zone
1. Go to [Route 53 Console](https://console.aws.amazon.com/route53/v2/hostedzones)
2. Click "Create hosted zone"
3. Domain name: `ieltsaiprep.com`
4. Type: Public hosted zone
5. Click "Create hosted zone"
6. **Save the 4 nameservers** shown (you'll need these for Namecheap)

### Step 2: Request SSL Certificate
1. Go to [Certificate Manager Console](https://console.aws.amazon.com/acm/home?region=us-east-1)
2. Click "Request a certificate"
3. Request a public certificate
4. Domain names:
   - `ieltsaiprep.com`
   - `www.ieltsaiprep.com`
5. Validation method: **DNS validation**
6. Click "Request"

### Step 3: Add DNS Validation Records
1. In Certificate Manager, click on your certificate
2. Copy the CNAME validation records
3. Go back to Route 53 hosted zone
4. Click "Create record"
5. Add each CNAME validation record exactly as shown
6. Wait for certificate status to change to "Issued" (5-10 minutes)

### Step 4: Create API Gateway Custom Domain
1. Go to [API Gateway Console](https://console.aws.amazon.com/apigateway/main/publish/domain-names?region=us-east-1)
2. Click "Create domain name"
3. Domain name: `ieltsaiprep.com`
4. Certificate: Select your issued certificate
5. Endpoint type: Regional
6. Click "Create domain name"

### Step 5: Create API Mapping
1. In the custom domain page, click "API mappings"
2. Click "Configure API mappings"
3. API: Select your Lambda API (should contain "n0cpf1rmvc")
4. Stage: `prod`
5. Path: (leave empty)
6. Click "Save"

### Step 6: Update Route 53 A Record
1. Copy the "Target domain name" from API Gateway custom domain
2. Go back to Route 53 hosted zone
3. Create new record:
   - Record name: (leave empty for apex domain)
   - Record type: A
   - Alias: Yes
   - Route traffic to: Alias to API Gateway API
   - Region: US East (N. Virginia)
   - API Gateway domain name: Paste the target domain
4. Click "Create records"

### Step 7: Create WWW Subdomain
1. Create another record:
   - Record name: `www`
   - Record type: A
   - Alias: Yes
   - Route traffic to: Alias to API Gateway API
   - Use same target domain as step 6
2. Click "Create records"

### Step 8: Update Nameservers at Namecheap
1. Login to Namecheap
2. Go to Domain List → ieltsaiprep.com → Manage
3. Change nameservers from "Namecheap BasicDNS" to "Custom DNS"
4. Enter the 4 Route 53 nameservers from Step 1
5. Save changes

### Step 9: Wait for DNS Propagation
- Timeline: 24-48 hours for global propagation
- Test with: `dig ieltsaiprep.com` and `curl -I https://ieltsaiprep.com`

## Expected Results After Migration
- https://ieltsaiprep.com → Your IELTS app
- https://www.ieltsaiprep.com → Your IELTS app
- SSL certificate automatically validated and renewed
- Professional domain for App Store submission

This manual approach avoids CLI permission issues while achieving the same AWS-native domain management.