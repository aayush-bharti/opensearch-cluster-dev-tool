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
    manifest: "",

    // deploy config
    suffix: "",
    distributionUrl: "",
    minDistribution: "false",
    securityDisabled: true,
    cpuArch: "arm64",
    singleNodeCluster: false,
    dataInstanceType: "r6g.large",
    dataNodeCount: 3,
    distVersion: "3.0.0",
    use50PercentHeap: true,
    isInternal: false,

    // benchmark config
    clusterEndpoint: "",
    workloadType: "percolator",
    pipeline: "benchmark-only",
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
      const workflowResponse = await fetch(
        `${API_ENDPOINTS.WORKFLOW}?${queryParams}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            // Build config
            ...(selectedTasks.build && { manifest_yml: config.manifest }),

            // Deploy config
            ...(selectedTasks.deploy && {
              suffix: config.suffix,
              ...(config.distributionUrl && {
                distribution_url: config.distributionUrl,
              }),
              security_disabled: config.securityDisabled,
              cpu_arch: config.cpuArch,
              data_instance_type: config.dataInstanceType,
              data_node_count: config.dataNodeCount,
              dist_version: config.distVersion,
              min_distribution: config.minDistribution,
              single_node_cluster: config.singleNodeCluster,
              server_access_type: config.serverAccessType,
              restrict_server_access_to: config.restrictServerAccessTo,
              use_50_percent_heap: config.use50PercentHeap !== false,
              is_internal: config.isInternal,
            }),

            // Benchmark config
            ...(selectedTasks.benchmark && {
              ...(config.clusterEndpoint && {
                cluster_endpoint: config.clusterEndpoint,
              }),
              workload_type: config.workloadType,
              pipeline: "benchmark-only",
            }),
          }),
        }
      );

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
    if (
      !selectedTasks.build &&
      !selectedTasks.deploy &&
      !selectedTasks.benchmark
    ) {
      errors.push("Select at least one task");
    }
    if (
      selectedTasks.build &&
      selectedTasks.benchmark &&
      !selectedTasks.deploy
    ) {
      errors.push("Build + Benchmark workflow requires Deploy");
    }
    // if the workflow is valid, check for required fields
    else {
      if (selectedTasks.build && !config.manifest.trim()) {
        errors.push("Manifest YAML is required for build");
      }
      if (selectedTasks.deploy && !config.suffix) {
        errors.push("Deployment suffix is required");
      }
      if (
        selectedTasks.deploy &&
        !selectedTasks.build &&
        !config.distributionUrl
      ) {
        errors.push("Distribution URL required");
      }
      if (
        selectedTasks.benchmark &&
        !selectedTasks.deploy &&
        !config.clusterEndpoint
      ) {
        errors.push("Cluster endpoint required");
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
