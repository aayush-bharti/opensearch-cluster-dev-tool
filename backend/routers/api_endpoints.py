# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from scripts.build import run_build_process
from scripts.deploy import run_deploy_process
from scripts.benchmark import run_benchmark_process
from job_tracker import job_tracker, JobStatus, TaskStatus
from constants import Status, TaskTypes, ResultFields, ConfigFields, ErrorMessages
from datetime import datetime
import logging

# Create new router for auto-credential endpoints
router = APIRouter()
auto_logger = logging.getLogger(__name__)

# class that handles the configs for the workflow
class WorkflowConfig(BaseModel):
    """Unified configuration for workflow operations"""
    # Build configuration
    manifest_yml: Optional[str] = None
    suffix: Optional[str] = None
    custom_build_params: Optional[list] = None
    
    # Deploy configuration
    distribution_url: Optional[str] = None
    security_disabled: bool = None
    cpu_arch: str = None
    single_node_cluster: bool = None
    data_instance_type: Optional[str] = None
    data_node_count: Optional[int] = None
    dist_version: str = None
    min_distribution: bool = None
    server_access_type: str = None
    restrict_server_access_to: str = None
    use_50_percent_heap: Optional[bool] = None
    is_internal: Optional[bool] = None
    custom_deploy_params: Optional[list] = None
    admin_password: Optional[str] = None
    
    # Benchmark configuration
    cluster_endpoint: Optional[str] = None
    workload_type: Optional[str] = None
    pipeline: Optional[str] = None
    custom_benchmark_params: Optional[list] = None
    
    # S3 Configuration
    s3_bucket: str = None

# Task execution functions
def execute_build_task(job_id: str, config: dict, workflow_timestamp: str) -> dict:
    """Execute build task and return result."""
    auto_logger.info(f"🔨 Starting build operation for job {job_id}")
    job_tracker.update_task_status(job_id, TaskTypes.BUILD, TaskStatus.RUNNING)
    job_tracker.update_progress(job_id, "Building OpenSearch...")
    
    try:
        # Prepare build configuration with S3 bucket
        build_config = {
            ConfigFields.MANIFEST_YML: config[ConfigFields.MANIFEST_YML],
            ConfigFields.S3_BUCKET: config.get(ConfigFields.S3_BUCKET),
            ConfigFields.CUSTOM_BUILD_PARAMS: config.get(ConfigFields.CUSTOM_BUILD_PARAMS)
        }
        
        build_result = run_build_process(
            build_config,
            workflow_timestamp
        )
        
        if build_result.get(ResultFields.STATUS) == Status.SUCCESS:
            auto_logger.info(f"✅ Build completed successfully for job {job_id}")
            job_tracker.update_task_status(job_id, TaskTypes.BUILD, TaskStatus.COMPLETED, build_result)
            return build_result
        else:
            raise Exception(f"Build failed: {build_result}")
            
    except Exception as e:
        auto_logger.error(f"❌ Build failed for job {job_id}: {str(e)}")
        job_tracker.update_task_status(job_id, TaskTypes.BUILD, TaskStatus.FAILED, error=str(e))
        raise

