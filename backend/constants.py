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
    MANIFEST_YML = "manifest_yml"
    SUFFIX = "suffix"
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
    CLUSTER_ENDPOINT = "cluster_endpoint"
    WORKLOAD_TYPE = "workload_type"
    PIPELINE = "pipeline"

# Default values
class Defaults:
    SECURITY_DISABLED = True
    CPU_ARCH = "arm64"
    SINGLE_NODE_CLUSTER = False
    DATA_INSTANCE_TYPE = "r6g.2xlarge"
    DATA_NODE_COUNT = 3
    DIST_VERSION = "3.0.0"
    MIN_DISTRIBUTION = False
    SERVER_ACCESS_TYPE = ""
    RESTRICT_SERVER_ACCESS_TO = ""
    USE_50_PERCENT_HEAP = True
    IS_INTERNAL = False
    PIPELINE = "benchmark-only"

# Error messages
class ErrorMessages:
    BUILD_S3_UPLOAD_FAILED = "Build completed but S3 upload failed. Cannot proceed with deployment."
    DEPLOY_CLUSTER_ENDPOINT_NOT_FOUND = "Deploy completed but cluster endpoint not found. Cannot proceed with benchmark."
    WORKFLOW_INTERRUPTED = "Process interrupted (server restart)" 