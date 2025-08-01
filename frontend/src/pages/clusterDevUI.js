/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useCallback } from "react";
import { EuiIcon } from "@opensearch-project/oui";
import "./clusterDevUI.css";
import JobConfiguration from "../components/JobConfiguration";
import TaskHistory from "../components/TaskHistory";

// API Endpoint Constants
const API_BASE_URL = "http://localhost:8000";
const API_ENDPOINTS = {
  JOBS: `${API_BASE_URL}/api/cluster/jobs`,
  JOB_DETAILS: (jobId) => `${API_BASE_URL}/api/cluster/jobs/${jobId}`,
  JOB_DELETE: (jobId) => `${API_BASE_URL}/api/cluster/jobs/${jobId}/delete`,
  JOB_CANCEL: (jobId) => `${API_BASE_URL}/api/cluster/jobs/${jobId}/cancel`,
  WORKFLOW: `${API_BASE_URL}/api/cluster/workflow`,
};

// Cluster Dev UI Page
export default function ClusterDevUI() {
  const [selectedTasks, setSelectedTasks] = useState({
    build: false,
    deploy: false,
    benchmark: false,
  });
  const [config, setConfig] = useState({
    // build config
    manifest_yml: '',

    // deploy config
    suffix: '',
    distribution_url: '',
    min_distribution: 'false',
    security_disabled: true,
    cpu_arch: 'arm64',
    single_node_cluster: false,
    data_instance_type: 'r6g.large',
    data_node_count: 3,
    dist_version: '3.0.0',
    use_50_percent_heap: true,
    is_internal: false,

    // advanced deploy config (optional)
    additional_config: '',
    additional_osd_config: '',
    admin_password: '',
    certificate_arn: '',
    cidr: '',
    client_node_count: undefined,
    context_key: '',
    custom_config_files: '',
    custom_role_arn: '',
    data_node_storage: undefined,
    enable_monitoring: undefined,
    enable_remote_store: undefined,
    ingest_node_count: undefined,
    jvm_sys_props: '',
    load_balancer_type: '',
    manager_node_count: undefined,
    map_opensearch_dashboards_port_to: undefined,
    map_opensearch_port_to: undefined,
    ml_instance_type: '',
    ml_node_count: undefined,
    ml_node_storage: undefined,
    network_stack_suffix: '',
    restrict_server_access_to: '',
    security_group_id: '',
    server_access_type: '',
    storage_volume_type: '',
    use_instance_based_storage: undefined,
    vpc_id: '',

    // benchmark config
    cluster_endpoint: '',
    workload_type: 'percolator',
    pipeline: 'benchmark-only',
    
    // S3 Configuration
    s3_bucket: ''
  });

  const [jobs, setJobs] = useState([]);
  const [isButtonPressed, setIsButtonPressed] = useState(false);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);

  // Helper function to fetch detailed job information
  const fetchJobDetails = useCallback(async (jobId) => {
    try {
      const response = await fetch(API_ENDPOINTS.JOB_DETAILS(jobId));
      if (response.ok) {
        const jobDetails = await response.json();

        // Extract task selection from job details
        const tasks = {};
        Object.keys(jobDetails.tasks || {}).forEach((taskName) => {
          tasks[taskName] = true;
        });

        return {
          id: jobDetails.job_id,
          jobId: jobDetails.job_id,
          displayId: jobDetails.display_id || 0,
          tasks: tasks,
          config: jobDetails.config || {},
          timestamp: new Date(jobDetails.created_at).toLocaleString(),
        };
      } else {
        console.warn(`Failed to fetch details for job ${jobId}`);
        return null;
      }
    } catch (error) {
      console.error(`Error fetching job details for ${jobId}:`, error);
      return null;
    }
  }, []);

  // Function to fetch jobs from backend
  const fetchJobs = useCallback(async () => {
    try {
      setIsLoadingJobs(true);
      const response = await fetch(API_ENDPOINTS.JOBS);
      if (response.ok) {
        const data = await response.json();

        // Convert backend job format to frontend job format
        const formattedJobs = data.jobs.map((backendJob) => {
          // Get the full job details using backend UUID
          return fetchJobDetails(backendJob.job_id);
        });

        // Wait for all job details to be fetched
        const resolvedJobs = await Promise.all(formattedJobs);
        const validJobs = resolvedJobs.filter((job) => job !== null);

        // Update display IDs from backend job listing
        validJobs.forEach((job, index) => {
          const backendJob = data.jobs.find((bj) => bj.job_id === job.jobId);
          if (backendJob && backendJob.display_id) {
            job.displayId = backendJob.display_id;
          }
        });

        setJobs(validJobs);
      } else {
        console.error("Failed to fetch jobs:", response.status);
      }
    } catch (error) {
      console.error("Error fetching jobs:", error);
    } finally {
      setIsLoadingJobs(false);
    }
  }, [fetchJobDetails]);

  // Function to delete a job
  const handleDeleteJob = useCallback(async (jobId) => {
    if (!window.confirm("Are you sure you want to delete this job?")) return;

    try {
      const response = await fetch(API_ENDPOINTS.JOB_DELETE(jobId), {
        method: "DELETE",
      });

      if (response.ok) {
        // Remove job from local state
        setJobs((prevJobs) => prevJobs.filter((job) => job.jobId !== jobId));
        console.log(`Job ${jobId} deleted successfully`);
      } else {
        const data = await response.json();
        alert(data.detail || "Failed to delete job");
      }
    } catch (error) {
      console.error("Error deleting job:", error);
      alert("Error deleting job");
    }
  }, []);

  // Fetch jobs from backend on component mount
  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleTaskToggle = (task) => {
    setSelectedTasks((prev) => ({ ...prev, [task]: !prev[task] }));
  };

  const handleConfigChange = (field) => (e) => {
    const value =
      e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const handleLaunchJob = async () => {
    setIsButtonPressed(true);

    try {
      // Build query parameters based on selected tasks
      const queryParams = new URLSearchParams();
      if (selectedTasks.build) queryParams.set("build", "true");
      if (selectedTasks.deploy) queryParams.set("deploy", "true");
      if (selectedTasks.benchmark) queryParams.set("benchmark", "true");

      // Single workflow API call to start the job
      const workflowResponse = await fetch(`${API_ENDPOINTS.WORKFLOW}?${queryParams}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          // Build config
          ...(selectedTasks.build && { manifest_yml: config.manifest_yml }),
          
          // Deploy config
          ...(selectedTasks.deploy && {
            suffix: config.suffix,
            ...(config.distribution_url && { distribution_url: config.distribution_url }),
            security_disabled: config.security_disabled,
            cpu_arch: config.cpu_arch,
            data_instance_type: config.data_instance_type,
            data_node_count: config.data_node_count,
            dist_version: config.dist_version,
            min_distribution: config.min_distribution,
            single_node_cluster: config.single_node_cluster,
            server_access_type: config.server_access_type,
            restrict_server_access_to: config.restrict_server_access_to,
            use_50_percent_heap: config.use_50_percent_heap,
            is_internal: config.is_internal,
            
            // Advanced deploy configuration (only include if provided)
            ...(config.additional_config && { additional_config: config.additional_config }),
            ...(config.additional_osd_config && { additional_osd_config: config.additional_osd_config }),
            ...(config.admin_password && { admin_password: config.admin_password }),
            ...(config.certificate_arn && { certificate_arn: config.certificate_arn }),
            ...(config.cidr && { cidr: config.cidr }),
            ...(config.client_node_count && { client_node_count: config.client_node_count }),
            ...(config.context_key && { context_key: config.context_key }),
            ...(config.custom_config_files && { custom_config_files: config.custom_config_files }),
            ...(config.custom_role_arn && { custom_role_arn: config.custom_role_arn }),
            ...(config.data_node_storage && { data_node_storage: config.data_node_storage }),
            ...(config.enable_monitoring !== undefined && { enable_monitoring: config.enable_monitoring }),
            ...(config.enable_remote_store !== undefined && { enable_remote_store: config.enable_remote_store }),
            ...(config.ingest_node_count && { ingest_node_count: config.ingest_node_count }),
            ...(config.jvm_sys_props && { jvm_sys_props: config.jvm_sys_props }),
            ...(config.load_balancer_type && { load_balancer_type: config.load_balancer_type }),
            ...(config.manager_node_count && { manager_node_count: config.manager_node_count }),
            ...(config.map_opensearch_dashboards_port_to && { map_opensearch_dashboards_port_to: config.map_opensearch_dashboards_port_to }),
            ...(config.map_opensearch_port_to && { map_opensearch_port_to: config.map_opensearch_port_to }),
            ...(config.ml_instance_type && { ml_instance_type: config.ml_instance_type }),
            ...(config.ml_node_count && { ml_node_count: config.ml_node_count }),
            ...(config.ml_node_storage && { ml_node_storage: config.ml_node_storage }),
            ...(config.network_stack_suffix && { network_stack_suffix: config.network_stack_suffix }),
            ...(config.restrict_server_access_to && { restrict_server_access_to: config.restrict_server_access_to }),
            ...(config.security_group_id && { security_group_id: config.security_group_id }),
            ...(config.storage_volume_type && { storage_volume_type: config.storage_volume_type }),
            ...(config.use_instance_based_storage !== undefined && { use_instance_based_storage: config.use_instance_based_storage }),
            ...(config.vpc_id && { vpc_id: config.vpc_id })
          }),
          
          // Benchmark config
          ...(selectedTasks.benchmark && {
            ...(config.cluster_endpoint && { cluster_endpoint: config.cluster_endpoint }),
            workload_type: config.workload_type,
            pipeline: config.pipeline
          }),
          
          // S3 Configuration (always include)
          s3_bucket: config.s3_bucket || ''
        })
      });

      if (!workflowResponse.ok) {
        const errorData = await workflowResponse.json();
        throw new Error(`Workflow failed: ${errorData.detail}`);
      }

      const workflowData = await workflowResponse.json();

      const newJob = {
        id: workflowData.job_id,
        jobId: workflowData.job_id,
        displayId: workflowData.display_id,
        tasks: { ...selectedTasks },
        config: { ...config },
        timestamp: new Date().toLocaleString(),
      };

      setJobs((prev) => [newJob, ...prev]);
    } catch (error) {
      console.error("Failed to launch job:", error);
      alert(`Failed to launch job: ${error.message}`);
    } finally {
      setTimeout(() => {
        setIsButtonPressed(false);
      }, 500);
    }
  };

  // Validation
  const getValidationErrors = () => {
    const errors = [];
    // check for valid workflow selections
    if (!selectedTasks.build && !selectedTasks.deploy && !selectedTasks.benchmark) {
      errors.push("Select at least one task");
    }
    if (selectedTasks.build && selectedTasks.benchmark && !selectedTasks.deploy) {
      errors.push("Build + Benchmark workflow requires Deploy");
    }
    // if the workflow is valid, check for required fields
    else {
      if (selectedTasks.build && !config.manifest_yml.trim()) {
        errors.push("Manifest YAML is required for build");
      }
      if (selectedTasks.deploy && !config.suffix) {
        errors.push("Deployment suffix is required");
      }
      if (selectedTasks.deploy && !selectedTasks.build && !config.distribution_url) {
        errors.push("Distribution URL required when not building");
      }
      if (selectedTasks.benchmark && !selectedTasks.deploy && !config.cluster_endpoint) {
        errors.push("Cluster endpoint required when not deploying");
      }
      if (!config.s3_bucket.trim()) {
        errors.push("S3 bucket name is required");
      }
    }
    
    return errors;
  };

  const validationErrors = getValidationErrors();
  const isLaunchDisabled = validationErrors.length > 0;
  const isWorkflowValid = !(
    selectedTasks.build &&
    selectedTasks.benchmark &&
    !selectedTasks.deploy
  );

  // display the UI
  return (
    <div className="page">
      <div className="header">
        <div className="header-content">
          <h1 className="header-title">
            <EuiIcon type="logoOpenSearch" size="l" /> OpenSearch Cluster Dev
            Tool
          </h1>
        </div>
      </div>

      <div className="container">
        {/* Job Configuration Component */}
        <JobConfiguration
          selectedTasks={selectedTasks}
          onTaskToggle={handleTaskToggle}
          config={config}
          onConfigChange={handleConfigChange}
          onLaunchJob={handleLaunchJob}
          validationErrors={validationErrors}
          isLaunchDisabled={isLaunchDisabled}
          isButtonPressed={isButtonPressed}
          isWorkflowValid={isWorkflowValid}
        />

        {/* Task History Component */}
        <TaskHistory
          jobs={jobs}
          isLoading={isLoadingJobs}
          onRefresh={fetchJobs}
          onDelete={handleDeleteJob}
        />
      </div>
    </div>
  );
}
