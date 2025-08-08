# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import Dict, Any, Optional
from constants import ConfigFields

# used to log info to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# benchmark executor class
class BenchmarkExecutor:
    """Handles benchmark execution and user data script generation."""
    
    def __init__(self):
        pass
    
    # create the user data script
    def create_user_data_script(self, config: Dict[str, Any], aws_creds: Dict[str, str], 
                               local_timezone: str, workflow_timestamp: str, 
                               benchmark_id: str, task_started_at: str = None) -> str:
        """Create the user data script for the EC2 instance."""
        # Pre-process the configuration values to avoid f-string evaluation issues
        logger.info("🔍 Creating user data script...")
        logger.info(f"🔍 Config keys: {list(config.keys())}")
        
        try:
            cluster_endpoint = config[ConfigFields.CLUSTER_ENDPOINT]
            logger.info(f"✅ Got cluster_endpoint: {cluster_endpoint}")
        except Exception as e:
            logger.error(f"❌ Error getting cluster_endpoint: {e}")
            raise
            
        try:
            workload_type = config[ConfigFields.WORKLOAD_TYPE]
            logger.info(f"✅ Got workload_type: {workload_type}")
        except Exception as e:
            logger.error(f"❌ Error getting workload_type: {e}")
            raise
            
        try:
            pipeline = config.get(ConfigFields.PIPELINE, 'benchmark-only')
            logger.info(f"✅ Got pipeline: {pipeline}")
        except Exception as e:
            logger.error(f"❌ Error getting pipeline: {e}")
            raise
            
        try:
            custom_benchmark_params = json.dumps(config.get(ConfigFields.CUSTOM_BENCHMARK_PARAMS, []))
            logger.info(f"✅ Got custom_benchmark_params: {custom_benchmark_params}")
        except Exception as e:
            logger.error(f"❌ Error getting custom_benchmark_params: {e}")
            raise
            
        try:
            s3_bucket = config.get(ConfigFields.S3_BUCKET, 'osb-test-bucket-aayush')
            logger.info(f"✅ Got s3_bucket: {s3_bucket}")
        except Exception as e:
            logger.error(f"❌ Error getting s3_bucket: {e}")
            raise
            
        try:
            workflow_timestamp = workflow_timestamp or ''
            logger.info(f"✅ Got workflow_timestamp: {workflow_timestamp}")
        except Exception as e:
            logger.error(f"❌ Error getting workflow_timestamp: {e}")
            raise
            
        try:
            instance_type = config[ConfigFields.INSTANCE_TYPE]
            logger.info(f"✅ Got instance_type: {instance_type}")
        except Exception as e:
            logger.error(f"❌ Error getting instance_type: {e}")
            raise
        
        # create the Python script content separately to avoid f-string evaluation issues
        python_script = '''import subprocess
import json
import os
import sys
import boto3
from datetime import datetime

def log_progress(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print("✅ [" + timestamp + "] " + message)

def log_error(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print("❌ [" + timestamp + "] " + message)

def log_info(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print("ℹ️ [" + timestamp + "] " + message)

def run_benchmark():
    try:
        log_info("Starting benchmark execution...")
        with open('benchmark_config.json', 'r') as f:
            benchmark_config = json.load(f)
        log_info("Loaded configuration for workload: " + benchmark_config['workload_type'])
        
        # Set up AWS credentials for the Python script
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '/root/.aws/credentials'
        os.environ['AWS_CONFIG_FILE'] = '/root/.aws/config'
        
        # Also set environment variables as fallback
        os.environ['AWS_ACCESS_KEY_ID'] = benchmark_config.get('aws_access_key', '')
        os.environ['AWS_SECRET_ACCESS_KEY'] = benchmark_config.get('aws_secret_key', '')
        if benchmark_config.get('aws_token'):
            os.environ['AWS_SESSION_TOKEN'] = benchmark_config.get('aws_token', '')
        os.environ['AWS_DEFAULT_REGION'] = benchmark_config.get('aws_region', 'us-east-1')
        
        session = boto3.Session()
        
        # Check if credentials are available
        try:
            credentials = session.get_credentials()
            if credentials:
                log_info("AWS credentials found: " + credentials.access_key[:10] + "...")
            else:
                log_error("No AWS credentials found")
                return False
        except Exception as e:
            log_error("Error checking AWS credentials: " + str(e))
            return False
        
        benchmark_commands = [
            ["opensearch-benchmark"],
            ["python3", "-m", "opensearch_benchmark"],
            ["python3", "-m", "opensearch_benchmark.benchmark"]
        ]
        benchmark_cmd = None
        for cmd in benchmark_commands:
            try:
                result = subprocess.run(cmd + ["--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    benchmark_cmd = cmd if len(cmd) > 1 else cmd
                    log_info("Found benchmark command: " + " ".join(cmd))
                    break
            except Exception as e:
                continue
        if not benchmark_cmd:
            log_error("Could not find opensearch-benchmark command")
            return False
        full_cmd = benchmark_cmd + [
            "execute-test",
            "--pipeline", benchmark_config.get("pipeline", "benchmark-only"),
            "--workload", benchmark_config["workload_type"],
            "--target-host", benchmark_config["cluster_endpoint"] + ":80",
            "--results-file", "/opt/benchmark/benchmark-results.json"
        ]
        custom_params = benchmark_config.get("custom_benchmark_params", [])
        for param in custom_params:
            if param.get("value") and param["value"].strip():
                full_cmd.append(param["value"].strip())
        cmd_str = " ".join(full_cmd)
        log_info("Running benchmark command: " + cmd_str)
        log_progress("Starting OpenSearch benchmark...")
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=3600)
        log_info("Benchmark completed with exit code: " + str(result.returncode))
        log_info("STDOUT: " + result.stdout)
        if result.stderr:
            log_info("STDERR: " + result.stderr)
        if benchmark_config.get("s3_bucket"):
            try:
                s3_client = session.client('s3')
                bucket_name = benchmark_config["s3_bucket"]
                workflow_timestamp = benchmark_config["workflow_timestamp"]
                benchmark_id = benchmark_config.get("benchmark_id", "ec2_benchmark")
                
                # Test S3 access first
                log_info("Testing S3 access...")
                try:
                    s3_client.head_bucket(Bucket=bucket_name)
                    log_info("S3 access test successful")
                except Exception as e:
                    log_error("S3 access test failed: " + str(e))
                    return False
                
                # Read results file content if it exists
                results_file = "/opt/benchmark/benchmark-results.json"
                results_file_content = ""
                if os.path.exists(results_file):
                    try:
                        with open(results_file, 'r') as f:
                            results_file_content = f.read()
                        log_info("Found and read results file: " + results_file)
                    except Exception as e:
                        log_error("Failed to read results file: " + str(e))
                
                # Create benchmark metadata
                task_started_at = benchmark_config.get("task_started_at", datetime.now().strftime("%m/%d/%y, %H:%M:%S"))
                task_completed_at = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
                upload_date = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
                
                # Create clean config for upload
                clean_config = {
                    "cluster_endpoint": benchmark_config.get("cluster_endpoint"),
                    "workload_type": benchmark_config.get("workload_type"),
                    "pipeline": benchmark_config.get("pipeline"),
                    "s3_bucket": benchmark_config.get("s3_bucket"),
                    "custom_benchmark_params": benchmark_config.get("custom_benchmark_params", []),
                    "use_ec2_benchmark": True
                }
                
                # Upload benchmark-results.json
                benchmark_metadata = {
                    "benchmark_status": "success" if result.returncode == 0 else "error",
                    "benchmark_message": "EC2 benchmark completed successfully",
                    "benchmark_id": benchmark_id,
                    "results_location": f"s3://{bucket_name}/{workflow_timestamp}/benchmark/benchmark-results.json",
                    "config": clean_config,
                    "upload_date": upload_date,
                    "task_type": "benchmark",
                    "region": benchmark_config.get("aws_region", "us-east-1"),
                    "task_started_at": task_started_at,
                    "task_completed_at": task_completed_at
                }
                
                # Upload to {workflow_timestamp}/benchmark/benchmark-results.json (same as local)
                results_s3_key = f"{workflow_timestamp}/benchmark/benchmark-results.json"
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=results_s3_key,
                    Body=json.dumps(benchmark_metadata, indent=2),
                    ContentType='application/json'
                )
                log_info("Uploaded benchmark metadata: " + results_s3_key)
                
                # Upload benchmark-output.txt
                benchmark_command = " ".join(full_cmd)
                benchmark_stdout = result.stdout or ""
                benchmark_stderr = result.stderr or ""
                
                # Create output content
                output_content = f"Command: {benchmark_command}\\n"
                output_content += f"STDOUT:\\n{benchmark_stdout}\\n"
                if benchmark_stderr:
                    output_content += f"\\nSTDERR:\\n{benchmark_stderr}\\n"
                
                # Add results table if available
                if results_file_content:
                    output_content += f"\\n=== BENCHMARK RESULTS TABLE ===\\n{results_file_content}"
                
                # Upload to {workflow_timestamp}/benchmark/benchmark-output.txt
                output_s3_key = f"{workflow_timestamp}/benchmark/benchmark-output.txt"
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=output_s3_key,
                    Body=output_content,
                    ContentType='text/plain'
                )
                log_info("Uploaded benchmark output: " + output_s3_key)
                
                log_progress("Results uploaded to S3")
                
            except Exception as e:
                log_error("Failed to upload results to S3: " + str(e))
        return result.returncode == 0
    except Exception as e:
        log_error("Benchmark execution failed: " + str(e))
        return False
if __name__ == "__main__":
    success = run_benchmark()
    if success:
        print("✅ Benchmark completed successfully")
        with open('/opt/benchmark/status.txt', 'w') as f:
            f.write("BENCHMARK_COMPLETE")
    else:
        print("❌ Benchmark failed")
        with open('/opt/benchmark/status.txt', 'w') as f:
            f.write("BENCHMARK_FAILED")
'''
        
        script = f"""#!/bin/bash
exec > >(tee /var/log/user-data.log) 2>&1

echo "🚀 ========================================"
echo "🚀 OpenSearch Benchmark Worker Setup"
echo "🚀 ========================================"
echo "📅 Started at: $(date)"
echo "🆔 Benchmark ID: {benchmark_id}"
echo "🌐 Cluster Endpoint: {cluster_endpoint}"
echo "📊 Workload Type: {workload_type}"
echo "🏗️ Instance Type: {instance_type}"
echo ""

# Function to log progress
log_progress() {{
    echo "✅ [$(date '+%H:%M:%S')] $1"
}}

# Function to log error
log_error() {{
    echo "❌ [$(date '+%H:%M:%S')] $1"
}}

# Function to log info
log_info() {{
    echo "ℹ️ [$(date '+%H:%M:%S')] $1"
}}

log_progress "Starting EC2 instance setup..."

# Update system
log_info "Updating system packages..."
sudo yum update -y
log_progress "System packages updated"

# Set timezone to match local machine
log_info "Setting timezone to match local machine..."
sudo timedatectl set-timezone {local_timezone}
log_progress "Timezone set to {local_timezone}"

# Install required packages
log_info "Installing required packages..."
sudo yum install -y python3 python3-pip git wget curl
sudo yum install -y python3-pip
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel
log_progress "Required packages installed"

# Install Python 3.9 (required for opensearch-benchmark)
log_info "Installing Python 3.9..."
sudo yum install -y openssl-devel bzip2-devel libffi-devel

cd /tmp
wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar -xzf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall

# Update PATH to use Python 3.9
export PATH="/usr/local/bin:$PATH"
alias python3=/usr/local/bin/python3.9
alias pip3=/usr/local/bin/pip3.9

# Verify Python 3.9 installation
log_info "Verifying Python 3.9 installation..."
python3.9 --version
pip3.9 --version
log_progress "Python 3.9 installed successfully"

# Detect architecture and install appropriate AWS CLI
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    log_info "📦 Detected ARM64 architecture"
    curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
else
    log_info "📦 Detected x86_64 architecture"
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
fi

unzip awscliv2.zip
./aws/install
log_progress "AWS CLI installed"

# Set up AWS credentials from local machine
log_info "Setting up AWS credentials..."
mkdir -p /home/ec2-user/.aws

# Create credentials file with the same credentials as the local machine
cat > /home/ec2-user/.aws/credentials << 'EOF'
[default]
aws_access_key_id = {aws_creds['access_key']}
aws_secret_access_key = {aws_creds['secret_key']}
EOF

# Add token if it's a temporary credential
if [ -n "{aws_creds.get('token', '')}" ]; then
    echo "aws_session_token = {aws_creds.get('token', '')}" >> /home/ec2-user/.aws/credentials
fi

# Create config file
cat > /home/ec2-user/.aws/config << 'EOF'
[default]
region = {aws_creds['region']}
output = json
EOF

# Set proper permissions
chown -R ec2-user:ec2-user /home/ec2-user/.aws
chmod 600 /home/ec2-user/.aws/credentials
chmod 600 /home/ec2-user/.aws/config

# Also copy credentials to root's home for the Python script
mkdir -p /root/.aws
cp /home/ec2-user/.aws/credentials /root/.aws/
cp /home/ec2-user/.aws/config /root/.aws/
chmod 600 /root/.aws/credentials
chmod 600 /root/.aws/config

# Set environment variables for AWS credentials
export AWS_SHARED_CREDENTIALS_FILE=/root/.aws/credentials
export AWS_CONFIG_FILE=/root/.aws/config

log_progress "AWS credentials configured"

# Install OpenSearch Benchmark with Python 3.9
log_info "Installing OpenSearch Benchmark with Python 3.9..."
pip3.9 install opensearch-benchmark boto3

# Verify installation
log_info "Verifying OpenSearch Benchmark installation..."
if command -v opensearch-benchmark >/dev/null 2>&1; then
    log_progress "OpenSearch Benchmark installed successfully"
    opensearch-benchmark --version
else
    log_error "OpenSearch Benchmark not found in PATH, trying alternative installation..."
    pip3.9 install --user opensearch-benchmark boto3
    export PATH="$HOME/.local/bin:$PATH"
    if command -v opensearch-benchmark >/dev/null 2>&1; then
        log_progress "OpenSearch Benchmark installed with --user flag"
        opensearch-benchmark --version
    else
        log_error "OpenSearch Benchmark installation failed"
        find /usr/local -name "opensearch-benchmark" 2>/dev/null
        find ~/.local -name "opensearch-benchmark" 2>/dev/null
        pip3.9 show opensearch-benchmark
        log_info "Trying python -m opensearch_benchmark..."
        python3.9 -m opensearch_benchmark --version
    fi
fi

# Create symlink if needed
if ! command -v opensearch-benchmark >/dev/null 2>&1; then
    log_info "Creating symlink for opensearch-benchmark..."
    BENCHMARK_PATH=$(find /usr/local -name "opensearch-benchmark" 2>/dev/null | head -1)
    if [ -z "$BENCHMARK_PATH" ]; then
        BENCHMARK_PATH=$(find ~/.local -name "opensearch-benchmark" 2>/dev/null | head -1)
    fi
    if [ -n "$BENCHMARK_PATH" ]; then
        sudo ln -sf "$BENCHMARK_PATH" /usr/local/bin/opensearch-benchmark
        log_progress "Created symlink: $BENCHMARK_PATH -> /usr/local/bin/opensearch-benchmark"
    fi
fi

# Create benchmark directory
mkdir -p /opt/benchmark
cd /opt/benchmark

# Create benchmark configuration
log_info "Creating benchmark configuration..."
cat > benchmark_config.json << 'EOF'
{{
    "cluster_endpoint": "{cluster_endpoint}",
    "workload_type": "{workload_type}",
    "pipeline": "{pipeline}",
    "s3_bucket": "{s3_bucket}",
    "custom_benchmark_params": {custom_benchmark_params},
    "workflow_timestamp": "{workflow_timestamp}",
    "task_started_at": "{task_started_at or ''}",
    "aws_access_key": "{aws_creds['access_key']}",
    "aws_secret_key": "{aws_creds['secret_key']}",
    "aws_region": "{aws_creds['region']}"
}}
EOF

# Add token if it's a temporary credential
if [ -n "{aws_creds.get('token', '')}" ]; then
    echo '    "aws_token": "{aws_creds.get('token', '')}",' >> benchmark_config.json
fi
log_progress "Benchmark configuration created"

# Create benchmark script
log_info "Creating benchmark execution script..."
cat > run_benchmark.py << 'PYTHON_EOF'
{python_script}
PYTHON_EOF
log_progress "Benchmark script created"
echo "SETUP_COMPLETE" > /opt/benchmark/status.txt
log_progress "Setup completed - starting benchmark..."
log_info "Starting benchmark execution..."
python3.9 run_benchmark.py
echo "BENCHMARK_COMPLETE" > /opt/benchmark/status.txt
log_progress "Benchmark workflow completed"
"""

        logger.info("✅ User data script created successfully")
        return script