# execute the deploy task
def execute_deploy_task(job_id: str, config: dict, workflow_timestamp: str) -> dict:
    """Execute deploy task and return result."""
    auto_logger.info(f"🚀 Starting deploy operation for job {job_id}")
    job_tracker.update_task_status(job_id, TaskTypes.DEPLOY, TaskStatus.RUNNING)
    job_tracker.update_progress(job_id, "Deploying OpenSearch cluster...")
    
    try:
        # Prepare deploy configuration
        deploy_config = {
            ConfigFields.SUFFIX: config[ConfigFields.SUFFIX],
            ConfigFields.DISTRIBUTION_URL: config[ConfigFields.DISTRIBUTION_URL],
            ConfigFields.SECURITY_DISABLED: config[ConfigFields.SECURITY_DISABLED],
            ConfigFields.CPU_ARCH: config[ConfigFields.CPU_ARCH],
            ConfigFields.SINGLE_NODE_CLUSTER: config[ConfigFields.SINGLE_NODE_CLUSTER],
            ConfigFields.DATA_INSTANCE_TYPE: config[ConfigFields.DATA_INSTANCE_TYPE],
            ConfigFields.DATA_NODE_COUNT: config[ConfigFields.DATA_NODE_COUNT],
            ConfigFields.DIST_VERSION: config[ConfigFields.DIST_VERSION],
            ConfigFields.MIN_DISTRIBUTION: config[ConfigFields.MIN_DISTRIBUTION],
            ConfigFields.SERVER_ACCESS_TYPE: config[ConfigFields.SERVER_ACCESS_TYPE],
            ConfigFields.RESTRICT_SERVER_ACCESS_TO: config[ConfigFields.RESTRICT_SERVER_ACCESS_TO],
            ConfigFields.USE_50_PERCENT_HEAP: config[ConfigFields.USE_50_PERCENT_HEAP],
            ConfigFields.IS_INTERNAL: config[ConfigFields.IS_INTERNAL],
            ConfigFields.ADMIN_PASSWORD: config.get(ConfigFields.ADMIN_PASSWORD),
            ConfigFields.S3_BUCKET: config.get(ConfigFields.S3_BUCKET),
            ConfigFields.CUSTOM_DEPLOY_PARAMS: config.get(ConfigFields.CUSTOM_DEPLOY_PARAMS)
        }
        
        # Add S3 bucket to deploy config
        auto_logger.info(f"🔍 S3 bucket from config: {config.get(ConfigFields.S3_BUCKET)}")
        
        deploy_result = run_deploy_process(
            deploy_config,
            workflow_timestamp
        )
        
        if deploy_result.get(ResultFields.STATUS) == Status.SUCCESS:
            auto_logger.info(f"✅ Deploy completed successfully for job {job_id}")
            job_tracker.update_task_status(job_id, TaskTypes.DEPLOY, TaskStatus.COMPLETED, deploy_result)
            return deploy_result
        else:
            raise Exception(f"Deploy failed: {deploy_result}")
            
    except Exception as e:
        auto_logger.error(f"❌ Deploy failed for job {job_id}: {str(e)}")
        job_tracker.update_task_status(job_id, TaskTypes.DEPLOY, TaskStatus.FAILED, error=str(e))
        raise

# execute the benchmark task
def execute_benchmark_task(job_id: str, config: dict, workflow_timestamp: str) -> dict:
    """Execute benchmark task and return result."""
    auto_logger.info(f"📊 Starting benchmark operation for job {job_id}")
    job_tracker.update_task_status(job_id, TaskTypes.BENCHMARK, TaskStatus.RUNNING)
    job_tracker.update_progress(job_id, "Running benchmark...")
    
    try:
        benchmark_config = {
            ConfigFields.CLUSTER_ENDPOINT: config[ConfigFields.CLUSTER_ENDPOINT],
            ConfigFields.WORKLOAD_TYPE: config[ConfigFields.WORKLOAD_TYPE],
            ConfigFields.PIPELINE: config[ConfigFields.PIPELINE],
            ConfigFields.S3_BUCKET: config.get(ConfigFields.S3_BUCKET),
            ConfigFields.CUSTOM_BENCHMARK_PARAMS: config.get(ConfigFields.CUSTOM_BENCHMARK_PARAMS)
        }
        
        benchmark_result = run_benchmark_process(
            benchmark_config,
            workflow_timestamp
        )
        
        if benchmark_result.get(ResultFields.STATUS) == Status.SUCCESS:
            auto_logger.info(f"✅ Benchmark completed successfully for job {job_id}")
            job_tracker.update_task_status(job_id, TaskTypes.BENCHMARK, TaskStatus.COMPLETED, benchmark_result)
            return benchmark_result
        else:
            raise Exception(f"Benchmark failed: {benchmark_result}")
            
    except Exception as e:
        auto_logger.error(f"❌ Benchmark failed for job {job_id}: {str(e)}")
        job_tracker.update_task_status(job_id, TaskTypes.BENCHMARK, TaskStatus.FAILED, error=str(e))
        raise

