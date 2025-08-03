# 🚀 AWS Deployment Guide for LaMa + ZITS Pipeline

This guide covers deploying and running the subtitle removal pipeline on AWS with S3 integration.

## 🏗️ AWS Architecture Options

### Option 1: EC2 with Docker (Recommended)
- **Instance Types**: 
  - GPU: `p3.2xlarge`, `p3.8xlarge`, `g4dn.xlarge`, `g4dn.2xlarge`
  - CPU: `c5.4xlarge`, `c5.9xlarge`, `c6i.4xlarge`
- **Storage**: 50-100GB EBS volume
- **Benefits**: Full control, cost-effective for batch processing

### Option 2: AWS Batch with Docker
- **Compute Environment**: EC2 with GPU support
- **Job Queue**: High priority for GPU jobs
- **Benefits**: Managed scaling, automatic resource management

### Option 3: ECS with Fargate (CPU only)
- **Task Definition**: Docker container with 4-8 vCPUs
- **Memory**: 16-32GB RAM
- **Benefits**: Serverless, no instance management

## 🔧 Setup Instructions

### Prerequisites

1. **AWS CLI installed and configured**
```bash
pip install awscli
aws configure
```

2. **Docker installed** (for local testing)
```bash
# Ubuntu/Debian
sudo apt-get install docker.io
sudo usermod -aG docker $USER

# Amazon Linux 2
sudo yum install docker
sudo service docker start
```

3. **NVIDIA Docker** (for GPU instances)
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### EC2 Instance Setup

1. **Launch EC2 Instance**
```bash
# Create security group
aws ec2 create-security-group \
    --group-name lama-zits-sg \
    --description "Security group for LaMa ZITS pipeline"

# Allow SSH access
aws ec2 authorize-security-group-ingress \
    --group-name lama-zits-sg \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Launch instance (example for g4dn.xlarge)
aws ec2 run-instances \
    --image-id ami-0c94855ba95b798c7 \  # Deep Learning AMI
    --count 1 \
    --instance-type g4dn.xlarge \
    --key-name your-key-pair \
    --security-groups lama-zits-sg \
    --block-device-mappings DeviceName=/dev/sda1,Ebs={VolumeSize=100}
```

2. **Instance Initialization Script**
```bash
#!/bin/bash
# Save as user-data.sh and use with --user-data file://user-data.sh

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo service docker start
sudo usermod -aG docker ec2-user

# Install nvidia-docker (for GPU instances)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo rpm --import -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | sudo tee /etc/yum.repos.d/nvidia-docker.repo
sudo yum install -y nvidia-docker2
sudo systemctl restart docker

# Clone repository
cd /home/ec2-user
git clone https://github.com/your-repo/subtitle-burn-remover.git
cd subtitle-burn-remover/lama_zits_unified_pipeline

# Make scripts executable
chmod +x test_pipeline.sh
```

## 📦 S3 Setup

### Create S3 Buckets
```bash
# Create input bucket
aws s3 mb s3://your-video-input-bucket

# Create output bucket  
aws s3 mb s3://your-video-output-bucket

# Set up proper permissions (adjust as needed)
aws s3api put-bucket-policy \
    --bucket your-video-input-bucket \
    --policy file://bucket-policy.json
```

### Bucket Policy Example (bucket-policy.json)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR-ACCOUNT-ID:root"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-video-input-bucket/*",
                "arn:aws:s3:::your-video-output-bucket/*"
            ]
        }
    ]
}
```

## 🚀 Running the Pipeline

### Method 1: Direct EC2 Execution
```bash
# SSH to your EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Navigate to pipeline directory
cd subtitle-burn-remover/lama_zits_unified_pipeline

# Set AWS credentials (if not using IAM roles)
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Run with S3 input and output
./test_pipeline.sh aws gpu \
    s3://your-video-input-bucket/input-video.mp4 \
    s3://your-video-output-bucket/results/

