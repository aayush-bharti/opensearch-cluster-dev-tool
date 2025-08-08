# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import boto3
import logging
import subprocess
import time
from typing import Dict
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

# used to log info to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS credentials manager class
class AWSCredentialsManager:
    """Manages AWS credentials validation and retrieval."""
    
    def __init__(self):
        self.session = boto3.Session()
        self.region = self.session.region_name or 'us-east-1'
    
    # validate the AWS credentials
    def validate_aws_credentials(self):
        """Validate that AWS credentials are available from default locations."""
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials is None:
                raise NoCredentialsError("No AWS credentials found")
            
            # Test credentials by making a simple call
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            account_id = identity.get('Account', 'unknown')
            user_arn = identity.get('Arn', 'unknown')
            
            logger.info(f"✅ AWS credentials validated successfully")
            logger.info(f"   Account: {account_id}")
            logger.info(f"   Identity: {user_arn}")
            
        except (NoCredentialsError, PartialCredentialsError, ClientError) as e:
            logger.error(f"❌ AWS credentials validation failed: {e}")
            raise Exception(
                "AWS credentials not found or invalid. Please run 'aws configure' to set up your credentials.\n"
                "Make sure you have ~/.aws/credentials and ~/.aws/config files properly configured."
            )

    # get the local timezone
    def get_local_timezone(self) -> str:
        """Get the local machine's timezone."""
        try:
            import time
            import os
            
            # Try to read from /etc/timezone (Linux)
            if os.path.exists('/etc/timezone'):
                with open('/etc/timezone', 'r') as f:
                    timezone = f.read().strip()
                    if timezone:
                        return timezone
            
            # Try timedatectl
            try:
                result = subprocess.run(['timedatectl', 'show', '--property=Timezone', '--value'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass
            
            # Use Python's time module
            # Get timezone offset and convert to timezone name
            timezone_offset = time.timezone if time.daylight == 0 else time.altzone
            hours_offset = -timezone_offset // 3600
            
            # Map common offsets to timezone names
            offset_to_tz = {
                -8: "America/Los_Angeles",
                -7: "America/Denver",
                -6: "America/Chicago",
                -5: "America/New_York",
                0: "UTC",
                1: "Europe/London",
                2: "Europe/Berlin",
                9: "Asia/Tokyo"
            }
            
            if hours_offset in offset_to_tz:
                return offset_to_tz[hours_offset]
            else:
                # Default to UTC
                return "UTC"
                
        except Exception as e:
            logger.warning(f"Failed to detect timezone: {e}")
            return "UTC"

    # get the current AWS credentials
    def get_current_aws_credentials(self) -> Dict[str, str]:
        """Get the current AWS credentials from the local machine."""
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if credentials:
                creds_dict = {
                    'access_key': credentials.access_key,
                    'secret_key': credentials.secret_key,
                    'region': session.region_name or 'us-east-1'
                }
                
                # Add token if it's a temporary credential
                if credentials.token:
                    creds_dict['token'] = credentials.token
                
                logger.info(f"✅ Retrieved AWS credentials for region: {creds_dict['region']}")
                return creds_dict
            else:
                raise Exception("No AWS credentials found")
        except Exception as e:
            logger.error(f"❌ Failed to get AWS credentials: {e}")
            raise

    # get the boto3 session
    def get_session(self):
        """Get the boto3 session."""
        return self.session
    
    # get the current AWS region
    def get_region(self) -> str:
        """Get the current AWS region."""
        return self.region
