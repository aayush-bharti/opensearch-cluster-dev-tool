# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import boto3
import os
import sys
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any
from datetime import datetime
import json
import tempfile
from constants import TaskTypes, ResultFields, ConfigFields

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class S3Uploader:
    """S3 upload service with timestamp-based folder organization."""
    
    def __init__(self, region: str = "us-east-1", bucket_name: str = None, workflow_timestamp: str = None):
        self.region = region
        self.bucket_name = bucket_name
        # Use provided timestamp or generate new one for this workflow session
        self.workflow_timestamp = workflow_timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
        
        try:
            self.session = boto3.Session()
            self.s3_client = self.session.client('s3', region_name=region)
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS CLI or set environment variables.")
            sys.exit(1)
    
    def ensure_bucket_exists(self) -> bool:
        """Ensure the S3 bucket exists, create if needed."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ S3 bucket exists: {self.bucket_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.info(f"📤 Creating S3 bucket: {self.bucket_name}")
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    
                    # Set bucket to private for security
                    self.s3_client.put_public_access_block(
                        Bucket=self.bucket_name,
                        PublicAccessBlockConfiguration={
                            'BlockPublicAcls': True,
                            'IgnorePublicAcls': True,
                            'BlockPublicPolicy': True,
                            'RestrictPublicBuckets': True
                        }
                    )
                    logger.info(f"✅ S3 bucket created: {self.bucket_name}")
                    return True
                except Exception as create_error:
                    logger.error(f"❌ Failed to create bucket: {create_error}")
                    return False
            else:
                logger.error(f"❌ Error checking bucket: {e}")
                return False
    
    # upload a file to S3
    def upload_file(self, file_path: str, s3_key: str, content_type: str = None) -> Dict[str, Any]:
        """Upload a file to S3."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.ensure_bucket_exists():
            raise Exception("Failed to ensure bucket exists")
        
        file_size = os.path.getsize(file_path)
        logger.info(f"📤 Uploading {file_path} ({file_size / (1024*1024):.2f} MB) to s3://{self.bucket_name}/{s3_key}")
        
        try:
            # Upload with progress callback
            def progress_callback(bytes_transferred):
                percentage = (bytes_transferred / file_size) * 100
                print(f"\rProgress: {percentage:.1f}%", end='', flush=True)
            
            upload_kwargs = {
                'Filename': file_path,
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'Callback': progress_callback
            }
            
            if content_type:
                upload_kwargs['ExtraArgs'] = {'ContentType': content_type}
            
            self.s3_client.upload_file(**upload_kwargs)
            print()
            
            # Generate URLs
            s3_uri = f"s3://{self.bucket_name}/{s3_key}"
            https_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"✅ File upload successful!")
            logger.info(f"   S3 URI: {s3_uri}")
            logger.info(f"   HTTPS URL: {https_url}")
            
            return {
                ResultFields.S3_URI: s3_uri,
                "https_url": https_url,
                "bucket_name": self.bucket_name,
                "s3_key": s3_key,
                "file_size": file_size,
                "timestamp": self.workflow_timestamp
            }
            
        except Exception as e:
            logger.error(f"❌ File upload failed: {e}")
            raise
    
    # upload JSON data to S3
    def upload_json_data(self, data: Dict[str, Any], s3_key: str) -> Dict[str, Any]:
        """Upload JSON data to S3."""
        if not self.ensure_bucket_exists():
            raise Exception("Failed to ensure bucket exists")
        
        # Convert data to JSON string
        json_content = json.dumps(data, indent=2)
        file_size = len(json_content.encode('utf-8'))
        
        logger.info(f"📝 Uploading JSON data to: s3://{self.bucket_name}/{s3_key}")
        logger.info(f"   File size: {file_size / 1024:.2f} KB")
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_content,
                ContentType='application/json'
            )
            
            # Generate URLs
            s3_uri = f"s3://{self.bucket_name}/{s3_key}"
            https_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"✅ JSON data upload successful!")
            logger.info(f"   S3 URI: {s3_uri}")
            logger.info(f"   HTTPS URL: {https_url}")
            
            return {
                ResultFields.S3_URI: s3_uri,
                "https_url": https_url,
                "bucket_name": self.bucket_name,
                "s3_key": s3_key,
                "file_size": file_size,
                "timestamp": self.workflow_timestamp
            }
            
        except Exception as e:
            logger.error(f"❌ JSON data upload failed: {e}")
            raise
    
    # upload the build manifest to S3
    def upload_build_manifest(self, manifest_path: str) -> Dict[str, Any]:
        """Upload build manifest to S3 using new structure: timestamp/build/manifest.yaml"""
        filename = os.path.basename(manifest_path)
        s3_key = f"{self.workflow_timestamp}/{TaskTypes.BUILD}/{filename}"
        return self.upload_file(manifest_path, s3_key, 'text/yaml')

    # upload the build artifact to S3
    def upload_build_artifact(self, file_path: str) -> Dict[str, Any]:
        """Upload build artifact to S3 using new structure: timestamp/build/artifact.tar.gz"""
        filename = os.path.basename(file_path)
        s3_key = f"{self.workflow_timestamp}/{TaskTypes.BUILD}/{filename}"
        
        return self.upload_file(file_path, s3_key, 'application/gzip')
    
    def upload_task_results(self, task_type: str, results_data: Dict[str, Any], timing_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Upload task results to S3 using structure: timestamp/{task_type}/{task_type}-results.json
        
        Args:
            task_type: Type of task (build, deploy, benchmark)
            results_data: Task results data to upload
            timing_data: Optional timing information (started_at, completed_at)
            
        Returns:
            Dictionary with upload information
        """
        filename = f"{task_type}-results.json"
        s3_key = f"{self.workflow_timestamp}/{task_type}/{filename}"
        
        # Add metadata to results
        results_data.update({
            "upload_date": datetime.now().strftime("%m/%d/%y, %H:%M:%S"),
            "task_type": task_type,
            "region": self.region
        })
        
        # Add timing information if provided
        if timing_data:
            results_data.update({
                "task_started_at": timing_data.get("started_at"),
                "task_completed_at": timing_data.get("completed_at")
            })
        
        return self.upload_json_data(results_data, s3_key)
    
    # upload the output to S3
    def upload_output_txt(self, task_type: str, output: str, stderr: str = None, command: str = None) -> Dict[str, Any]:
        """Upload a plain text file containing the terminal output to S3."""
        output_content = ""
        if command:
            output_content += f"Command: {command}\n\n"
        if output:
            output_content += f"STDOUT:\n{output}\n"
        if stderr:
            output_content += f"\nSTDERR:\n{stderr}\n"
        
        output_filename = f"{task_type}-output.txt"
        output_s3_key = f"{self.workflow_timestamp}/{task_type}/{output_filename}"
        
        # Create temporary file for upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(output_content)
            temp_file_path = temp_file.name
        
        try:
            output_result = self.upload_file(temp_file_path, output_s3_key, 'text/plain')
        finally:
            os.unlink(temp_file_path)
        
        return output_result
