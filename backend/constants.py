# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

"""Constants used throughout the OpenSearch workflow application."""

# Status constants
class Status:
    SUCCESS = "success"
    ERROR = "error"
    SUCCESS_UPPER = "SUCCESS"

# Task type constants
class TaskTypes:
    BUILD = "build"
    DEPLOY = "deploy"
    BENCHMARK = "benchmark"

# AWS Configuration constants
class AWSConfig:
    DEFAULT_REGION = "us-east-1"

# Result field constants
class ResultFields:
    STATUS = "status"
    MESSAGE = "message"
    S3_INFO = "s3_info"
    S3_URI = "s3_uri"
    HTTPS_URL = "https_url"
    BUCKET_NAME = "bucket_name"
    S3_KEY = "s3_key"
    FILE_SIZE = "file_size"
    TIMESTAMP = "timestamp"
    UPLOAD_DATE = "upload_date"
    TASK_TYPE = "task_type"
    REGION = "region"
    CLUSTER_INFO = "cluster_info"
    CLUSTER_ENDPOINT = "cluster_endpoint"
    BENCHMARK_ID = "benchmark_id"
    RESULTS_LOCATION = "results_location"
    OUTPUT = "output"
    RESULTS_FILE_CONTENT = "results_file_content"
    ERROR_OUTPUT = "error_output"
    FULL_OUTPUT = "full_output"
    COMMAND = "command"
    CONFIG = "config"

    BUILD_STATUS = "build_status"
    BUILD_MESSAGE = "build_message"
    BUILD_MANIFEST_PATH = "build_manifest_path"
    TARBALL_PATH = "tarball_path"

    DEPLOY_STATUS = "deploy_status"
    DEPLOY_MESSAGE = "deploy_message"

    TASK_STARTED_AT = "task_started_at"
    TASK_COMPLETED_AT = "task_completed_at"
    STDOUT = "stdout"
    STDERR = "stderr"
    BENCHMARK_STATUS = "benchmark_status"
    BENCHMARK_MESSAGE = "benchmark_message"
    EXECUTION_INFO = "execution_info"
    CONTENT_LENGTH = "content_length"
    BENCHMARK_SUCCESS = "benchmark_success"
    INSTANCE_ID = "instance_id"
    INSTANCE_INFO = "instance_info"
    
    CLUSTER_SECURITY_GROUP = "cluster_security_group"
    PUBLIC_IP = "public_ip"
    PRIVATE_IP = "private_ip"
    SECURITY_GROUP_ID = "security_group_id"
    VPC_ID = "vpc_id"
    SUBNET_ID = "subnet_id"

    OUTPUT_S3_INFO = "output_s3_info"
    RESULTS_S3_URI = "results_s3_uri"
    RESULTS_HTTPS_URL = "results_https_url"
    RESULTS_S3_KEY = "results_s3_key"

    RESULTS_EXIST = "results_exist"
    OUTPUT_EXIST = "output_exist"
    WORKFLOW_TIMESTAMP = "workflow_timestamp"
    RESULTS_KEY = "results_key"
    OUTPUT_KEY = "output_key"
    RESULTS_SIZE = "results_size"
    OUTPUT_SIZE = "output_size"
    RESULTS_LAST_MODIFIED = "results_last_modified"
    OUTPUT_LAST_MODIFIED = "output_last_modified"

# Configuration field constants
class ConfigFields:
    # Build config
    MANIFEST_YML = "manifest_yml"
    SUFFIX = "suffix"
    # Deploy config
    DISTRIBUTION_URL = "distribution_url"
    SECURITY_DISABLED = "security_disabled"
    CPU_ARCH = "cpu_arch"
    SINGLE_NODE_CLUSTER = "single_node_cluster"
    DATA_INSTANCE_TYPE = "data_instance_type"
    DATA_NODE_COUNT = "data_node_count"
    DIST_VERSION = "dist_version"
    MIN_DISTRIBUTION = "min_distribution"
    SERVER_ACCESS_TYPE = "server_access_type"
    RESTRICT_SERVER_ACCESS_TO = "restrict_server_access_to"
    USE_50_PERCENT_HEAP = "use_50_percent_heap"
    IS_INTERNAL = "is_internal"
    ADMIN_PASSWORD = "admin_password"
    # Benchmark config
    CLUSTER_ENDPOINT = "cluster_endpoint"
    WORKLOAD_TYPE = "workload_type"
    PIPELINE = "pipeline"
    
    # EC2 Benchmark config
    USE_EC2_BENCHMARK = "use_ec2_benchmark"
    INSTANCE_TYPE = "instance_type"
    KEY_NAME = "key_name"
    SUBNET_ID = "subnet_id"
    MY_IP = "my_ip"
    TIMEOUT_MINUTES = "timeout_minutes"
    SECURITY_GROUP_ID = "security_group_id"
    
    # S3 Configuration
    S3_BUCKET = "s3_bucket"    
    
    # Custom parameters for each task type
    CUSTOM_BUILD_PARAMS = "custom_build_params"
    CUSTOM_DEPLOY_PARAMS = "custom_deploy_params"
    CUSTOM_BENCHMARK_PARAMS = "custom_benchmark_params"

# Error messages
class ErrorMessages:
    BUILD_S3_UPLOAD_FAILED = "Build completed but S3 upload failed. Cannot proceed with deployment."
    DEPLOY_CLUSTER_ENDPOINT_NOT_FOUND = "Deploy completed but cluster endpoint not found. Cannot proceed with benchmark."
    WORKFLOW_INTERRUPTED = "Process interrupted (server restart)"
