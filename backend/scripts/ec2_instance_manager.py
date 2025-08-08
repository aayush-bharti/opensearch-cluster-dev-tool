# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import boto3
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError

# used to log info to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EC2 instance manager class
class EC2InstanceManager:
    """Manages EC2 instance operations including creation, monitoring, and termination."""
    
    def __init__(self, session: boto3.Session):
        self.session = session
        self.ec2_client = session.client('ec2')
        self.instance_id = None
        self.benchmark_id = f"ec2_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # get the default VPC and a public subnet from it
    def get_default_vpc_and_subnet(self) -> tuple:
        """Get the default VPC and a public subnet from it."""
        try:
            # get the default VPC
            vpc_response = self.ec2_client.describe_vpcs(
                Filters=[{"Name": "is-default", "Values": ["true"]}]
            )
            
            if not vpc_response['Vpcs']:
                raise Exception("No default VPC found in this region")
            
            default_vpc = vpc_response['Vpcs'][0]
            vpc_id = default_vpc['VpcId']
            logger.info(f"🏗️ Found default VPC: {vpc_id}")
            
            # get the public subnets in the default VPC
            subnet_response = self.ec2_client.describe_subnets(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "map-public-ip-on-launch", "Values": ["true"]}
                ]
            )
            
            if not subnet_response['Subnets']:
                raise Exception("No public subnets found in default VPC")
            
            # choose the first public subnet
            default_subnet = subnet_response['Subnets'][0]
            subnet_id = default_subnet['SubnetId']
            logger.info(f"🏗️ Found public subnet: {subnet_id}")
            
            return vpc_id, subnet_id
            
        except Exception as e:
            logger.error(f"❌ Failed to get default VPC and subnet: {e}")
            raise

    # get the appropriate AMI ID for the current region and architecture
    def get_ami_id(self, instance_type: str, region: str) -> str:
        """Get the appropriate AMI ID for the current region and architecture."""
        # check if we should use ARM based on instance type
        use_arm = instance_type.startswith(("c6g", "c7g", "m6g", "m7g", "r6g", "r7g", "t4g"))
        
        try:
            # query AWS for the latest Amazon Linux 2 AMI
            if use_arm:
                # get the ARM64 Amazon Linux 2 AMI
                response = self.ec2_client.describe_images(
                    Owners=['amazon'],
                    Filters=[
                        {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-arm64-gp2']},
                        {'Name': 'state', 'Values': ['available']},
                        {'Name': 'architecture', 'Values': ['arm64']}
                    ]
                )
                logger.info(f"📦 Looking for ARM64 Amazon Linux 2 AMI in {region}")
            else:
                # get the x86_64 Amazon Linux 2 AMI
                response = self.ec2_client.describe_images(
                    Owners=['amazon'],
                    Filters=[
                        {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                        {'Name': 'state', 'Values': ['available']},
                        {'Name': 'architecture', 'Values': ['x86_64']}
                    ]
                )
                logger.info(f"📦 Looking for x86_64 Amazon Linux 2 AMI in {region}")
            
            if not response['Images']:
                raise Exception(f"No Amazon Linux 2 AMI found for {'ARM64' if use_arm else 'x86_64'} in {region}")
            
            # sort by creation date to get the latest
            images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
            ami_id = images[0]['ImageId']
            architecture = "ARM64" if use_arm else "x86_64"
            
            logger.info(f"📦 Using {architecture} AMI {ami_id} for region {region}")
            return ami_id
            
        except Exception as e:
            logger.error(f"❌ Failed to get AMI: {e}")
            # fallback to known AMIs
            if use_arm:
                fallback_amis = {
                    'us-east-1': 'ami-0c2b8ca1dad447f8a',
                    'us-east-2': 'ami-0a0c8eebcdd6dcbd0',
                    'us-west-1': 'ami-0c1a2f6a2b6b6b6b6',
                    'us-west-2': 'ami-0892d3c7ee96c0bf7',
                }
            else:
                fallback_amis = {
                    'us-east-1': 'ami-0c02fb55956c7d316',
                    'us-east-2': 'ami-0a0c8eebcdd6dcbd0',
                    'us-west-1': 'ami-0c1a2f6a2b6b6b6b6',
                    'us-west-2': 'ami-0892d3c7ee96c0bf7',
                }
            
            ami_id = fallback_amis.get(region, fallback_amis['us-east-1'])
            architecture = "ARM64" if use_arm else "x86_64"
            logger.warning(f"⚠️ Using fallback {architecture} AMI {ami_id} for region {region}")
            return ami_id

    # create the EC2 instance
    def create_ec2_instance(self, config: Dict[str, Any], user_data: str, security_group_id: str) -> Dict[str, Any]:
        """Create an EC2 instance for running the benchmark."""
        try:
            logger.info("🚀 Creating EC2 instance for benchmark...")
            
            # get the VPC ID and subnet ID (use provided or default)
            if config.get("subnet_id"):
                # use the provided subnet
                subnet_response = self.ec2_client.describe_subnets(SubnetIds=[config["subnet_id"]])
                vpc_id = subnet_response['Subnets'][0]['VpcId']
                subnet_id = config["subnet_id"]
                logger.info(f"🏗️ Using provided subnet: {subnet_id}")
            else:
                # use the default VPC and subnet
                vpc_id, subnet_id = self.get_default_vpc_and_subnet()
                logger.info(f"🏗️ Using default VPC and subnet")
            
            # choose the AMI based on region
            ami_id = self.get_ami_id(config["instance_type"], self.session.region_name or 'us-east-1')
            
            # launch the EC2 instance
            response = self.ec2_client.run_instances(
                ImageId=ami_id,
                InstanceType=config["instance_type"],
                KeyName=config["key_name"],
                UserData=user_data,
                MinCount=1,
                MaxCount=1,
                NetworkInterfaces=[
                    {
                        'DeviceIndex': 0,
                        'SubnetId': subnet_id,
                        'Groups': [security_group_id],
                        'AssociatePublicIpAddress': True
                    }
                ],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': f'OpenSearch-Benchmark-Worker-{self.benchmark_id}'
                            },
                            {
                                'Key': 'Purpose',
                                'Value': 'OpenSearch-Benchmark'
                            },
                            {
                                'Key': 'BenchmarkId',
                                'Value': self.benchmark_id
                            }
                        ]
                    }
                ]
            )
            
            self.instance_id = response['Instances'][0]['InstanceId']
            logger.info(f"✅ Created EC2 instance: {self.instance_id}")
            
            # Wait for instance to be running
            logger.info("⏳ Waiting for instance to start...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[self.instance_id], WaiterConfig={'Delay': 15, 'MaxAttempts': 40})
            
            # Get instance details
            instance = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            instance_data = instance['Reservations'][0]['Instances'][0]
            public_ip = instance_data.get('PublicIpAddress')
            private_ip = instance_data.get('PrivateIpAddress')
            
            logger.info(f"✅ Instance is running")
            logger.info(f"   Public IP: {public_ip}")
            logger.info(f"   Private IP: {private_ip}")
            
            return {
                "instance_id": self.instance_id,
                "public_ip": public_ip,
                "private_ip": private_ip,
                "security_group_id": security_group_id,
                "vpc_id": vpc_id,
                "subnet_id": subnet_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create EC2 instance: {e}")
            raise

    # monitor the EC2 instance progress
    def monitor_instance_progress(self, timeout_minutes: int = 60) -> bool:
        """Monitor the EC2 instance progress and provide real-time status updates."""
        try:
            logger.info(f"🔍 Monitoring EC2 instance progress (timeout: {timeout_minutes} minutes)...")
            
            start_time = time.time()
            timeout_seconds = timeout_minutes * 60
            last_status = None
            
            while time.time() - start_time < timeout_seconds:
                try:
                    # Check if instance is still running
                    response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
                    instance = response['Reservations'][0]['Instances'][0]
                    state = instance['State']['Name']
                    
                    if state == 'terminated':
                        logger.info("✅ Instance terminated - benchmark completed")
                        return True
                    elif state == 'stopped':
                        logger.info("✅ Instance stopped - benchmark completed")
                        return True
                    elif state != 'running':
                        logger.warning(f"⚠️ Instance in unexpected state: {state}")
                        return False
                    
                    # Try to get user data logs via SSM or check status file
                    try:
                        # Check if we can get status via SSM (if instance has SSM agent)
                        ssm_client = self.session.client('ssm')
                        status_response = ssm_client.send_command(
                            InstanceIds=[self.instance_id],
                            DocumentName="AWS-RunShellScript",
                            Parameters={'commands': ['cat /opt/benchmark/status.txt 2>/dev/null || echo "STATUS_NOT_AVAILABLE"']}
                        )
                        
                        command_id = status_response['Command']['CommandId']
                        time.sleep(2)  # Wait for command to execute
                        
                        output_response = ssm_client.get_command_invocation(
                            CommandId=command_id,
                            InstanceId=self.instance_id
                        )
                        
                        if output_response['Status'] == 'Success':
                            status = output_response['StandardOutputContent'].strip()
                            if status != last_status:
                                if status == "SETUP_COMPLETE":
                                    logger.info("✅ EC2 instance setup completed - benchmark starting...")
                                elif status == "BENCHMARK_COMPLETE":
                                    logger.info("✅ Benchmark execution completed!")
                                    return True
                                elif status == "STATUS_NOT_AVAILABLE":
                                    logger.info("ℹ️ Waiting for setup to complete...")
                                else:
                                    logger.info(f"ℹ️ Instance status: {status}")
                                last_status = status
                        
                    except Exception as e:
                        # SSM not available, try to get user data logs
                        try:
                            # Get user data logs from the instance
                            log_response = ssm_client.send_command(
                                InstanceIds=[self.instance_id],
                                DocumentName="AWS-RunShellScript",
                                Parameters={'commands': ['tail -n 20 /var/log/user-data.log 2>/dev/null || echo "LOGS_NOT_AVAILABLE"']}
                            )
                            
                            command_id = log_response['Command']['CommandId']
                            time.sleep(2)
                            
                            log_output = ssm_client.get_command_invocation(
                                CommandId=command_id,
                                InstanceId=self.instance_id
                            )
                            
                            if log_output['Status'] == 'Success':
                                logs = log_output['StandardOutputContent']
                                if "✅" in logs or "🚀" in logs:
                                    # Extract the last few lines with progress indicators
                                    lines = logs.strip().split('\n')
                                    recent_lines = [line for line in lines[-5:] if any(indicator in line for indicator in ['✅', '❌', 'ℹ️', '🚀', '📦', '📊'])]
                                    if recent_lines:
                                        for line in recent_lines:
                                            if line.strip() and line not in last_status:
                                                logger.info(f"📋 Instance: {line.strip()}")
                                                last_status = line
                                
                        except Exception as log_e:
                            # If we can't get logs, just show basic status
                            if last_status != "monitoring":
                                logger.info("ℹ️ Monitoring instance progress...")
                                last_status = "monitoring"
                    
                    # Wait before checking again
                    time.sleep(30)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error monitoring instance: {e}")
                    time.sleep(30)
            
            logger.warning(f"⚠️ Timeout reached ({timeout_minutes} minutes)")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error monitoring instance progress: {e}")
            return False

    # terminate the EC2 instance
    def terminate_instance(self):
        """Terminate the EC2 instance."""
        try:
            if self.instance_id:
                logger.info(f"🗑️ Terminating EC2 instance: {self.instance_id}")
                self.ec2_client.terminate_instances(InstanceIds=[self.instance_id])
                logger.info("✅ Instance termination initiated")
        except Exception as e:
            logger.error(f"❌ Failed to terminate instance: {e}")

    # get the user data logs from the EC2 instance
    def get_instance_logs(self) -> str:
        """Get the user data logs from the EC2 instance."""
        try:
            if not self.instance_id:
                return "No instance ID available"
            
            # try to get logs via SSM
            try:
                ssm_client = self.session.client('ssm')
                response = ssm_client.send_command(
                    InstanceIds=[self.instance_id],
                    DocumentName="AWS-RunShellScript",
                    Parameters={'commands': ['cat /var/log/user-data.log 2>/dev/null || echo "LOGS_NOT_AVAILABLE"']}
                )
                
                command_id = response['Command']['CommandId']
                time.sleep(3)  # Wait for command to execute
                
                output_response = ssm_client.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=self.instance_id
                )
                
                if output_response['Status'] == 'Success':
                    return output_response['StandardOutputContent']
                else:
                    return f"Failed to get logs: {output_response.get('StandardErrorContent', 'Unknown error')}"
                    
            except Exception as e:
                return f"Could not retrieve logs via SSM: {str(e)}"
                
        except Exception as e:
            return f"Error getting instance logs: {str(e)}"

    # log the current status of the EC2 instance
    def log_instance_status(self):
        """Log the current status of the EC2 instance."""
        try:
            if not self.instance_id:
                logger.info("ℹ️ No instance ID available")
                return
            
            response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            instance = response['Reservations'][0]['Instances'][0]
            
            state = instance['State']['Name']
            public_ip = instance.get('PublicIpAddress', 'N/A')
            private_ip = instance.get('PrivateIpAddress', 'N/A')
            
            logger.info(f"📋 Instance Status:")
            logger.info(f"   ID: {self.instance_id}")
            logger.info(f"   State: {state}")
            logger.info(f"   Public IP: {public_ip}")
            logger.info(f"   Private IP: {private_ip}")
            
            # get recent logs
            logs = self.get_instance_logs()
            if logs and "LOGS_NOT_AVAILABLE" not in logs:
                # Extract last few lines with progress indicators
                lines = logs.strip().split('\n')
                recent_lines = [line for line in lines[-10:] if any(indicator in line for indicator in ['✅', '❌', 'ℹ️', '🚀', '📦', '📊'])]
                if recent_lines:
                    logger.info(f"📋 Recent Instance Activity:")
                    for line in recent_lines[-5:]:  # Show last 5 progress lines
                        if line.strip():
                            logger.info(f"   {line.strip()}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not get instance status: {e}")

    # get the current instance ID
    def get_instance_id(self) -> Optional[str]:
        """Get the current instance ID."""
        return self.instance_id

    # get the benchmark ID
    def get_benchmark_id(self) -> str:
        """Get the benchmark ID."""
        return self.benchmark_id
