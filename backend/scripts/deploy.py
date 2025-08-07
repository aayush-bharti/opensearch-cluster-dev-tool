# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import subprocess
import os
import tempfile
import logging
import shutil
import json
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from datetime import datetime
from scripts.s3_upload import S3Uploader
from constants import Status, ResultFields, TaskTypes, ConfigFields, ErrorMessages

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenSearchDeployer:
    """OpenSearch deployer that automatically uses AWS credentials from ~/.aws/credentials"""
    
    def __init__(self, workflow_timestamp: str = None, config: Dict[str, Any] = None):
        self.temp_dir = tempfile.mkdtemp()
        self.workflow_timestamp = workflow_timestamp
        self.config = config or {}

        self.validate_aws_credentials()

        # Initialize AWS session
        self.session = boto3.Session()
        self.region = self.session.region_name or 'us-east-1'

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
    
    # create the CDK context file
    def create_cdk_context(self, config: Dict[str, Any]) -> str:
        """Create CDK context file with deployment configuration."""
        context_file = os.path.join(self.temp_dir, "cdk-context.json")
        
        distribution_url = config.get("distribution_url", "")
        logger.info(f"📦 Using distribution URL: {distribution_url}")
        
        # Base configuration - only include if provided
        base_config = {
            "distributionUrl": distribution_url,
            "suffix": config.get(ConfigFields.SUFFIX, ""),
            "securityDisabled": config.get(ConfigFields.SECURITY_DISABLED),
            "cpuArch": config.get(ConfigFields.CPU_ARCH),
            "singleNodeCluster": config.get(ConfigFields.SINGLE_NODE_CLUSTER),
            "dataInstanceType": config.get(ConfigFields.DATA_INSTANCE_TYPE),
            "dataNodeCount": config.get(ConfigFields.DATA_NODE_COUNT),
            "distVersion": config.get(ConfigFields.DIST_VERSION),
            "minDistribution": config.get(ConfigFields.MIN_DISTRIBUTION),
            "serverAccessType": config.get(ConfigFields.SERVER_ACCESS_TYPE),
            "restrictServerAccessTo": config.get(ConfigFields.RESTRICT_SERVER_ACCESS_TO),
            "use50PercentHeap": config.get(ConfigFields.USE_50_PERCENT_HEAP),
            "isInternal": config.get(ConfigFields.IS_INTERNAL),
        }
        
        # Only add non-None base parameters to context
        context = {}
        for key, value in base_config.items():
            if value is not None:
                context[key] = value
                logger.info(f"📝 Added base parameter: {key} = {value}")
        
        # Add admin password if provided (needed when security is enabled)
        admin_password = config.get(ConfigFields.ADMIN_PASSWORD)
        if admin_password is not None:
            context["adminPassword"] = admin_password
            logger.info(f"📝 Added admin password parameter")
        
        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2)
        
        logger.info(f"📝 CDK context saved to {context_file}")
        return context_file
    
    # clone the CDK repository and install dependencies
    def clone_cdk_repo(self) -> bool:
        """Clone CDK repository and install dependencies."""
        # cdk_dir = "opensearch-cluster-cdk-test"
        cdk_dir = "opensearch-cluster-cdk"
        
        # Always validate the directory thoroughly
        if os.path.exists(cdk_dir):
            logger.info(f"Directory {cdk_dir} exists, validating...")
            
            # Check if it's actually a directory
            if not os.path.isdir(cdk_dir):
                logger.warning(f"⚠️ Path {cdk_dir} exists but is not a directory. Removing...")
                os.remove(cdk_dir)
            else:
                # Check for key files that indicate a valid CDK repo
                has_git = os.path.exists(os.path.join(cdk_dir, ".git"))
                has_package_json = os.path.exists(os.path.join(cdk_dir, "package.json"))
                has_cdk_json = os.path.exists(os.path.join(cdk_dir, "cdk.json"))
                dir_contents = os.listdir(cdk_dir) if os.path.isdir(cdk_dir) else []
                
                logger.info(f"Directory validation - .git: {has_git}, package.json: {has_package_json}, cdk.json: {has_cdk_json}")
                logger.info(f"Directory contents: {dir_contents}")
                
                # Only proceed if we have a valid git repo with CDK files
                if has_git and (has_package_json or has_cdk_json):
                    logger.info("📁 CDK repository already exists and appears valid")
                    # Pull latest changes before npm install
                    try:
                        logger.info("🔄 Pulling latest changes in CDK repo...")
                        subprocess.run(["git", "pull", "--no-rebase", "origin", "main"], cwd=cdk_dir, check=True)
                        logger.info("✅ Pulled latest changes in CDK repo")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to pull latest changes: {e}")
                    # Continue to npm install
                else:
                    logger.warning(f"⚠️ Directory {cdk_dir} exists but appears corrupted. Removing and re-cloning...")
                    import shutil
                    try:
                        shutil.rmtree(cdk_dir)
                        logger.info(f"Removed corrupted directory: {cdk_dir}")
                    except Exception as e:
                        logger.error(f"Failed to remove corrupted directory: {e}")
                        raise Exception(f"Cannot remove corrupted CDK directory: {e}")
        
        # Clone repository if it doesn't exist or was removed
        if not os.path.exists(cdk_dir):
            logger.info("📦 Cloning opensearch-cluster-cdk repository...")
            try:
                result = subprocess.run([
                    "git", "clone",
                    "https://github.com/opensearch-project/opensearch-cluster-cdk.git",
                    cdk_dir
                ], capture_output=True, text=True, timeout=120)
                
                logger.info(f"Git clone stdout: {result.stdout}")
                if result.stderr:
                    logger.info(f"Git clone stderr: {result.stderr}")
                
                if result.returncode != 0:
                    logger.error(f"Git clone failed with return code {result.returncode}")
                    raise Exception(f"Failed to clone CDK repository: {result.stderr}")
                    
                logger.info("✅ CDK repository cloned successfully")
                
                # Verify the clone was successful
                if not os.path.exists(os.path.join(cdk_dir, "package.json")) and not os.path.exists(os.path.join(cdk_dir, "cdk.json")):
                    logger.error(f"CDK repository clone appears incomplete")
                    raise Exception("CDK repository clone appears incomplete - missing key files")
                    
            except subprocess.TimeoutExpired:
                logger.error("❌ Git clone timed out")
                raise Exception("Git clone operation timed out")
            except Exception as e:
                logger.error(f"❌ Failed to clone CDK repository: {e}")
                raise
        
        # Change to CDK directory and install dependencies
        original_cwd = os.getcwd()
        try:
            logger.info(f"Changing to CDK directory: {cdk_dir}")
            if not os.path.exists(cdk_dir):
                raise Exception(f"CDK directory {cdk_dir} does not exist after clone attempt")
            os.chdir(cdk_dir)
            
            # Install npm dependencies in the CDK directory
            logger.info("Installing npm dependencies in CDK directory...")
            logger.info("This may take several minutes on the first run...")
            
            # Clear npm cache first to avoid potential issues
            logger.info("Clearing npm cache...")
            try:
                subprocess.run(["npm", "cache", "clean", "--force"], 
                             capture_output=True, text=True, timeout=60)
            except:
                logger.warning("Failed to clear npm cache, but continuing...")
            
            # Try npm install with better error handling
            try:
                npm_install_result = subprocess.run(
                    ["npm", "install", "--verbose"],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout for npm install (can be slow on first run)
                )
                    
                if npm_install_result.returncode != 0:
                    logger.error(f"npm install failed with return code {npm_install_result.returncode}")
                    logger.error(f"npm install stderr: {npm_install_result.stderr}")
                    logger.error(f"npm install stdout: {npm_install_result.stdout}")
                    
                    # Try alternative npm install approach
                    logger.info("Trying npm install with --force flag...")
                    npm_install_result = subprocess.run(
                        ["npm", "install", "--force"],
                        capture_output=True,
                        text=True,
                        timeout=600
                    )
                    
                    if npm_install_result.returncode != 0:
                        raise Exception(f"npm install failed even with --force: {npm_install_result.stderr}")
                
                logger.info("npm install completed successfully")
                
            except subprocess.TimeoutExpired:
                logger.error("npm install timed out after 10 minutes")
                raise Exception("npm install timed out. This could be due to slow network or large dependencies.")
            
            # Check if CDK is available (don't install globally to avoid permission issues)
            logger.info("Installing AWS CDK globally...")
            try:
                npm_install_result2 = subprocess.run(
                    ["npm", "install", "-g", "aws-cdk"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout for global CDK install
                )

                if npm_install_result2.returncode != 0:
                    logger.error(f"Global CDK install failed: {npm_install_result2.stderr}")
                    logger.warning("Global CDK install failed, but proceeding as CDK might already be available")
                else:
                    logger.info("Global CDK install completed successfully")
                    
            except subprocess.TimeoutExpired:
                logger.warning("Global CDK install timed out, but proceeding as CDK might already be available")
            return True
    
        finally:
            # Always return to original directory
            os.chdir(original_cwd)

    def add_custom_parameters(self, cmd: list, custom_params: list) -> list:
        """Add custom parameters to a CDK command."""
        if not custom_params:
            return cmd
            
        logger.info(f"Adding custom deploy parameters: {custom_params}")
        for param in custom_params:
            if param.get("value") and param["value"].strip():
                param_value = param["value"].strip()

                # Check if the parameter is already in the command
                if not any(param_value in arg for arg in cmd):
                    # Add the parameter to the command
                    if not param_value.startswith("-c"):
                        cmd.extend(["-c", param_value])
                        logger.info(f"📝 Added parameter: {param_value}")
                    else:
                        cmd.append(param_value)
                        logger.info(f"📝 Added parameter: {param_value}")
                else:
                    logger.info(f"📝 Parameter already in command: {param_value}")
        
        return cmd

    # run the CDK bootstrap
    def run_cdk_bootstrap(self, context_file: str) -> bool:
        """Run CDK bootstrap to prepare AWS environment."""

        original_cwd = os.getcwd()
            
        try:
            # cdk_dir = "opensearch-cluster-cdk-test"
            cdk_dir = "opensearch-cluster-cdk"
            if not os.path.exists(cdk_dir):
                raise Exception(f"CDK directory {cdk_dir} not found. Repository should have been cloned already.")
            
            # Change to the CDK directory
            logger.info(f"Changing directory to: {cdk_dir}")
            os.chdir(cdk_dir)

            logger.info("🔧 Running CDK bootstrap...")
            
            # Read context file and convert to CDK context arguments
            with open(context_file, 'r') as f:
                context_data = json.load(f)
            
            # Build context arguments for CDK command
            context_args = []
            for key, value in context_data.items():
                if value is not None:  # Only add non-null values
                    # Convert Python booleans to lowercase strings that CDK expects
                    if isinstance(value, bool):
                        str_value = str(value).lower()
                    else:
                        str_value = str(value)
                    context_args.extend(["-c", f"{key}={str_value}"])
            
            bootstrap_cmd = ["cdk", "bootstrap"] + context_args

            # Add custom deploy parameters if provided
            custom_params = self.config.get(ConfigFields.CUSTOM_DEPLOY_PARAMS, [])
            bootstrap_cmd = self.add_custom_parameters(bootstrap_cmd, custom_params)

            logger.info(f"Running bootstrap command: {' '.join(bootstrap_cmd)}")
            
            result = subprocess.run(
                bootstrap_cmd,
                cwd=".",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ CDK bootstrap completed successfully")
                return True
            else:
                logger.error(f"❌ CDK bootstrap failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ CDK bootstrap timed out")
            return False
        except Exception as e:
            logger.error(f"❌ CDK bootstrap error: {e}")
            return False
        finally:
            # Always return to original directory
            os.chdir(original_cwd)
            logger.info(f"Returned to original directory: {original_cwd}")
    
    # run the CDK deploy
    def run_cdk_deploy(self, context_file: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run CDK deploy to create the OpenSearch cluster."""
        original_cwd = os.getcwd()
            
        try:
            cdk_dir = "opensearch-cluster-cdk"
            if not os.path.exists(cdk_dir):
                raise Exception(f"CDK directory {cdk_dir} not found. Repository should have been cloned already.")
            
            # Change to the CDK directory
            logger.info(f"Changing directory to: {cdk_dir}")
            os.chdir(cdk_dir)

            # Set environment variables
            os.environ["SUFFIX"] = config.get(ConfigFields.SUFFIX, "")
            logger.info(f"🔧 Setting SUFFIX environment variable: {config.get(ConfigFields.SUFFIX, '')}")
            
            # Read context file and convert to CDK context arguments
            with open(context_file, 'r') as f:
                context_data = json.load(f)
            
            # Build CDK context arguments
            context_args = []
            for key, value in context_data.items():
                if value is not None:  # Only add non-null values
                    # Convert Python booleans to lowercase strings that CDK expects
                    if isinstance(value, bool):
                        str_value = str(value).lower()
                    else:
                        str_value = str(value)
                    context_args.extend(["-c", f"{key}={str_value}"])
            
            logger.info("🚀 Running CDK deploy...")
            
            deploy_cmd = [
                "cdk", "deploy", "*",
                "--require-approval", "never",
                "--verbose",
                "--rollback", "false"
            ] + context_args

            # Add custom deploy parameters if provided
            custom_params = self.config.get(ConfigFields.CUSTOM_DEPLOY_PARAMS, [])
            deploy_cmd = self.add_custom_parameters(deploy_cmd, custom_params)
            
            logger.info(f"Running deploy command: {' '.join(deploy_cmd)}")
            result = subprocess.run(
                deploy_cmd,
                cwd=".",
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            logger.info(f"CDK Deploy STDOUT:\n{result.stdout}")
            if result.stderr:
                logger.info(f"CDK Deploy STDERR:\n{result.stderr}")
            
            if result.returncode != 0:
                logger.error(f"❌ CDK deploy failed with return code: {result.returncode}")
                return {
                    "status": "error",
                    "message": f"CDK deploy failed with return code: {result.returncode}",
                    "output": result.stdout,
                    "error_output": result.stderr,
                    "full_output": f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
                }
            
            logger.info("✅ CDK deploy completed successfully")
            
            # Upload output to S3
            logger.info("📤 Uploading deploy output to S3...")
            deploy_command = " ".join(deploy_cmd)
            deploy_output = result.stdout
            deploy_stderr = result.stderr or ""
            
            bucket_name = self.config.get(ConfigFields.S3_BUCKET, "")
            if not bucket_name or bucket_name.strip() == "":
                logger.warning("⚠️ S3 bucket not found in config")
            
            logger.info(f"📤 Using S3 bucket: {bucket_name}")
            # upload the output to S3
            uploader = S3Uploader(bucket_name=bucket_name, workflow_timestamp=self.workflow_timestamp)
            output_s3_info = uploader.upload_output_txt(
                TaskTypes.DEPLOY, 
                deploy_output, 
                deploy_stderr, 
                deploy_command
            )
            
            # Parse output to extract cluster information
            combined_output = f"{result.stdout}\n{result.stderr}"
            cluster_info = self.parse_deploy_output(combined_output, config.get(ConfigFields.SUFFIX, ""))
            
            deploy_result = {
                ResultFields.STATUS: Status.SUCCESS,
                ResultFields.MESSAGE: "OpenSearch cluster deployed successfully",
                ResultFields.CLUSTER_INFO: cluster_info,
                ResultFields.OUTPUT: result.stdout,
                "full_output": combined_output,
                "command": deploy_command
            }
            
            # Add output to S3 info to deploy result
            if output_s3_info:
                deploy_result["output_s3_info"] = output_s3_info
                logger.info("✅ Deploy command and output uploaded to S3")
            else:
                logger.warning("⚠️ Deploy command and output upload failed")
            
            return deploy_result
            
        except subprocess.TimeoutExpired:
            logger.error("❌ CDK deploy timed out")
            raise Exception("CDK deploy timed out after 30 minutes")
        except Exception as e:
            logger.error(f"❌ Error during CDK deploy: {e}")
            raise
        finally:
            # Always return to original directory
            os.chdir(original_cwd)
            logger.info(f"Returned to original directory: {original_cwd}")
            
    # parse the CDK deploy output
    def parse_deploy_output(self, output: str, suffix: str) -> Dict[str, Any]:
        """Parse CDK deploy output to extract cluster information."""
        cluster_info = {
            "cluster_endpoint": None,
            "stack_name": None,
            "deployment_time": None,
            "total_time": None
        }
        
        logger.info(f"🔍 Parsing CDK output for suffix: {suffix}")
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for loadbalancerurl in stack output
            if ".loadbalancerurl" in line.lower() and "=" in line:
                logger.info(f"Found loadbalancerurl line: '{line}'")
                parts = line.split("=", 1)
                if len(parts) == 2:
                    cluster_info["cluster_endpoint"] = parts[1].strip()
                    logger.info(f"✅ Extracted cluster endpoint: {cluster_info['cluster_endpoint']}")
                    
                    # Extract stack name from the output key
                    stack_output_key = parts[0].strip()
                    if "." in stack_output_key:
                        cluster_info["stack_name"] = stack_output_key.split(".")[0]
                        logger.info(f"✅ Extracted stack name: {cluster_info['stack_name']}")
            
            # Look for other endpoint patterns
            elif any(term in line.lower() for term in ["cluster", "domain"]) and "endpoint" in line.lower() and "=" in line:
                logger.info(f"Found endpoint line: '{line}'")
                parts = line.split("=", 1)
                if len(parts) == 2:
                    cluster_info["cluster_endpoint"] = parts[1].strip()
                    logger.info(f"✅ Extracted cluster endpoint: {cluster_info['cluster_endpoint']}")
            
            # Extract timing information
            elif "Deployment time:" in line:
                time_part = line.split("Deployment time:", 1)
                if len(time_part) == 2:
                    cluster_info["deployment_time"] = time_part[1].strip()
                    logger.info(f"⏱️ Deployment time: {cluster_info['deployment_time']}")
            
            elif "Total time:" in line:
                time_part = line.split("Total time:", 1)
                if len(time_part) == 2:
                    cluster_info["total_time"] = time_part[1].strip()
                    logger.info(f"⏱️ Total time: {cluster_info['total_time']}")
        
        logger.info(f"📋 Final parsed cluster info: {cluster_info}")
        return cluster_info
    
    # get the AWS account ID
    def get_account_id(self) -> str:
        """Get AWS account ID."""
        try:
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            return identity.get('Account', '')
        except Exception:
            return "unknown"
    
    # upload the deploy results to S3
    def upload_deploy_results_to_s3(self, deploy_result: Dict[str, Any], config: Dict[str, Any], timestamp: str, timing_data: Dict[str, Any] = None) -> Dict[str, str]:
        """Save deploy results metadata to S3 in deploy-results folder."""
        try:
            bucket_name = self.config.get(ConfigFields.S3_BUCKET, "")
            if not bucket_name or bucket_name.strip() == "":
                logger.warning("⚠️ S3 bucket not found in config")
            
            logger.info(f"📤 Using S3 bucket: {bucket_name}")
            uploader = S3Uploader(bucket_name=bucket_name, workflow_timestamp=self.workflow_timestamp)
            
            # Create deploy results metadata
            deploy_metadata = {
                "deploy_status": deploy_result.get(ResultFields.STATUS),
                "deploy_message": deploy_result.get(ResultFields.MESSAGE),
                "config": config,
                ResultFields.CLUSTER_INFO: deploy_result.get(ResultFields.CLUSTER_INFO, {})
            }
            
            # Use the new upload method with timing data
            result = uploader.upload_task_results(TaskTypes.DEPLOY, deploy_metadata, timing_data)
            
            return {
                "results_s3_uri": result["s3_uri"],
                "results_https_url": result["https_url"],
                "results_s3_key": result["s3_key"],
                "timestamp": result["timestamp"],
                "file_size": result["file_size"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to upload deploy results to S3: {e}")
            return {}
    
    # cleanup the files and repositories
    def cleanup(self):
        """Clean up files and repositories."""
        try:
            shutil.rmtree(self.temp_dir)
            if os.path.exists("opensearch-cluster-cdk"):
                shutil.rmtree("opensearch-cluster-cdk")
            logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")

# run the deploy process
def run_deploy_process(config: Dict[str, Any], workflow_timestamp: str = None) -> Dict[str, Any]:
    """
    Deploy OpenSearch with the provided manifest using automatic AWS credentials.
    
    Args:
        config: Deploy configuration including S3 bucket
        workflow_timestamp: Shared timestamp for the workflow (optional)
    
    Returns:
        Dictionary containing deploy results including S3 upload info
    """
    logger.info("🚀 Starting OpenSearch deploy with auto AWS credentials...")
    
    # Capture start time
    task_started_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
    logger.info(f"📅 Task started at: {task_started_at}")
    
    # Generate timestamp for folder organization
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    deployer = OpenSearchDeployer(workflow_timestamp, config)
    try:
        # create the CDK context file
        context_file = deployer.create_cdk_context(config)
        
        # clone the CDK repository
        deployer.clone_cdk_repo()
        
        # run the CDK bootstrap with context
        if not deployer.run_cdk_bootstrap(context_file):
            raise Exception("CDK bootstrap failed")
        
        # run the CDK deploy with context
        result = deployer.run_cdk_deploy(context_file, config)
        
        # Capture completion time
        task_completed_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
        logger.info(f"📅 Task completed at: {task_completed_at}")
        
        # Create timing data for S3 upload
        timing_data = {
            "started_at": task_started_at,
            "completed_at": task_completed_at
        }
        # store timing data as instance variable for use in upload methods
        deployer.timing_data = timing_data
        
        # Upload deploy results metadata to S3
        if result.get(ResultFields.STATUS) == Status.SUCCESS:
            logger.info("☁️ Uploading deploy results to S3...")
            # use timing data from instance variable
            s3_results_info = deployer.upload_deploy_results_to_s3(result, config, timestamp, deployer.timing_data)
            if s3_results_info:
                result["s3_info"] = s3_results_info
                result[ResultFields.MESSAGE] = "OpenSearch cluster deployed successfully with S3 results upload"
                logger.info("✅ Deployment completed successfully with S3 upload")
            else:
                result[ResultFields.MESSAGE] = "OpenSearch cluster deployed successfully (S3 upload failed)"
                logger.warning("⚠️ Deployment completed but S3 upload failed")
        
        # Add timing information to deploy result
        result["task_started_at"] = task_started_at
        result["task_completed_at"] = task_completed_at
        
        return result
    finally:
        deployer.cleanup()
