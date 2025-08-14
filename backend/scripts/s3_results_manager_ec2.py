# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import boto3
import json
import logging
from typing import Dict, Any
from constants import Status, ResultFields, ConfigFields, AWSConfig

# used to log info to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S3 results manager class for ec2 benchmark
class S3ResultsManager:
    """Manages S3 results download and processing for EC2 benchmarks."""
    
    def __init__(self, session: boto3.Session):
        self.session = session
        self.s3_client = session.client('s3')
        self.region = session.region_name or AWSConfig.DEFAULT_REGION
    
    # download and process the S3 results
    def download_and_process_s3_results(self, config: Dict[str, Any], workflow_timestamp: str) -> Dict[str, Any]:
        """Download S3 results and format them."""
        try:
            bucket_name = config.get(ConfigFields.S3_BUCKET)
            
            if not bucket_name or not workflow_timestamp:
                logger.warning("⚠️ Missing S3 bucket or workflow timestamp for results download")
                return {}
            
            # Download benchmark-results.json
            results_s3_key = f"{workflow_timestamp}/benchmark/benchmark-results.json"
            output_s3_key = f"{workflow_timestamp}/benchmark/benchmark-output.txt"
            
            # Get results metadata
            try:
                response = self.s3_client.get_object(Bucket=bucket_name, Key=results_s3_key)
                results_metadata = json.loads(response['Body'].read().decode('utf-8'))
                logger.info(f"✅ Downloaded results metadata from S3: {results_s3_key}")
            except Exception as e:
                logger.error(f"❌ Failed to download results metadata: {e}")
                return {}
            
            # Get benchmark output
            try:
                response = self.s3_client.get_object(Bucket=bucket_name, Key=output_s3_key)
                benchmark_output = response['Body'].read().decode('utf-8')
                logger.info(f"✅ Downloaded benchmark output from S3: {output_s3_key}")
            except Exception as e:
                logger.error(f"❌ Failed to download benchmark output: {e}")
                benchmark_output = "Benchmark output not available"
            
            # Extract command from output (first line after "Command: ")
            command = "Unknown command"
            if "Command: " in benchmark_output:
                command_line = benchmark_output.split("Command: ")[1].split("\n")[0]
                command = command_line.strip()
            
            # Extract stdout and stderr from output
            stdout = benchmark_output
            stderr = ""
            if "STDOUT:\n" in benchmark_output and "STDERR:\n" in benchmark_output:
                parts = benchmark_output.split("STDOUT:\n")
                if len(parts) > 1:
                    stdout_part = parts[1].split("STDERR:\n")[0] if "STDERR:\n" in parts[1] else parts[1]
                    stdout = stdout_part.strip()
                    if "STDERR:\n" in parts[1]:
                        stderr = parts[1].split("STDERR:\n")[1].strip()
            
            # Extract results table content
            results_file_content = ""
            if "=== BENCHMARK RESULTS TABLE ===" in benchmark_output:
                results_start = benchmark_output.find("=== BENCHMARK RESULTS TABLE ===")
                results_content = benchmark_output[results_start:]
                results_file_content = results_content.strip()
            
            # Format results
            s3_results = {
                ResultFields.STATUS: Status.SUCCESS,
                ResultFields.BENCHMARK_ID: results_metadata.get(ResultFields.BENCHMARK_ID, "ec2_benchmark"),
                ResultFields.RESULTS_LOCATION: f"s3://{bucket_name}/{results_s3_key}",
                ResultFields.OUTPUT: benchmark_output,
                ResultFields.STDOUT: stdout,
                ResultFields.STDERR: stderr,
                ResultFields.COMMAND: command,
                ResultFields.TASK_STARTED_AT: results_metadata.get("task_started_at", ""),
                ResultFields.TASK_COMPLETED_AT: results_metadata.get("task_completed_at", ""),
                ResultFields.RESULTS_FILE_CONTENT: results_file_content,
                ResultFields.RESULTS_S3_URI: f"s3://{bucket_name}/{results_s3_key}",
                ResultFields.RESULTS_HTTPS_URL: f"https://{bucket_name}.s3.{self.region}.amazonaws.com/{results_s3_key}",
                ResultFields.RESULTS_S3_KEY: results_s3_key,
                ResultFields.MESSAGE: "EC2 benchmark completed successfully with S3 upload",
                ResultFields.OUTPUT_S3_INFO: {
                    ResultFields.S3_URI: f"s3://{bucket_name}/{output_s3_key}",
                    ResultFields.HTTPS_URL: f"https://{bucket_name}.s3.{self.region}.amazonaws.com/{output_s3_key}",
                    ResultFields.BUCKET_NAME: bucket_name,
                    ResultFields.S3_KEY: output_s3_key,
                    ResultFields.FILE_SIZE: len(benchmark_output.encode('utf-8')),
                    ResultFields.TIMESTAMP: workflow_timestamp
                }
            }
            
            return s3_results
        
        except Exception as e:
            logger.error(f"❌ Error downloading S3 results: {e}")
            return {}
    
    # check if the S3 results exist
    def check_s3_results_exist(self, bucket_name: str, workflow_timestamp: str) -> bool:
        """Check if S3 results exist for the given workflow."""
        try:
            results_s3_key = f"{workflow_timestamp}/benchmark/benchmark-results.json"
            
            # Try to head the object to check if it exists
            self.s3_client.head_object(Bucket=bucket_name, Key=results_s3_key)
            logger.info(f"✅ S3 results found: s3://{bucket_name}/{results_s3_key}")
            return True
            
        except Exception as e:
            logger.info(f"ℹ️ S3 results not found: {e}")
            return False
    
    # get the summary of the S3 results
    def get_s3_results_summary(self, bucket_name: str, workflow_timestamp: str) -> Dict[str, Any]:
        """Get a summary of S3 results without downloading the full content."""
        try:
            results_s3_key = f"{workflow_timestamp}/benchmark/benchmark-results.json"
            output_s3_key = f"{workflow_timestamp}/benchmark/benchmark-output.txt"
            
            # Get metadata for both files
            summary = {
                ResultFields.WORKFLOW_TIMESTAMP: workflow_timestamp,
                ResultFields.BUCKET_NAME: bucket_name,
                ResultFields.RESULTS_KEY: results_s3_key,
                ResultFields.OUTPUT_KEY: output_s3_key,
                ResultFields.RESULTS_EXIST: False,
                ResultFields.OUTPUT_EXIST: False
            }
            
            # Check if results file exists
            try:
                response = self.s3_client.head_object(Bucket=bucket_name, Key=results_s3_key)
                summary[ResultFields.RESULTS_EXIST] = True
                summary[ResultFields.RESULTS_SIZE] = response.get('ContentLength', 0)
                summary[ResultFields.RESULTS_LAST_MODIFIED] = response.get('LastModified', '').isoformat()
            except Exception:
                pass
            
            # Check if output file exists
            try:
                response = self.s3_client.head_object(Bucket=bucket_name, Key=output_s3_key)
                summary[ResultFields.OUTPUT_EXIST] = True
                summary[ResultFields.OUTPUT_SIZE] = response.get('ContentLength', 0)
                summary[ResultFields.OUTPUT_LAST_MODIFIED] = response.get('LastModified', '').isoformat()
            except Exception:
                pass
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting S3 results summary: {e}")
            return {}
