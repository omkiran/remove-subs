#!/usr/bin/env python3
"""
AWS S3 Handler for LaMa + ZITS Pipeline
Handles S3 downloads, uploads, and AWS configuration
"""

import boto3
import os
import sys
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

class S3Handler:
    def __init__(self):
        """Initialize S3 client with AWS credentials."""
        try:
            # Try to initialize S3 client
            self.s3_client = boto3.client('s3')
            
            # Test credentials by listing buckets (this will fail if no creds)
            self.s3_client.list_buckets()
            self.aws_available = True
            print("✅ AWS credentials configured successfully")
            
        except (NoCredentialsError, ClientError) as e:
            self.aws_available = False
            print("⚠️  AWS credentials not configured or invalid")
            print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
            print("   Or use IAM roles/instance profiles on EC2")
    
    def parse_s3_url(self, s3_url):
        """Parse S3 URL to extract bucket and key."""
        if not s3_url.startswith('s3://'):
            raise ValueError("S3 URL must start with 's3://'")
        
        # Remove s3:// prefix and split
        path = s3_url[5:]  # Remove 's3://'
        parts = path.split('/', 1)
        
        if len(parts) < 2:
            raise ValueError("S3 URL must include bucket and key: s3://bucket/key")
        
        bucket = parts[0]
        key = parts[1]
        
        return bucket, key
    
    def download_file(self, s3_url, local_path):
        """Download file from S3 to local path."""
        if not self.aws_available:
            print("❌ Cannot download from S3 - AWS not configured")
            return False
        
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            print(f"📥 Downloading from S3: {s3_url}")
            print(f"   Target: {local_path}")
            
            self.s3_client.download_file(bucket, key, local_path)
            
            # Verify file was downloaded
            if os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                print(f"✅ Downloaded successfully ({file_size / 1024 / 1024:.1f} MB)")
                return True
            else:
                print("❌ Download failed - file not found locally")
                return False
                
        except Exception as e:
            print(f"❌ S3 download failed: {str(e)}")
            return False
    
    def upload_file(self, local_path, s3_url):
        """Upload local file to S3."""
        if not self.aws_available:
            print("❌ Cannot upload to S3 - AWS not configured")
            return False
        
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            if not os.path.exists(local_path):
                print(f"❌ Local file not found: {local_path}")
                return False
            
            file_size = os.path.getsize(local_path)
            print(f"📤 Uploading to S3: {s3_url}")
            print(f"   Source: {local_path} ({file_size / 1024 / 1024:.1f} MB)")
            
            self.s3_client.upload_file(local_path, bucket, key)
            print("✅ Upload completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ S3 upload failed: {str(e)}")
            return False
    
    def upload_directory(self, local_dir, s3_base_url):
        """Upload entire directory to S3."""
        if not self.aws_available:
            print("❌ Cannot upload to S3 - AWS not configured")
            return False
        
        try:
            bucket, base_key = self.parse_s3_url(s3_base_url)
            
            uploaded_files = 0
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    
                    # Calculate relative path for S3 key
                    relative_path = os.path.relpath(local_file_path, local_dir)
                    s3_key = f"{base_key}/{relative_path}".replace('\\', '/')
                    
                    try:
                        self.s3_client.upload_file(local_file_path, bucket, s3_key)
                        uploaded_files += 1
                        print(f"   📤 Uploaded: {relative_path}")
                    except Exception as e:
                        print(f"   ❌ Failed to upload {relative_path}: {str(e)}")
            
            print(f"✅ Directory upload completed: {uploaded_files} files")
            return uploaded_files > 0
            
        except Exception as e:
            print(f"❌ Directory upload failed: {str(e)}")
            return False
    
    def check_file_exists(self, s3_url):
        """Check if file exists in S3."""
        if not self.aws_available:
            return False
        
        try:
            bucket, key = self.parse_s3_url(s3_url)
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False

def main():
    """Test S3 functionality."""
    handler = S3Handler()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Test with example URLs
            test_url = "s3://example-bucket/test-video.mp4"
            print(f"Testing S3 URL parsing: {test_url}")
            try:
                bucket, key = handler.parse_s3_url(test_url)
                print(f"   Bucket: {bucket}")
                print(f"   Key: {key}")
            except Exception as e:
                print(f"   Error: {e}")

if __name__ == "__main__":
    main()