# runs the workflow in the background
def run_workflow_background(job_id: str, config: dict, tasks: dict):
    """Run workflow in background thread with job tracking."""
    try:
        # Update job status to running
        job_tracker.update_job_status(job_id, JobStatus.RUNNING)
        
        # Generate workflow timestamp
        workflow_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        job_tracker.set_workflow_timestamp(job_id, workflow_timestamp)
        
        auto_logger.info(f"🚀 Starting background workflow for job {job_id}")
        
        # Track results for data passing between tasks
        build_result = None
        deploy_result = None
        benchmark_result = None
        
        # Execute build task if requested
        if tasks.get(TaskTypes.BUILD):
            build_result = execute_build_task(job_id, config, workflow_timestamp)
            
            # Pass build artifact to deploy if needed
            if tasks.get(TaskTypes.DEPLOY) and build_result.get(ResultFields.S3_INFO):
                config[ConfigFields.DISTRIBUTION_URL] = build_result[ResultFields.S3_INFO][ResultFields.S3_URI]
                auto_logger.info(f"📦 Using build artifact for deployment: {config[ConfigFields.DISTRIBUTION_URL]}")
            elif tasks.get(TaskTypes.DEPLOY) and not build_result.get(ResultFields.S3_INFO):
                raise Exception(ErrorMessages.BUILD_S3_UPLOAD_FAILED)
        
        # Execute deploy task if requested
        if tasks.get(TaskTypes.DEPLOY):
            deploy_result = execute_deploy_task(job_id, config, workflow_timestamp)
            
            # Pass cluster endpoint to benchmark if needed
            if tasks.get(TaskTypes.BENCHMARK) and deploy_result.get(ResultFields.CLUSTER_INFO, {}).get(ResultFields.CLUSTER_ENDPOINT):
                config[ConfigFields.CLUSTER_ENDPOINT] = deploy_result[ResultFields.CLUSTER_INFO][ResultFields.CLUSTER_ENDPOINT]
                auto_logger.info(f"🔗 Using deployed cluster for benchmark: {config[ConfigFields.CLUSTER_ENDPOINT]}")
            elif tasks.get(TaskTypes.BENCHMARK) and not deploy_result.get(ResultFields.CLUSTER_INFO, {}).get(ResultFields.CLUSTER_ENDPOINT):
                raise Exception(ErrorMessages.DEPLOY_CLUSTER_ENDPOINT_NOT_FOUND)
        
        # Execute benchmark task if requested
        if tasks.get(TaskTypes.BENCHMARK):
            benchmark_result = execute_benchmark_task(job_id, config, workflow_timestamp)
        
        # If all tasks completed successfully, update the job status
        job_tracker.update_job_status(job_id, JobStatus.COMPLETED)
        job_tracker.update_progress(job_id, "Workflow completed successfully!")
        auto_logger.info(f"✅ Workflow completed successfully for job {job_id}")
        
    except Exception as e:
        auto_logger.error(f"❌ Workflow execution failed for job {job_id}: {str(e)}")
        job_tracker.update_job_status(job_id, JobStatus.FAILED, str(e))

