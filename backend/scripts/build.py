# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import subprocess
import os
import tempfile
import logging
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from datetime import datetime
from scripts.s3_upload import S3Uploader
from constants import Status, ResultFields

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenSearchBuilder:
    """OpenSearch builder that automatically uses AWS credentials from ~/.aws/credentials"""
    
    def __init__(self, manifest_yml: str, workflow_timestamp: str = None, config: Dict[str, Any] = None):
        self.manifest_yml = manifest_yml
        self.workflow_timestamp = workflow_timestamp
        self.config = config or {}
        self.temp_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.temp_dir, "manifest.yml")
        
        # Validate AWS credentials are available
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
    
    # run the build process
    def run_build(self) -> Dict[str, Any]:
        """Run the OpenSearch build process"""
        try:
            # Capture start time
            task_started_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
            logger.info(f"📅 Task started at: {task_started_at}")
            
            # Clone opensearch-build repo if not present
            if not os.path.exists("opensearch-build"):
                logger.info("📦 Cloning opensearch-build repository (build)...")
                subprocess.run([
                    "git", "clone", "https://github.com/opensearch-project/opensearch-build.git"
                ], check=True)
                logger.info("✅ Repository cloned for Docker build")
            else:
                logger.info("📦 Pulling latest changes from opensearch-build repository (build)...")
                subprocess.run([
                    "git", "pull", "origin", "main"
                ], check=True, cwd="opensearch-build")
                logger.info("✅ Latest changes pulled for build")

            # Pull the correct Docker image for OpenSearch build
            docker_image = "opensearchstaging/ci-runner:ci-runner-al2-opensearch-build-v1"
            logger.info(f"🐳 Pulling Docker image: {docker_image}")
            subprocess.run([
                "docker", "pull", docker_image
            ], check=True)
            logger.info(f"✅ Pulled Docker image: {docker_image}")

            # Run the build inside a Docker container
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{os.path.abspath('opensearch-build')}:/opensearch-build",
                "-v", f"{os.path.abspath(self.manifest_path)}:/opensearch-build/manifest.yml",
                "-w", "/opensearch-build",
                "-e", "JAVA_HOME=/opt/java/openjdk-21",
                docker_image,
                "./build.sh", "/opensearch-build/manifest.yml",
                "-p", "linux",
                "-a", "arm64",
                "--continue-on-error",
                "-d", "tar",
                "-s"
            ]
            logger.info(f"🐳 Running build: {' '.join(docker_cmd)}")
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True
            )
            logger.info(f"🐳 Build stdout:\n{result.stdout}")
            if result.stderr:
                logger.warning(f"🐳 Build stderr:\n{result.stderr}")
            if result.returncode != 0:
                logger.error(f"❌ Build failed with code {result.returncode}")
                raise Exception(f"Build failed: {result.stderr}")

            # Extract build manifest path from build output
            build_manifest_path = None
            for line in result.stdout.split('\n'):
                if 'Created build manifest' in line:
                    build_manifest_path = line.split('Created build manifest')[1].strip()
                    logger.info(f"📝 Found build manifest: {build_manifest_path}")
                    break
            
            if not build_manifest_path:
                logger.error("❌ Could not find build manifest path in build output")
                logger.error("   Expected to find a line containing 'Created build manifest'")
                logger.error("   Build output:")
                logger.error(result.stdout)
                raise Exception("Could not find build manifest path in build output")

            # Run assemble.sh to create the tarball in a named container
            container_name = f"opensearch-assemble-{int(datetime.now().timestamp())}"
            assemble_cmd = [
                "docker", "run", "--name", container_name,
                "-v", f"{os.path.abspath('opensearch-build')}:/opensearch-build",
                "-w", "/opensearch-build",
                "-e", "JAVA_HOME=/opt/java/openjdk-21",
                docker_image,
                "./assemble.sh", build_manifest_path
            ]
            logger.info(f"🐳 Running assemble: {' '.join(assemble_cmd)}")
            assemble_result = subprocess.run(
                assemble_cmd,
                capture_output=True,
                text=True
            )
            logger.info(f"🐳 assemble stdout:\n{assemble_result.stdout}")
            if assemble_result.stderr:
                logger.warning(f"🐳 assemble stderr:\n{assemble_result.stderr}")
            if assemble_result.returncode != 0:
                logger.error(f"❌ assemble failed with code {assemble_result.returncode}")
                # Clean up container if it exists
                subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
                raise Exception(f"assemble failed: {assemble_result.stderr}")

            # Find the resulting tarball by parsing assemble output
            container_tarball_path = None
            for line in assemble_result.stdout.split('\n'):
                if 'Published' in line and '.tar.gz' in line:
                    container_tarball_path = line.split('Published')[1].strip().rstrip('.')
                    logger.info(f"📦 Found build artifact in container: {container_tarball_path}")
                    break

            if not container_tarball_path:
                logger.error("❌ Could not find build artifact in assemble output")
                logger.error("   Expected to find a line containing 'Published' and '.tar.gz'")
                logger.error("   Assemble output:")
                logger.error(assemble_result.stdout)
                # Clean up container if it exists
                subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
                raise Exception("Could not find build artifact (.tar.gz) in assemble output")

            # Copy the tarball from Docker container to host
            host_tarball_path = os.path.join(os.getcwd(), os.path.basename(container_tarball_path))
            docker_cp_cmd = ["docker", "cp", f"{container_name}:{container_tarball_path}", host_tarball_path]
            logger.info(f"📋 Copying artifact from container: {' '.join(docker_cp_cmd)}")
            cp_result = subprocess.run(docker_cp_cmd, capture_output=True, text=True)
            if cp_result.returncode != 0:
                logger.error(f"❌ Failed to copy artifact from container: {cp_result.stderr}")
                # Clean up container if it exists
                subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
                raise Exception(f"Failed to copy artifact from container: {cp_result.stderr}")
            logger.info(f"✅ Copied artifact to host: {host_tarball_path}")

            # Clean up the container
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

            # Capture completion time and create timing data
            task_completed_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
            logger.info(f"📅 Task completed at: {task_completed_at}")
            
            # Create timing data for S3 upload
            timing_data = {
                "started_at": task_started_at,
                "completed_at": task_completed_at
            }
            # Store timing data as instance variable for use in upload methods
            self.timing_data = timing_data

            # Upload the local copy to S3
            logger.info("☁️ Uploading to S3...")
            s3_info = self.upload_to_s3(host_tarball_path)

            tarball_path = host_tarball_path

            # Upload output to S3
            logger.info("📤 Uploading build command and output to S3...")
            build_command = " ".join(docker_cmd)
            assemble_command = " ".join(assemble_cmd)
            
            # Combine both build.sh and assemble.sh outputs
            build_output = result.stdout
            build_stderr = result.stderr or ""
            assemble_output = assemble_result.stdout
            assemble_stderr = assemble_result.stderr or ""
            
            # Create combined output with clear separation
            combined_output = f"=== BUILD.SH OUTPUT ===\n{build_output}\n"
            if build_stderr:
                combined_output += f"=== BUILD.SH STDERR ===\n{build_stderr}\n"
            combined_output += f"\n=== ASSEMBLE.SH OUTPUT ===\n{assemble_output}\n"
            if assemble_stderr:
                combined_output += f"=== ASSEMBLE.SH STDERR ===\n{assemble_stderr}\n"
            
            # Create combined command
            combined_command = f"# Build command:\n{build_command}\n\n# Assemble command:\n{assemble_command}"
            
            build_config = {"manifest_yml": self.manifest_yml}
            
            bucket_name = self.config.get("s3_bucket", "")
            if not bucket_name or bucket_name.strip() == "":
                logger.warning("⚠️ S3 bucket not found in config")
            
            logger.info(f"📤 Using S3 bucket: {bucket_name}")
            uploader = S3Uploader(bucket_name=bucket_name, workflow_timestamp=self.workflow_timestamp)
            output_s3_info = uploader.upload_output_txt(
                "build", 
                combined_output, 
                "",
                combined_command
            )
            
            # Prepare build result
            build_result = {
                ResultFields.STATUS: Status.SUCCESS,
                "message": "Build completed successfully with S3 upload",
                "tarball_path": tarball_path,
                "command": combined_command,
                "s3_info": s3_info,
                "output": combined_output
            }
            # Upload build results metadata to S31
            if s3_info:
                build_result["s3_info"] = s3_info
                timestamp = s3_info.get("timestamp")
                if timestamp:
                    logger.info("📝 Uploading build results metadata to S3...")
                    # Use timing data from instance variable
                    results_s3_info = self.upload_build_results_to_s3(build_result, timestamp, self.timing_data)
                    if results_s3_info:
                        build_result.update(results_s3_info)
                        logger.info("✅ Build results metadata uploaded successfully")
                logger.info("✅ Build completed successfully with S3 upload")
            else:
                build_result["message"] = "Build completed successfully (S3 upload failed)"
                logger.warning("⚠️ Build completed but S3 upload failed")
            
            # Add timing information to build result
            build_result["task_started_at"] = task_started_at
            build_result["task_completed_at"] = task_completed_at
            
            # Add output to S3 info to build result
            if output_s3_info:
                build_result["output_s3_info"] = output_s3_info
                logger.info("✅ Build command and output uploaded to S3")
            else:
                logger.warning("⚠️ Build command and output upload failed")
            
            return build_result
        except Exception as e:
            logger.error(f"❌ Build failed: {str(e)}")
            raise
    
    # save the manifest to a temporary file
    def save_manifest(self):
        """Save the manifest YAML to a temporary file."""
        with open(self.manifest_path, 'w') as f:
            f.write(self.manifest_yml)
        logger.info(f"📝 Manifest saved to {self.manifest_path}")
    
    # upload the manifest to S3
    def upload_manifest_to_s3(self):
        """Upload manifest to S3."""
        try:
            logger.info("📄 Starting manifest upload to S3...")
            bucket_name = self.config.get("s3_bucket", "")
            uploader = S3Uploader(bucket_name=bucket_name, workflow_timestamp=self.workflow_timestamp)
            result = uploader.upload_build_manifest(self.manifest_path)
            logger.info("✅ Manifest uploaded to S3 successfully")
            return result
        except Exception as e:
            logger.error(f"❌ Manifest upload failed: {e}")
            return {"error": str(e), "uploaded": False}
    
    # upload the tarball to S3
    def upload_to_s3(self, tarball_path: str) -> Dict[str, str]:
        """Upload tarball to S3 and return S3 info."""
        try:
            bucket_name = self.config.get("s3_bucket", "")
            uploader = S3Uploader(bucket_name=bucket_name, workflow_timestamp=self.workflow_timestamp)
            return uploader.upload_build_artifact(tarball_path)
        except Exception as e:
            logger.error(f"❌ S3 upload failed: {e}")
    
    # upload the build results to S3
    def upload_build_results_to_s3(self, build_result: Dict[str, Any], timestamp: str, timing_data: Dict[str, Any] = None) -> Dict[str, str]:
        """Save build results metadata to S3 in build-results folder."""
        try:
            bucket_name = self.config.get("s3_bucket", "")
            uploader = S3Uploader(bucket_name=bucket_name, workflow_timestamp=self.workflow_timestamp)
            
            # Create build results metadata
            build_metadata = {
                "build_status": build_result.get("status"),
                "build_message": build_result.get("message"),
                "build_manifest_path": build_result.get("build_manifest_path"),
                "tarball_path": build_result.get("tarball_path"),
                "s3_info": build_result.get("s3_info", {})
            }
            
            # Use the new upload method with timing data
            result = uploader.upload_build_results(build_metadata, timing_data)
            
            return {
                "results_s3_uri": result["s3_uri"],
                "results_https_url": result["https_url"],
                "results_s3_key": result["s3_key"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to upload build results to S3: {e}")
            return {}
    
    # cleanup the files and repositories
    def cleanup(self):
        """Clean up files and repositories."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            if os.path.exists("opensearch-build"):
                shutil.rmtree("opensearch-build")
            logger.info("🧹 Cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup failed: {str(e)}")

# run the build process
def run_build_process(config: Dict[str, Any], workflow_timestamp: str = None) -> Dict[str, Any]:
    """
    Build OpenSearch with the provided manifest using automatic AWS credentials.
    
    Args:
        config: Build configuration containing manifest_yml and S3 bucket
        workflow_timestamp: Shared timestamp for the workflow
    
    Returns:
        Dictionary containing build results including S3 upload info
    """
    logger.info("🚀 Starting OpenSearch build with auto AWS credentials...")
    
    # Extract manifest_yml from config
    manifest_yml = config.get("manifest_yml")
    if not manifest_yml:
        raise ValueError("manifest_yml is required in config")
    
    # Capture start time
    task_started_at = datetime.now().isoformat()
    logger.info(f"📅 Task started at: {task_started_at}")
    
    # initialize the builder
    builder = OpenSearchBuilder(manifest_yml, workflow_timestamp, config)
    
    try:
        # save the manifest to a temporary file
        builder.save_manifest()
        # upload the manifest to S3
        manifest_upload_result = builder.upload_manifest_to_s3()
        # run the build process
        build_result = builder.run_build()
        
        # Capture completion time
        task_completed_at = datetime.now().isoformat()
        logger.info(f"📅 Task completed at: {task_completed_at}")
        
        # Add timing information to build result
        build_result["task_started_at"] = task_started_at
        build_result["task_completed_at"] = task_completed_at
        
        # Add manifest upload info to build result
        if manifest_upload_result:
            build_result["manifest_s3_info"] = manifest_upload_result
            if not manifest_upload_result.get("uploaded", True):  # Check if upload failed
                logger.warning("⚠️ Manifest upload failed but continuing with build")
        
        return build_result
    finally:
        builder.cleanup()
