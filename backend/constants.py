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

# Result field constants
class ResultFields:
    STATUS = "status"
    MESSAGE = "message"
    S3_INFO = "s3_info"
    S3_URI = "s3_uri"
    CLUSTER_INFO = "cluster_info"
    CLUSTER_ENDPOINT = "cluster_endpoint"
    BENCHMARK_ID = "benchmark_id"
    RESULTS_LOCATION = "results_location"
    OUTPUT = "output"
    RESULTS_FILE_CONTENT = "results_file_content"

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
