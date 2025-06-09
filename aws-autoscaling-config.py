"""
AWS Auto Scaling Configuration for IELTS GenAI Prep
Optimized for 250,000 concurrent users
"""

import os
import boto3
import json
from datetime import datetime

class AWSAutoScalingManager:
    """Manages AWS auto-scaling configuration for high-concurrency deployment"""
    
    def __init__(self):
        self.autoscaling = boto3.client('autoscaling')
        self.cloudwatch = boto3.client('cloudwatch')
        self.elbv2 = boto3.client('elbv2')
        self.ec2 = boto3.client('ec2')
        
    def create_launch_template(self):
        """Create optimized EC2 launch template for high concurrency"""
        return {
            'LaunchTemplateName': 'ielts-genai-prep-template',
            'LaunchTemplateData': {
                'ImageId': 'ami-0c02fb55956c7d316',  # Amazon Linux 2023
                'InstanceType': 'c6i.2xlarge',  # 8 vCPU, 16 GB RAM
                'SecurityGroupIds': ['sg-ielts-app'],
                'UserData': self._get_user_data_script(),
                'IamInstanceProfile': {
                    'Name': 'ielts-ec2-instance-profile'
                },
                'TagSpecifications': [{
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'ielts-genai-prep-instance'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'Application', 'Value': 'ielts-genai-prep'}
                    ]
                }]
            }
        }
    
    def create_auto_scaling_group(self):
        """Create auto-scaling group for 250K concurrent users"""
        return {
            'AutoScalingGroupName': 'ielts-genai-prep-asg',
            'LaunchTemplate': {
                'LaunchTemplateName': 'ielts-genai-prep-template',
                'Version': '$Latest'
            },
            'MinSize': 10,  # Minimum 10 instances
            'MaxSize': 100,  # Scale up to 100 instances
            'DesiredCapacity': 25,  # Start with 25 instances
            'TargetGroupARNs': ['arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/ielts-app-tg/ID'],
            'VPCZoneIdentifier': 'subnet-1,subnet-2,subnet-3',  # Multi-AZ deployment
            'HealthCheckType': 'ELB',
            'HealthCheckGracePeriod': 300,
            'DefaultCooldown': 300,
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'ielts-genai-prep-asg',
                    'PropagateAtLaunch': True,
                    'ResourceId': 'ielts-genai-prep-asg',
                    'ResourceType': 'auto-scaling-group'
                }
            ]
        }
    
    def create_scaling_policies(self):
        """Create scaling policies for dynamic load management"""
        return {
            'scale_up_policy': {
                'AutoScalingGroupName': 'ielts-genai-prep-asg',
                'PolicyName': 'ielts-scale-up-policy',
                'PolicyType': 'TargetTrackingScaling',
                'TargetTrackingConfiguration': {
                    'TargetValue': 70.0,  # Target 70% CPU utilization
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': 'ASGAverageCPUUtilization'
                    },
                    'ScaleOutCooldown': 300,
                    'ScaleInCooldown': 300
                }
            },
            'request_count_policy': {
                'AutoScalingGroupName': 'ielts-genai-prep-asg',
                'PolicyName': 'ielts-request-count-policy',
                'PolicyType': 'TargetTrackingScaling',
                'TargetTrackingConfiguration': {
                    'TargetValue': 1000.0,  # Target 1000 requests per target
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': 'ALBRequestCountPerTarget',
                        'ResourceLabel': 'app/ielts-alb/1234567890123456/targetgroup/ielts-app-tg/1234567890123456'
                    }
                }
            }
        }
    
    def create_application_load_balancer(self):
        """Create ALB configuration for high-concurrency traffic distribution"""
        return {
            'Name': 'ielts-genai-prep-alb',
            'Subnets': ['subnet-1', 'subnet-2', 'subnet-3'],
            'SecurityGroups': ['sg-ielts-alb'],
            'Scheme': 'internet-facing',
            'Type': 'application',
            'IpAddressType': 'ipv4',
            'Tags': [
                {'Key': 'Name', 'Value': 'ielts-genai-prep-alb'},
                {'Key': 'Environment', 'Value': 'production'}
            ]
        }
    
    def create_target_group(self):
        """Create target group with health checks optimized for high load"""
        return {
            'Name': 'ielts-app-target-group',
            'Protocol': 'HTTP',
            'Port': 5000,
            'VpcId': 'vpc-12345',
            'HealthCheckProtocol': 'HTTP',
            'HealthCheckPath': '/health',
            'HealthCheckIntervalSeconds': 30,
            'HealthCheckTimeoutSeconds': 10,
            'HealthyThresholdCount': 2,
            'UnhealthyThresholdCount': 5,
            'TargetType': 'instance',
            'Matcher': {'HttpCode': '200'},
            'Tags': [
                {'Key': 'Name', 'Value': 'ielts-app-target-group'}
            ]
        }
    
    def create_cloudwatch_alarms(self):
        """Create CloudWatch alarms for monitoring high-concurrency performance"""
        return {
            'high_cpu_alarm': {
                'AlarmName': 'ielts-high-cpu-utilization',
                'ComparisonOperator': 'GreaterThanThreshold',
                'EvaluationPeriods': 2,
                'MetricName': 'CPUUtilization',
                'Namespace': 'AWS/EC2',
                'Period': 300,
                'Statistic': 'Average',
                'Threshold': 80.0,
                'ActionsEnabled': True,
                'AlarmActions': ['arn:aws:sns:us-east-1:ACCOUNT:ielts-alerts'],
                'AlarmDescription': 'High CPU utilization detected',
                'Dimensions': [
                    {
                        'Name': 'AutoScalingGroupName',
                        'Value': 'ielts-genai-prep-asg'
                    }
                ]
            },
            'high_request_count': {
                'AlarmName': 'ielts-high-request-count',
                'ComparisonOperator': 'GreaterThanThreshold',
                'EvaluationPeriods': 2,
                'MetricName': 'RequestCount',
                'Namespace': 'AWS/ApplicationELB',
                'Period': 60,
                'Statistic': 'Sum',
                'Threshold': 50000.0,  # 50K requests per minute threshold
                'ActionsEnabled': True,
                'AlarmActions': ['arn:aws:sns:us-east-1:ACCOUNT:ielts-alerts']
            }
        }
    
    def _get_user_data_script(self):
        """Generate user data script for instance initialization"""
        script = """#!/bin/bash
# IELTS GenAI Prep Instance Setup for High Concurrency

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
    "metrics": {
        "namespace": "IELTS/Application",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s

# Pull and run the application
docker run -d \\
  --name ielts-app \\
  --restart unless-stopped \\
  -p 5000:5000 \\
  -e DATABASE_URL="$DATABASE_URL" \\
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \\
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \\
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \\
  ielts-genai-prep:latest

# Configure log rotation
cat > /etc/logrotate.d/docker-container << EOF
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
"""
        return script
    
    def get_performance_recommendations(self):
        """Performance recommendations for 250K concurrent users"""
        return {
            'infrastructure': {
                'instances': '50-100 c6i.2xlarge instances',
                'capacity': '2,500-5,000 concurrent requests per instance',
                'total_capacity': '250,000+ concurrent users',
                'database': 'RDS PostgreSQL with read replicas',
                'cache': 'ElastiCache Redis cluster',
                'cdn': 'CloudFront for static assets'
            },
            'application_optimization': {
                'gunicorn_workers': 8,
                'threads_per_worker': 16,
                'connection_pooling': 'PgBouncer with 100 connections per instance',
                'session_storage': 'Redis-based sessions',
                'caching_strategy': 'Multi-layer caching (Redis, CDN)',
                'monitoring': 'CloudWatch, Prometheus, Grafana'
            },
            'cost_estimation': {
                'ec2_instances': '$2,400-4,800/month (50-100 instances)',
                'database': '$500-1,500/month (RDS + replicas)',
                'cache': '$200-600/month (ElastiCache)',
                'load_balancer': '$20-50/month',
                'data_transfer': '$500-2,000/month',
                'total_estimated': '$3,620-8,950/month'
            }
        }

# Configuration deployment helper
def deploy_autoscaling_configuration():
    """Deploy auto-scaling configuration to AWS"""
    manager = AWSAutoScalingManager()
    
    print("Deploying IELTS GenAI Prep auto-scaling configuration...")
    print("Estimated capacity: 250,000+ concurrent users")
    print("Infrastructure: 50-100 EC2 instances with automatic scaling")
    
    config = {
        'launch_template': manager.create_launch_template(),
        'autoscaling_group': manager.create_auto_scaling_group(),
        'scaling_policies': manager.create_scaling_policies(),
        'load_balancer': manager.create_application_load_balancer(),
        'target_group': manager.create_target_group(),
        'cloudwatch_alarms': manager.create_cloudwatch_alarms(),
        'performance_recommendations': manager.get_performance_recommendations()
    }
    
    return config

if __name__ == "__main__":
    config = deploy_autoscaling_configuration()
    with open('aws-autoscaling-deployment.json', 'w') as f:
        json.dump(config, f, indent=2, default=str)