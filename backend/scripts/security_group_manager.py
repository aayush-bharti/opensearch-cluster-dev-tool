# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import boto3
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

# used to log info to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# security group manager class
class SecurityGroupManager:
    """Manages security group operations for EC2 instances and OpenSearch clusters."""
    
    def __init__(self, session: boto3.Session):
        self.session = session
        self.ec2_client = session.client('ec2')
        self.cluster_security_group_id = None
    
    # extract the security group ID from deploy output
    def extract_cluster_security_group(self, cluster_endpoint: str, deploy_result: Dict[str, Any] = None) -> Optional[str]:
        """Extract the security group ID from deploy output or OpenSearch cluster endpoint."""
        
        try:
            # try to get security group from deploy result if available
            if deploy_result and deploy_result.get("cluster_info", {}).get("security_group_id"):
                security_group_id = deploy_result["cluster_info"]["security_group_id"]
                self.cluster_security_group_id = security_group_id
                logger.info(f"✅ Found security group from deploy output: {security_group_id}")
                return security_group_id
                    
        except Exception as e:
            logger.error(f"❌ Failed to extract cluster security group: {e}")
            return None

    # get the default security group for the VPC
    def get_default_security_group(self, vpc_id: str) -> str:
        """Get the default security group for the VPC."""
        try:
            # Get the default security group for the VPC
            response = self.ec2_client.describe_security_groups(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "group-name", "Values": ["default"]}
                ]
            )
            
            if response["SecurityGroups"]:
                default_sg_id = response["SecurityGroups"][0]["GroupId"]
                logger.info(f"✅ Using default security group: {default_sg_id}")
                return default_sg_id
            else:
                raise Exception(f"No default security group found for VPC {vpc_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to get default security group: {e}")
            raise

    # add the EC2 instance's IP to the cluster's security group inbound rules
    def add_ec2_to_cluster_security_group(self, ec2_instance_id: str) -> bool:
        """Add the EC2 instance's IP to the cluster's security group inbound rules."""
        try:
            if not self.cluster_security_group_id:
                logger.warning("⚠️ No cluster security group ID available")
                return False
            
            # Get EC2 instance details to find its public IP
            response = self.ec2_client.describe_instances(InstanceIds=[ec2_instance_id])
            instance = response['Reservations'][0]['Instances'][0]
            public_ip = instance.get('PublicIpAddress')
            
            if not public_ip:
                logger.error("❌ Could not get public IP for EC2 instance")
                return False
            
            logger.info(f"🔒 Adding EC2 instance public IP {public_ip} to cluster security group {self.cluster_security_group_id}")
            
            # Add inbound rule to cluster security group - allow all traffic
            self.ec2_client.authorize_security_group_ingress(
                GroupId=self.cluster_security_group_id,
                IpPermissions=[
                    {
                        "IpProtocol": "-1",  # All protocols
                        "FromPort": -1,       # All ports
                        "ToPort": -1,         # All ports
                        "IpRanges": [{"CidrIp": f"{public_ip}/32", "Description": f"EC2 benchmark instance {ec2_instance_id}"}]
                    }
                ]
            )
            
            logger.info(f"✅ Successfully added EC2 instance to cluster security group")
            return True
            
        except ClientError as e:
            if "InvalidPermission.Duplicate" in str(e):
                logger.info("✅ EC2 instance already has access to cluster")
                return True
            else:
                logger.error(f"❌ Failed to add EC2 instance to cluster security group: {e}")
                return False
        except Exception as e:
            logger.error(f"❌ Error adding EC2 instance to cluster security group: {e}")
            return False

    # cleanup the security groups
    def cleanup_security_groups(self, instance_id: str):
        """Clean up security groups created for this benchmark."""
        try:
            # Remove EC2 instance from cluster security group
            if self.cluster_security_group_id and instance_id:
                try:
                    # Get instance public IP
                    response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
                    instance = response['Reservations'][0]['Instances'][0]
                    public_ip = instance.get('PublicIpAddress')
                    
                    if public_ip:
                        self.ec2_client.revoke_security_group_ingress(
                            GroupId=self.cluster_security_group_id,
                            IpPermissions=[
                                {
                                    "IpProtocol": "-1",  # All protocols
                                    "FromPort": -1,       # All ports
                                    "ToPort": -1,         # All ports
                                    "IpRanges": [{"CidrIp": f"{public_ip}/32"}]
                                }
                            ]
                        )
                        logger.info("✅ Removed EC2 instance public IP from cluster security group")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to remove EC2 instance from cluster security group: {e}")
            
            # Note: We're using the default security group, so we don't delete it
            # The default security group is managed by AWS and should not be deleted
            logger.info("ℹ️ Using default security group - no cleanup needed")
                    
        except Exception as e:
            logger.error(f"❌ Error during security group cleanup: {e}")

    # get the cluster security group ID
    def get_cluster_security_group_id(self) -> Optional[str]:
        """Get the cluster security group ID."""
        return self.cluster_security_group_id