# Run with synthetic data
./test_pipeline.sh aws gpu
```

### Method 2: Docker Compose
```bash
# Create environment file
cat > .env << EOF
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_INPUT_VIDEO=s3://your-video-input-bucket/input-video.mp4
S3_OUTPUT_LOCATION=s3://your-video-output-bucket/results/
USE_SYNTHETIC_DATA=false
EOF

# Run with GPU
docker-compose --profile aws-gpu up

# Run with CPU
docker-compose --profile aws-cpu up
```

### Method 3: AWS Batch Job
```bash
# Create job definition
aws batch register-job-definition \
    --job-definition-name lama-zits-pipeline \
    --type container \
    --container-properties file://job-definition.json

# Submit job
aws batch submit-job \
    --job-name video-processing-$(date +%s) \
    --job-queue your-job-queue \
    --job-definition lama-zits-pipeline \
    --parameters inputVideo=s3://bucket/video.mp4,outputLocation=s3://bucket/output/
```

## 📊 Cost Optimization

### Instance Recommendations

| Use Case | Instance Type | vCPUs | Memory | GPU | Hourly Cost* |
|----------|---------------|-------|---------|-----|--------------|
| Development | g4dn.xlarge | 4 | 16GB | 1x T4 | $0.526 |
| Production | g4dn.2xlarge | 8 | 32GB | 1x T4 | $0.752 |
| Large Videos | p3.2xlarge | 8 | 61GB | 1x V100 | $3.06 |
| CPU Fallback | c5.4xlarge | 16 | 32GB | None | $0.68 |

*Prices are approximate and vary by region

### Cost Saving Tips

1. **Use Spot Instances**: 50-70% cost reduction
```bash
aws ec2 run-instances \
    --instance-market-options MarketType=spot,SpotOptions={MaxPrice=0.30}
```

2. **Auto Scaling**: Scale down when not in use
3. **S3 Intelligent Tiering**: Automatic cost optimization for storage
4. **Reserved Instances**: For predictable workloads

## 🔍 Monitoring and Logging

### CloudWatch Metrics
```bash
# Install CloudWatch agent
sudo yum install -y amazon-cloudwatch-agent

# Configure custom metrics
aws logs create-log-group --log-group-name /aws/ec2/lama-zits
```

### Performance Monitoring
```bash
# GPU utilization
nvidia-smi -l 1

# System resources
htop

# Docker container stats
docker stats
```

## 🛠️ Troubleshooting

### Common Issues

**GPU not detected**
```bash
# Check NVIDIA driver
nvidia-smi

# Verify Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.3-base-ubuntu20.04 nvidia-smi
```

**S3 Permission Denied**
```bash
# Test S3 access
aws s3 ls s3://your-bucket/

# Check IAM permissions
aws iam get-user
aws iam list-attached-user-policies --user-name your-username
```

**Out of Memory**
```bash
# Check available memory
free -h

# Monitor Docker memory usage
docker system df
docker system prune -f
```

### Debug Mode
```bash
export DEBUG=1
./test_pipeline.sh aws gpu
```

## 📋 IAM Permissions

Create an IAM policy with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-video-*",
                "arn:aws:s3:::your-video-*/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream", 
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

## 🎯 Production Considerations

1. **Security**: Use IAM roles instead of access keys
2. **Networking**: Deploy in private subnets with NAT gateway
3. **Backup**: Enable S3 versioning for input/output buckets
4. **Monitoring**: Set up CloudWatch alarms for failures
5. **Scaling**: Use Auto Scaling Groups for high throughput

## 📞 Support

For AWS-specific issues:
- Check [AWS Documentation](https://docs.aws.amazon.com/)
- Use [AWS Support](https://aws.amazon.com/support/)
- Monitor [AWS Service Health](https://status.aws.amazon.com/)

---

**This guide ensures your subtitle removal pipeline runs efficiently and cost-effectively on AWS! 🚀**
