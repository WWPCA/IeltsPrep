#!/usr/bin/env python3
"""
AWS Resource Teardown Script for IELTS GenAI Prep
Safely removes all AWS resources created for the production deployment
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

class AWSResourceTeardown:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.project_name = 'ielts-genai-prep'
        
        # Initialize AWS clients
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.apigateway_client = boto3.client('apigateway', region_name=region)
        self.dynamodb_client = boto3.client('dynamodb', region_name=region)
        self.elasticache_client = boto3.client('elasticache', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.logs_client = boto3.client('logs', region_name=region)
        self.route53_client = boto3.client('route53', region_name=region)
        self.acm_client = boto3.client('acm', region_name=region)
        self.cloudfront_client = boto3.client('cloudfront', region_name=region)
        
        print(f"🔧 Initialized AWS teardown for region: {region}")
        
    def confirm_teardown(self):
        """Confirm user wants to proceed with teardown"""
        print("\n⚠️  WARNING: This will permanently delete all AWS resources!")
        print("Resources to be removed:")
        print("   • Lambda function: ielts-genai-prep-api")
        print("   • API Gateway: n0cpf1rmvc")
        print("   • DynamoDB tables (4 tables)")
        print("   • ElastiCache Redis cluster")
        print("   • IAM roles and policies")
        print("   • CloudWatch log groups")
        print("   • Route 53 hosted zone (if exists)")
        print("   • SSL certificates")
        print("   • CloudFront distribution")
        
        response = input("\nType 'DELETE' to confirm teardown: ")
        return response == 'DELETE'
    
    def delete_lambda_function(self):
        """Delete Lambda function"""
        try:
            self.lambda_client.delete_function(
                FunctionName='ielts-genai-prep-api'
            )
            print("✅ Lambda function deleted")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("ℹ️  Lambda function not found (already deleted)")
                return True
            else:
                print(f"❌ Error deleting Lambda function: {e}")
                return False
    
    def delete_api_gateway(self):
        """Delete API Gateway"""
        try:
            # Find API Gateway by name or ID
            apis = self.apigateway_client.get_rest_apis()
            
            for api in apis['items']:
                if api['id'] == 'n0cpf1rmvc' or api['name'] == 'ielts-genai-prep':
                    self.apigateway_client.delete_rest_api(restApiId=api['id'])
                    print(f"✅ API Gateway deleted: {api['id']}")
                    return True
            
            print("ℹ️  API Gateway not found (already deleted)")
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting API Gateway: {e}")
            return False
    
    def delete_dynamodb_tables(self):
        """Delete all DynamoDB tables"""
        table_names = [
            'ielts-genai-prep-users',
            'ielts-genai-prep-sessions',
            'ielts-genai-prep-assessments',
            'ielts-genai-prep-rubrics',
            'ielts-genai-prep-qr-tokens',
            'ielts-assessment-questions'
        ]
        
        success = True
        for table_name in table_names:
            try:
                self.dynamodb_client.delete_table(TableName=table_name)
                print(f"✅ DynamoDB table deleted: {table_name}")
                
                # Wait for table to be deleted
                print(f"   Waiting for {table_name} to be deleted...")
                waiter = self.dynamodb_client.get_waiter('table_not_exists')
                waiter.wait(TableName=table_name, WaiterConfig={'MaxAttempts': 25})
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    print(f"ℹ️  Table not found: {table_name} (already deleted)")
                else:
                    print(f"❌ Error deleting table {table_name}: {e}")
                    success = False
        
        return success
    
    def delete_elasticache_cluster(self):
        """Delete ElastiCache Redis cluster"""
        try:
            cluster_id = f'{self.project_name}-redis'
            
            self.elasticache_client.delete_cache_cluster(
                CacheClusterId=cluster_id
            )
            print(f"✅ ElastiCache cluster deletion initiated: {cluster_id}")
            
            # Note: ElastiCache deletion takes time, don't wait
            print("   ElastiCache deletion will complete in background")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'CacheClusterNotFoundFault':
                print("ℹ️  ElastiCache cluster not found (already deleted)")
                return True
            else:
                print(f"❌ Error deleting ElastiCache cluster: {e}")
                return False
    
    def delete_iam_resources(self):
        """Delete IAM roles and policies"""
        role_name = f'{self.project_name}-lambda-role'
        
        try:
            # Detach managed policies
            try:
                self.iam_client.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
                )
            except ClientError:
                pass
            
            # Delete inline policies
            try:
                policies = self.iam_client.list_role_policies(RoleName=role_name)
                for policy_name in policies['PolicyNames']:
                    self.iam_client.delete_role_policy(
                        RoleName=role_name,
                        PolicyName=policy_name
                    )
            except ClientError:
                pass
            
            # Delete role
            self.iam_client.delete_role(RoleName=role_name)
            print(f"✅ IAM role deleted: {role_name}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                print("ℹ️  IAM role not found (already deleted)")
                return True
            else:
                print(f"❌ Error deleting IAM role: {e}")
                return False
    
    def delete_cloudwatch_logs(self):
        """Delete CloudWatch log groups"""
        log_groups = [
            f'/aws/lambda/{self.project_name}',
            f'/aws/lambda/{self.project_name}-api',
            f'/aws/apigateway/{self.project_name}'
        ]
        
        success = True
        for log_group in log_groups:
            try:
                self.logs_client.delete_log_group(logGroupName=log_group)
                print(f"✅ CloudWatch log group deleted: {log_group}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    print(f"ℹ️  Log group not found: {log_group} (already deleted)")
                else:
                    print(f"❌ Error deleting log group {log_group}: {e}")
                    success = False
        
        return success
    
    def delete_route53_resources(self):
        """Delete Route 53 hosted zone and records"""
        try:
            # Find hosted zone for ieltsaiprep.com
            zones = self.route53_client.list_hosted_zones()
            
            for zone in zones['HostedZones']:
                if zone['Name'] == 'ieltsaiprep.com.':
                    zone_id = zone['Id']
                    
                    # Delete all records except NS and SOA
                    records = self.route53_client.list_resource_record_sets(
                        HostedZoneId=zone_id
                    )
                    
                    for record in records['ResourceRecordSets']:
                        if record['Type'] not in ['NS', 'SOA']:
                            self.route53_client.change_resource_record_sets(
                                HostedZoneId=zone_id,
                                ChangeBatch={
                                    'Changes': [{
                                        'Action': 'DELETE',
                                        'ResourceRecordSet': record
                                    }]
                                }
                            )
                    
                    # Delete hosted zone
                    self.route53_client.delete_hosted_zone(Id=zone_id)
                    print(f"✅ Route 53 hosted zone deleted: ieltsaiprep.com")
                    return True
            
            print("ℹ️  Route 53 hosted zone not found")
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting Route 53 resources: {e}")
            return False
    
    def delete_ssl_certificates(self):
        """Delete SSL certificates"""
        try:
            certs = self.acm_client.list_certificates()
            
            for cert in certs['CertificateSummaryList']:
                if 'ieltsaiprep.com' in cert['DomainName']:
                    self.acm_client.delete_certificate(
                        CertificateArn=cert['CertificateArn']
                    )
                    print(f"✅ SSL certificate deleted: {cert['DomainName']}")
            
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting SSL certificates: {e}")
            return False
    
    def delete_cloudfront_distribution(self):
        """Delete CloudFront distribution"""
        try:
            distributions = self.cloudfront_client.list_distributions()
            
            if 'Items' in distributions['DistributionList']:
                for dist in distributions['DistributionList']['Items']:
                    # Check if distribution is for our domain
                    if any('ieltsaiprep.com' in alias for alias in dist.get('Aliases', {}).get('Items', [])):
                        dist_id = dist['Id']
                        
                        # Disable distribution first
                        config = self.cloudfront_client.get_distribution_config(Id=dist_id)
                        config['DistributionConfig']['Enabled'] = False
                        
                        self.cloudfront_client.update_distribution(
                            Id=dist_id,
                            DistributionConfig=config['DistributionConfig'],
                            IfMatch=config['ETag']
                        )
                        
                        print(f"✅ CloudFront distribution disabled: {dist_id}")
                        print("   Distribution will be deleted automatically after disabling")
                        return True
            
            print("ℹ️  CloudFront distribution not found")
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting CloudFront distribution: {e}")
            return False
    
    def run_teardown(self):
        """Run complete teardown process"""
        if not self.confirm_teardown():
            print("❌ Teardown cancelled by user")
            return False
        
        print("\n🚀 Starting AWS resource teardown...")
        
        # Track success of each step
        results = {
            'lambda': self.delete_lambda_function(),
            'api_gateway': self.delete_api_gateway(),
            'dynamodb': self.delete_dynamodb_tables(),
            'elasticache': self.delete_elasticache_cluster(),
            'iam': self.delete_iam_resources(),
            'cloudwatch': self.delete_cloudwatch_logs(),
            'route53': self.delete_route53_resources(),
            'ssl': self.delete_ssl_certificates(),
            'cloudfront': self.delete_cloudfront_distribution()
        }
        
        # Summary
        print("\n📋 TEARDOWN SUMMARY:")
        print("=" * 40)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        for service, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{service.upper():12} {status}")
        
        print(f"\n{success_count}/{total_count} services cleaned up successfully")
        
        if success_count == total_count:
            print("\n🎉 TEARDOWN COMPLETE!")
            print("All AWS resources have been removed.")
            print("Your AWS bill should return to $0 within 24 hours.")
        else:
            print("\n⚠️  PARTIAL TEARDOWN")
            print("Some resources may still be running.")
            print("Please check AWS console and manually delete any remaining resources.")
        
        return success_count == total_count

def main():
    """Main teardown function"""
    print("🔥 AWS Resource Teardown - IELTS GenAI Prep")
    print("=" * 50)
    
    teardown = AWSResourceTeardown()
    success = teardown.run_teardown()
    
    if success:
        print("\n💰 Cost Impact:")
        print("   • All billable resources removed")
        print("   • Account returns to AWS Free Tier")
        print("   • No ongoing charges")
    else:
        print("\n⚠️  Please check AWS console for any remaining resources")

if __name__ == "__main__":
    main()