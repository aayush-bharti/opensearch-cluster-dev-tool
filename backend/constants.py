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
    # Benchmark config
    CLUSTER_ENDPOINT = "cluster_endpoint"
    WORKLOAD_TYPE = "workload_type"
    PIPELINE = "pipeline"
    
    # S3 Configuration
    S3_BUCKET = "s3_bucket"    
    
    # Advanced deploy configuration fields
    ADDITIONAL_CONFIG = "additional_config"
    ADDITIONAL_OSD_CONFIG = "additional_osd_config"
    ADMIN_PASSWORD = "admin_password"
    CERTIFICATE_ARN = "certificate_arn"
    CIDR = "cidr"
    CLIENT_NODE_COUNT = "client_node_count"
    CONTEXT_KEY = "context_key"
    CUSTOM_CONFIG_FILES = "custom_config_files"
    CUSTOM_ROLE_ARN = "custom_role_arn"
    DATA_NODE_STORAGE = "data_node_storage"
    ENABLE_MONITORING = "enable_monitoring"
    ENABLE_REMOTE_STORE = "enable_remote_store"
    INGEST_NODE_COUNT = "ingest_node_count"
    JVM_SYS_PROPS = "jvm_sys_props"
    LOAD_BALANCER_TYPE = "load_balancer_type"
    MANAGER_NODE_COUNT = "manager_node_count"
    MAP_OPENSEARCH_DASHBOARDS_PORT_TO = "map_opensearch_dashboards_port_to"
    MAP_OPENSEARCH_PORT_TO = "map_opensearch_port_to"
    ML_INSTANCE_TYPE = "ml_instance_type"
    ML_NODE_COUNT = "ml_node_count"
    ML_NODE_STORAGE = "ml_node_storage"
    NETWORK_STACK_SUFFIX = "network_stack_suffix"
    SECURITY_GROUP_ID = "security_group_id"
    STORAGE_VOLUME_TYPE = "storage_volume_type"
    USE_INSTANCE_BASED_STORAGE = "use_instance_based_storage"
    VPC_ID = "vpc_id"

# Error messages
class ErrorMessages:
    BUILD_S3_UPLOAD_FAILED = "Build completed but S3 upload failed. Cannot proceed with deployment."
    DEPLOY_CLUSTER_ENDPOINT_NOT_FOUND = "Deploy completed but cluster endpoint not found. Cannot proceed with benchmark."
    WORKFLOW_INTERRUPTED = "Process interrupted (server restart)" 
    