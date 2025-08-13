# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import subprocess
import os
import logging
import re
from datetime import datetime
from typing import Dict, Any
from scripts.s3_upload import S3Uploader
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from constants import Status, ResultFields, TaskTypes, ConfigFields, ErrorMessages
from scripts.aws_credentials_manager import AWSCredentialsManager

# used to log info to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  benchmarker class
class OpenSearchBenchmarker:
    # initialize the benchmarker class
    def __init__(self, config: Dict[str, Any], workflow_timestamp: str = None):
        self.config = config
        self.workflow_timestamp = workflow_timestamp
        self.benchmark_id = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Use shared AWS credentials manager to validate credentials
        self.aws = AWSCredentialsManager()
        self.aws.validate_aws_credentials()

        # Initialize AWS session/region from manager
        self.session = self.aws.get_session()
        self.region = self.aws.get_region()

    # make sure opensearch benchmark is installed, if not install it
    def setup_opensearch_benchmark(self):
        """make sure opensearch-benchmark is installed"""
        try:
            logger.info("Checking if opensearch-benchmark is installed...")
            # Remove check=True so we can handle the error manually
            result = subprocess.run(["opensearch-benchmark", "--version"], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Successfully found opensearch-benchmark
                logger.info(f"opensearch-benchmark version: {result.stdout.strip()}")
            else:
                # opensearch-benchmark is not installed, install it
                logger.info("opensearch-benchmark is not installed. Installing...")
                install_result = subprocess.run(
                    ["pip", "install", "opensearch-benchmark"], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                logger.info(f"opensearch-benchmark installed: {install_result.stdout.strip()}")
                
                # Verify installation
                verify_result = subprocess.run(["opensearch-benchmark", "--version"], capture_output=True, text=True)
                if verify_result.returncode == 0:
                    logger.info(f"✅ Installation verified. Version: {verify_result.stdout.strip()}")
                else:
                    raise Exception("Installation completed but opensearch-benchmark is still not accessible")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install opensearch-benchmark: {e.stderr}")
            raise Exception(f"Failed to install opensearch-benchmark: {e.stderr}")
        except FileNotFoundError:
            # opensearch-benchmark command not found, try to install
            logger.info("opensearch-benchmark command not found. Installing...")
            try:
                install_result = subprocess.run(
                    ["pip", "install", "opensearch-benchmark"], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                logger.info(f"opensearch-benchmark installed: {install_result.stdout.strip()}")
                
                # Verify installation
                verify_result = subprocess.run(["opensearch-benchmark", "--version"], capture_output=True, text=True)
                if verify_result.returncode == 0:
                    logger.info(f"✅ Installation verified. Version: {verify_result.stdout.strip()}")
                else:
                    raise Exception("Installation completed but opensearch-benchmark is still not accessible")
            except subprocess.CalledProcessError as install_error:
                logger.error(f"Failed to install opensearch-benchmark: {install_error.stderr}")
                raise Exception(f"Failed to install opensearch-benchmark: {install_error.stderr}")

    
    # run the benchmark
    def run_benchmark(self):
        """Run the OpenSearch benchmark with proper error detection."""
        try:
            logger.info("Starting benchmark process...")
            
            # Capture start time
            task_started_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
            self.task_started_at = task_started_at
            logger.info(f"📅 Task started at: {task_started_at}")
            
            # Validate required config fields
            if not self.config.get(ConfigFields.WORKLOAD_TYPE):
                raise ValueError("workload_type is required in config")
            if not self.config.get(ConfigFields.CLUSTER_ENDPOINT):
                raise ValueError("cluster_endpoint is required in config")
            
            # Ensure values are strings
            workload_type = str(self.config[ConfigFields.WORKLOAD_TYPE]).strip()
            cluster_endpoint = str(self.config[ConfigFields.CLUSTER_ENDPOINT]).strip()
            
            if not workload_type:
                raise ValueError("workload_type cannot be empty")
            if not cluster_endpoint:
                raise ValueError("cluster_endpoint cannot be empty")
            
            # json file to store the benchmark results and upload to s3
            json_results_path = f"/tmp/benchmark_results_{self.benchmark_id}.json"
            
            # Get pipeline from config, default to "benchmark-only" if not provided
            pipeline = self.config.get(ConfigFields.PIPELINE, "benchmark-only")
            
            benchmark_cmd = [
                "opensearch-benchmark",
                "execute-test",
                "--pipeline", pipeline,
                "--workload", workload_type,
                "--target-host", cluster_endpoint + ":80", 
                "--results-file", json_results_path
            ]
            
            # Add custom benchmark parameters if provided
            custom_params = self.config.get(ConfigFields.CUSTOM_BENCHMARK_PARAMS, [])
            if custom_params:
                logger.info(f"🔧 Adding custom benchmark parameters: {custom_params}")
                for param in custom_params:
                    if param.get("value") and param["value"].strip():
                        param_value = param["value"].strip()
                        benchmark_cmd.append(param_value)
                        logger.info(f"📝 Added parameter: {param_value}")

            logger.info(f"Running benchmark command: {' '.join(benchmark_cmd)}")
            
            # Use Popen for better control over the process
            process = subprocess.Popen(
                benchmark_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for process to complete with timeout
            try:
                stdout, stderr = process.communicate(timeout=3600)  # 1 hour timeout
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                logger.error("🚫 Benchmark timed out after 1 hour")
                process.kill()
                stdout, stderr = process.communicate()
                raise Exception("Benchmark timed out after 1 hour")
            
            # Check if process was terminated by signal
            if return_code < 0:
                signal_num = -return_code
                signal_name = {
                    2: "SIGINT (Ctrl+C)",
                    15: "SIGTERM", 
                    9: "SIGKILL"
                }.get(signal_num, f"signal {signal_num}")
                logger.error(f"🚫 Benchmark was terminated by {signal_name}")
                raise Exception(f"Benchmark was interrupted by {signal_name}")
            
            # Check normal exit code
            if return_code != 0:
                logger.error(f"🚫 Benchmark failed with exit code {return_code}")
                error_output = ""
                if stdout:
                    error_output += "=== STDOUT ===\n" + stdout
                if stderr:
                    error_output += "\n=== STDERR ===\n" + stderr
                raise Exception(f"Benchmark failed (exit code {return_code}):\n{error_output}")
            
            logger.info(f"Benchmark STDOUT:\n{stdout}")
            if stderr:
                logger.info(f"Benchmark STDERR:\n{stderr}")

            logger.info("Benchmark process completed successfully")
            
            # Capture completion time
            task_completed_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
            self.task_completed_at = task_completed_at
            logger.info(f"📅 Task completed at: {task_completed_at}")
            
            # Create timing data for S3 upload
            timing_data = {
                "started_at": task_started_at,
                "completed_at": task_completed_at
            }
            # Store timing data as instance variable for use in upload methods
            self.timing_data = timing_data
            
            # Read results file content for inclusion in output
            results_file_content = None
            if os.path.exists(json_results_path):
                try:
                    with open(json_results_path, 'r') as f:
                        results_file_content = f.read()
                    logger.info(f"✅ Successfully read results file content ({len(results_file_content)} characters)")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to read results file: {e}")
            
            # Create benchmark output
            benchmark_command = " ".join(benchmark_cmd)
            benchmark_output = stdout
            if results_file_content:
                benchmark_output += f"\n\n=== BENCHMARK RESULTS TABLE ===\n{results_file_content}"
            
            # Create benchmark result first
            benchmark_result = {
                ResultFields.STATUS: Status.SUCCESS,
                ResultFields.BENCHMARK_ID: self.benchmark_id,
                # ResultFields.RESULTS_LOCATION: f"local://benchmark_results/{self.benchmark_id}",
                ResultFields.RESULTS_LOCATION: f"s3://{self.config.get(ConfigFields.S3_BUCKET, '')}/{self.workflow_timestamp}/benchmark/benchmark-results.json",
                ResultFields.OUTPUT: benchmark_output,
                ResultFields.STDOUT: stdout,
                ResultFields.STDERR: stderr,
                ResultFields.COMMAND: " ".join(benchmark_cmd),
                ResultFields.TASK_STARTED_AT: task_started_at,
                ResultFields.TASK_COMPLETED_AT: task_completed_at,
                ResultFields.RESULTS_FILE_CONTENT: results_file_content
            }
            
            # Upload results file to S3
            results_s3_info = None
            if results_file_content and os.path.exists(json_results_path):
                logger.info(f"📄 Results file exists at: {json_results_path}")
                try:
                    # Upload using the standardized function
                    results_s3_info = self.upload_benchmark_results_to_s3(benchmark_result, self.timing_data)
                    logger.info(f"✅ Results uploaded to S3: {results_s3_info.get('results_s3_uri')}")
                    os.unlink(json_results_path)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to upload results to S3: {e}")
                    # Clean up the file even if upload fails
                    try:
                        os.unlink(json_results_path)
                    except:
                        pass
            elif not os.path.exists(json_results_path):
                logger.warning(f"⚠️ Results file does not exist at: {json_results_path}")
            
            # Update benchmark result with S3 information
            if results_s3_info:
                benchmark_result.update(results_s3_info)
                benchmark_result["results_location"] = results_s3_info.get('results_s3_uri')
                benchmark_result[ResultFields.MESSAGE] = "Benchmark completed successfully with S3 upload"
                logger.info("✅ Benchmark completed successfully with S3 upload")
            else:
                benchmark_result[ResultFields.MESSAGE] = "Benchmark completed successfully (S3 upload failed)"
                logger.warning("⚠️ Benchmark completed but S3 upload failed")
            
            # Upload output to S3
            logger.info("📤 Uploading benchmark command and output to S3...")
            
            benchmark_stderr = stderr or ""
            
            bucket_name = self.config.get(ConfigFields.S3_BUCKET, "")
            if not bucket_name or bucket_name.strip() == "":
                logger.warning("⚠️ S3 bucket not found in config")
            
            logger.info(f"📤 Using S3 bucket: {bucket_name}")
            uploader = S3Uploader(bucket_name=bucket_name, workflow_timestamp=self.workflow_timestamp)
            output_s3_info = uploader.upload_output_txt(
                TaskTypes.BENCHMARK, 
                benchmark_output, 
                benchmark_stderr, 
                benchmark_command
            )
            
            # Add command output S3 info to benchmark result
            if output_s3_info:
                benchmark_result["output_s3_info"] = output_s3_info
                logger.info("✅ Benchmark command and output uploaded to S3")
            else:
                logger.warning("⚠️ Benchmark command and output upload failed")
            
            return benchmark_result

        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise Exception(f"Configuration error: {e}")
        except Exception as e:
            logger.error(f"Benchmark execution error: {e}")
            raise Exception(f"Benchmark failed: {e}")

    # upload the benchmark results to s3 bucket
    def upload_benchmark_results_to_s3(self, benchmark_result: Dict[str, Any], timing_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Upload benchmark results metadata to S3 in benchmark-results folder."""
        try:
            bucket_name = self.config.get(ConfigFields.S3_BUCKET, "")
            uploader = S3Uploader(bucket_name=bucket_name, workflow_timestamp=self.workflow_timestamp)
            
            # Create benchmark results metadata
            benchmark_metadata = {
                ResultFields.BENCHMARK_STATUS: benchmark_result.get(ResultFields.STATUS),
                ResultFields.BENCHMARK_MESSAGE: benchmark_result.get(ResultFields.MESSAGE),
                ResultFields.BENCHMARK_ID: benchmark_result.get(ResultFields.BENCHMARK_ID),
                ResultFields.RESULTS_LOCATION: benchmark_result.get(ResultFields.RESULTS_LOCATION),
                ResultFields.CONFIG: {
                    **self.config,
                    "use_ec2_benchmark": False
                }
            }
            
            # Use the new upload method with timing data
            result = uploader.upload_task_results(TaskTypes.BENCHMARK, benchmark_metadata, timing_data)
            
            return {
                "results_s3_uri": result[ResultFields.S3_URI],
                "results_https_url": result[ResultFields.HTTPS_URL],
                "results_s3_key": result[ResultFields.S3_KEY]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to upload benchmark results to S3: {e}")
            return {}

    def format_benchmark_text_results(self, raw_content: str) -> Dict[str, Any]:
        """Format benchmark text results into a clean, readable format with metadata."""
        lines = raw_content.split('\n')
        
        # Extract basic execution info from the content
        execution_info = {}
        
        for line in lines:
            line_stripped = line.strip()
            
            # Extract key execution details
            if "SUCCESS" in line_stripped and "took" in line_stripped:
                time_match = re.search(r'took (\d+) seconds', line_stripped)
                if time_match:
                    execution_info["duration_seconds"] = int(time_match.group(1))
                execution_info["status"] = "SUCCESS"
                execution_info["execution_summary"] = line_stripped
                
            elif "Test Execution ID" in line_stripped:
                execution_id = line_stripped.split(":")[1].strip() if ":" in line_stripped else None
                if execution_id:
                    execution_info["test_execution_id"] = execution_id
        
        # Return simple, clean format with timing information
        formatted_results = {
            "benchmark_metadata": {
                ResultFields.BENCHMARK_ID: self.benchmark_id,
                ConfigFields.WORKLOAD_TYPE: self.config.get(ConfigFields.WORKLOAD_TYPE),
                ConfigFields.CLUSTER_ENDPOINT: self.config.get(ConfigFields.CLUSTER_ENDPOINT),
                ResultFields.EXECUTION_INFO: execution_info,
                ResultFields.CONTENT_LENGTH: len(raw_content),
                ResultFields.TASK_STARTED_AT: getattr(self, 'task_started_at', None),
                ResultFields.TASK_COMPLETED_AT: getattr(self, 'task_completed_at', None)
            },
        }
        
        return formatted_results

    # cleanup the resources used
    def cleanup(self):
        """Clean up temporary files."""
        pass 

# main function to run the process of benchmark
def run_benchmark_process(config: Dict[str, Any], workflow_timestamp: str = None) -> Dict[str, Any]:
    """Main function to run the benchmark process."""
    logger.info("🚀 Starting OpenSearch benchmark with direct S3 upload...")
    
    # initialize the benchmarker and run the benchmark
    benchmarker = OpenSearchBenchmarker(config, workflow_timestamp)
    try:
        benchmarker.setup_opensearch_benchmark()
        result = benchmarker.run_benchmark()
        
        return result
    finally:
        benchmarker.cleanup()
