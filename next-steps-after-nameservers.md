# Next Steps After Adding Route 53 Nameservers

## Step 1: Update Namecheap (Do This Now)
Add these nameservers to your Custom DNS fields:
1. ns-22.awsdns-02.com
2. ns-1255.awsdns-28.org
3. ns-1995.awsdns-57.co.uk
4. ns-763.awsdns-31.net

Save changes in Namecheap.

## Step 2: Request SSL Certificate (AWS Console)
1. Go to AWS Certificate Manager
2. Request certificate for:
   - ieltsaiprep.com
   - www.ieltsaiprep.com
3. Use DNS validation
4. Create records in Route 53 automatically

## Step 3: Create API Gateway Custom Domain
1. API Gateway Console → Custom domain names
2. Domain: ieltsaiprep.com
3. Certificate: Select validated certificate
4. API mappings: n0cpf1rmvc → prod stage

## Step 4: Create DNS Records
1. Route 53 → ieltsaiprep.com hosted zone
2. Create A record (alias to API Gateway)
3. Create www A record (alias to API Gateway)

## Timeline
- Nameserver propagation: 15 minutes - 2 hours
- SSL certificate validation: 5-30 minutes
- Complete setup: 1-2 hours total

Your professional ieltsaiprep.com domain will be ready for mobile app submission.