# api endpoint to start the workflow, uses a dynamic approach for the api endpoint
@router.post("/workflow")
async def execute_workflow(
    config: WorkflowConfig,
    background_tasks: BackgroundTasks,
    build: bool = Query(False, description="Execute build step"),
    deploy: bool = Query(False, description="Execute deploy step"),
    benchmark: bool = Query(False, description="Execute benchmark step")
):
    """
    Start a workflow and return job ID immediately for polling.
    
    Examples:
    - POST /workflow?build=true&deploy=true&benchmark=true (build + deploy + benchmark)
    - POST /workflow?build=true&deploy=true (build + deploy)
    - POST /workflow?deploy=true&benchmark=true (deploy + benchmark)
    - POST /workflow?build=true (build only)
    - POST /workflow?deploy=true (deploy only)
    - POST /workflow?benchmark=true (benchmark only)
    """
    
    auto_logger.info(f"🚀 Starting workflow execution - build: {build}, deploy: {deploy}, benchmark: {benchmark}")
    
    # Validate that at least one operation is requested
    if not any([build, deploy, benchmark]):
        raise HTTPException(
            status_code=400,
            detail="At least one operation must be specified: build, deploy, or benchmark"
        )
    
    # Validate required fields for each operation
    if build and not config.manifest_yml:
        raise HTTPException(
            status_code=400,
            detail="manifest_yml is required when build=true"
        )
    
    if deploy and not config.distribution_url and not build:
        raise HTTPException(
            status_code=400,
            detail="distribution_url is required when deploy=true (unless build=true)"
        )
    
    if benchmark and not config.cluster_endpoint and not deploy:
        raise HTTPException(
            status_code=400,
            detail="cluster_endpoint is required when benchmark=true (unless deploy=true)"
        )
    
    if benchmark and not config.workload_type:
        raise HTTPException(
            status_code=400,
            detail="workload_type is required when benchmark=true"
        )
    
    # Create config dictionary for background task
    config_dict = {
        # Build config
        ConfigFields.MANIFEST_YML: config.manifest_yml,
        ConfigFields.CUSTOM_BUILD_PARAMS: config.custom_build_params,
        
        # Deploy config
        ConfigFields.SUFFIX: config.suffix,
        ConfigFields.DISTRIBUTION_URL: config.distribution_url,
        ConfigFields.SECURITY_DISABLED: config.security_disabled,
        ConfigFields.CPU_ARCH: config.cpu_arch,
        ConfigFields.SINGLE_NODE_CLUSTER: config.single_node_cluster,
        ConfigFields.DATA_INSTANCE_TYPE: config.data_instance_type,
        ConfigFields.DATA_NODE_COUNT: config.data_node_count,
        ConfigFields.DIST_VERSION: config.dist_version,
        ConfigFields.MIN_DISTRIBUTION: config.min_distribution,
        ConfigFields.SERVER_ACCESS_TYPE: config.server_access_type,
        ConfigFields.RESTRICT_SERVER_ACCESS_TO: config.restrict_server_access_to,
        ConfigFields.USE_50_PERCENT_HEAP: config.use_50_percent_heap,
        ConfigFields.IS_INTERNAL: config.is_internal,
        ConfigFields.ADMIN_PASSWORD: config.admin_password,
        ConfigFields.CUSTOM_DEPLOY_PARAMS: config.custom_deploy_params,
        
        # Benchmark config
        ConfigFields.CLUSTER_ENDPOINT: config.cluster_endpoint,
        ConfigFields.WORKLOAD_TYPE: config.workload_type,
        ConfigFields.PIPELINE: config.pipeline,
        ConfigFields.CUSTOM_BENCHMARK_PARAMS: config.custom_benchmark_params,
        
        # S3 Configuration
        ConfigFields.S3_BUCKET: config.s3_bucket
    }
    
    # Create tasks dictionary
    tasks_dict = {
        TaskTypes.BUILD: build,
        TaskTypes.DEPLOY: deploy,
        TaskTypes.BENCHMARK: benchmark
    }
    
    # Create job in job tracker
    job_id = job_tracker.create_job(config_dict, tasks_dict)
    
    # Start background workflow
    background_tasks.add_task(run_workflow_background, job_id, config_dict, tasks_dict)
    
    # Return job ID and other information
    return {
        "job_id": job_id,
        "message": "Workflow started. Use GET /jobs/{job_id} to check status.",
        "status_url": f"/api/cluster/jobs/{job_id}",
        "operations": {
            TaskTypes.BUILD: build,
            TaskTypes.DEPLOY: deploy,
            TaskTypes.BENCHMARK: benchmark
        }
    }

# api endpoint to get the status of a job
@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get the current status of a job by ID."""
    job_data = job_tracker.get_job_status(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return job_data

# api endpoint to list all jobs
@router.get("/jobs")
async def list_jobs(limit: int = Query(50, ge=1, le=100)):
    """List recent jobs with their status."""
    jobs = job_tracker.list_jobs(limit)
    return {
        "jobs": jobs,
        "total": len(jobs)
    }

# api endpoint to cancel a job
@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    job_data = job_tracker.get_job_status(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job_data["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Job {job_id} is already {job_data['status']}")
    
    # Update job status to cancelled
    success = job_tracker.update_job_status(job_id, JobStatus.CANCELLED)
    if success:
        return {"message": f"Job {job_id} cancelled successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to cancel job")

# api endpoint to delete a job
@router.delete("/jobs/{job_id}/delete")
async def delete_job(job_id: str):
    """Delete a job by ID."""
    success = job_tracker.delete_job(job_id)
    if success:
        return {"message": f"Job {job_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
