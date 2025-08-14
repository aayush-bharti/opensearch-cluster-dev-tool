# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from typing import Dict, Any
from constants import Status, ResultFields

# Import the functional modules
from scripts.aws_credentials_manager import AWSCredentialsManager
from scripts.ec2_instance_manager import EC2InstanceManager
from scripts.security_group_manager import SecurityGroupManager
from scripts.ec2_benchmark_executor import BenchmarkExecutor
from scripts.s3_results_manager_ec2 import S3ResultsManager

# used to log info to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EC2 workflow orchestrator class
class EC2WorkflowOrchestrator:
    """Orchestrates the complete EC2 benchmark workflow using functional modules."""
    
    def __init__(self, config: Dict[str, Any], workflow_timestamp: str = None):
        self.config = config
        self.workflow_timestamp = workflow_timestamp
        
        # Initialize AWS credentials manager
        self.aws_credentials_manager = AWSCredentialsManager()
        self.aws_credentials_manager.validate_aws_credentials()
        
        # Get AWS session and region
        self.session = self.aws_credentials_manager.get_session()
        self.region = self.aws_credentials_manager.get_region()
        
        # Initialize functional modules
        self.instance_manager = EC2InstanceManager(self.session)
        self.security_group_manager = SecurityGroupManager(self.session)
        self.benchmark_executor = BenchmarkExecutor()
        self.s3_results_manager = S3ResultsManager(self.session)
        
        # Get benchmark ID from instance manager
        self.benchmark_id = self.instance_manager.get_benchmark_id()
    
    # run the complete EC2 benchmark workflow
    def run_workflow(self, deploy_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the complete EC2 benchmark workflow."""
        try:
            logger.info("🚀 Starting EC2 benchmark workflow...")
            
            # Capture start time
            task_started_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
            logger.info(f"📅 Task started at: {task_started_at}")
            
            # Extract cluster security group
            if self.config.get("security_group_id"):
                # Use manually provided cluster security group ID
                cluster_sg = self.config["security_group_id"]
                logger.info(f"🔒 Using manually specified cluster security group: {cluster_sg}")
            else:
                # Try to extract cluster security group automatically
                cluster_sg = self.security_group_manager.extract_cluster_security_group(
                    self.config["cluster_endpoint"], deploy_result
                )
                if cluster_sg:
                    logger.info(f"🔒 Automatically extracted cluster security group: {cluster_sg}")
                else:
                    logger.warning("⚠️ Could not extract cluster security group - EC2 may not be able to access cluster")
            
            # Get AWS credentials for user data script
            aws_creds = self.aws_credentials_manager.get_current_aws_credentials()
            
            # Get local timezone for user data script
            local_timezone = self.aws_credentials_manager.get_local_timezone()
            
            # Create user data script
            user_data = self.benchmark_executor.create_user_data_script(
                config=self.config,
                aws_creds=aws_creds,
                local_timezone=local_timezone,
                workflow_timestamp=self.workflow_timestamp,
                benchmark_id=self.benchmark_id,
                task_started_at=task_started_at
            )
            
            # Get default security group for EC2 instance
            if self.config.get("subnet_id"):
                # Use provided subnet to get VPC ID
                ec2_client = self.session.client('ec2')
                subnet_response = ec2_client.describe_subnets(SubnetIds=[self.config["subnet_id"]])
                vpc_id = subnet_response['Subnets'][0]['VpcId']
            else:
                # Get VPC ID from default VPC
                vpc_id, _ = self.instance_manager.get_default_vpc_and_subnet()
            
            security_group_id = self.security_group_manager.get_default_security_group(vpc_id)
            
            # Create EC2 instance
            instance_info = self.instance_manager.create_ec2_instance(
                config=self.config,
                user_data=user_data,
                security_group_id=security_group_id
            )
            
            # Add EC2 instance to cluster security group
            if cluster_sg:
                # Set the cluster security group ID in the security group manager
                self.security_group_manager.cluster_security_group_id = cluster_sg
                self.security_group_manager.add_ec2_to_cluster_security_group(
                    self.instance_manager.get_instance_id()
                )
            
            # Log initial instance status
            logger.info("📋 Initial instance status:")
            self.instance_manager.log_instance_status()
            
            # Wait for benchmark completion with enhanced monitoring
            benchmark_success = self.instance_manager.monitor_instance_progress(
                timeout_minutes=self.config.get("timeout_minutes", 60)
            )
            
            # Log final instance status
            logger.info("📋 Final instance status:")
            self.instance_manager.log_instance_status()
            
            # Capture completion time
            task_completed_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
            logger.info(f"📅 Task completed at: {task_completed_at}")
            
            # Download and process S3 results if benchmark was successful
            s3_results = {}
            if benchmark_success:
                logger.info("📥 Downloading S3 results and updating job data...")
                s3_results = self.s3_results_manager.download_and_process_s3_results(
                    config=self.config,
                    workflow_timestamp=self.workflow_timestamp
                )
                if s3_results:
                    logger.info("✅ Successfully downloaded S3 results")
                else:
                    logger.warning("⚠️ Failed to download S3 results")
            
            # Create result
            result = {
                ResultFields.STATUS: Status.SUCCESS if benchmark_success else Status.FAILED,
                ResultFields.BENCHMARK_ID: self.benchmark_id,
                ResultFields.INSTANCE_ID: self.instance_manager.get_instance_id(),
                ResultFields.INSTANCE_INFO: instance_info,
                ResultFields.CLUSTER_SECURITY_GROUP: cluster_sg,
                ResultFields.BENCHMARK_SUCCESS: benchmark_success,
                ResultFields.TASK_STARTED_AT: task_started_at,
                ResultFields.TASK_COMPLETED_AT: task_completed_at,
                ResultFields.MESSAGE: "EC2 benchmark workflow completed successfully" if benchmark_success else "EC2 benchmark workflow failed"
            }
            
            # If benchmark was successful and we have S3 results, merge them into the main result
            if benchmark_success and s3_results:
                # Merge S3 results into the main result to match local benchmark format
                result.update(s3_results)
                logger.info("✅ Merged S3 results into main result for job data update")
            elif benchmark_success and not s3_results:
                logger.warning("⚠️ Benchmark succeeded but no S3 results available")
            elif not benchmark_success:
                logger.info("ℹ️ Benchmark failed, skipping S3 results merge")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ EC2 benchmark workflow failed: {e}")
            raise
        finally:
            # Cleanup
            self.cleanup()
    
    # cleanup the resources used
    def cleanup(self):
        """Clean up resources after workflow completion."""
        try:
            # Clean up security groups
            instance_id = self.instance_manager.get_instance_id()
            if instance_id:
                self.security_group_manager.cleanup_security_groups(instance_id)
            
            # Terminate instance
            self.instance_manager.terminate_instance()
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

# main function to run the EC2 benchmark workflow
def run_ec2_benchmark_workflow(config: Dict[str, Any], workflow_timestamp: str = None, deploy_result: Dict[str, Any] = None) -> Dict[str, Any]:
    """Main function to run the EC2 benchmark workflow using the orchestrator."""
    logger.info("🚀 Starting EC2 benchmark workflow...")
    
    orchestrator = EC2WorkflowOrchestrator(config, workflow_timestamp)
    try:
        result = orchestrator.run_workflow(deploy_result)
        return result
    finally:
        # Cleanup is handled in run_workflow
        pass
