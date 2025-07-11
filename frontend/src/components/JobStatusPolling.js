import { useState, useEffect, useCallback, useRef } from "react";

// API Endpoint Constants
const API_BASE_URL = "http://localhost:8000";
const API_ENDPOINTS = {
  JOBS: `${API_BASE_URL}/api/cluster/jobs`,
  JOB_DETAILS: (jobId) => `${API_BASE_URL}/api/cluster/jobs/${jobId}`,
  JOB_DELETE: (jobId) => `${API_BASE_URL}/api/cluster/jobs/${jobId}/delete`,
  JOB_CANCEL: (jobId) => `${API_BASE_URL}/api/cluster/jobs/${jobId}/cancel`,
  WORKFLOW: `${API_BASE_URL}/api/cluster/workflow`,
};

// useJobStatusPolling hook 
export const useJobStatusPolling = (jobId, jobDisplayId) => {
  const [jobStatus, setJobStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const intervalRef = useRef(null);
  const hasInitializedRef = useRef(false);

  const addLog = useCallback((message, type = "info") => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prevLogs) => [...prevLogs, { timestamp, message, type }]);
  }, []);

  // poll job status
  const pollJobStatus = useCallback(async () => {
    if (!jobId) return;
    try {
      const response = await fetch(API_ENDPOINTS.JOB_DETAILS(jobId));
      if (response.ok) {
        const data = await response.json();
        setJobStatus(data);
        if (!hasInitializedRef.current) {
          addLog(`Job #${jobDisplayId} loaded with status: ${data.status}`);
          hasInitializedRef.current = true;
          if (data.status === "completed") {
            addLog(`✅ Job #${jobDisplayId} completed successfully!`);
          } else if (data.status === "failed") {
            addLog(
              `❌ Job #${jobDisplayId} failed: ${data.error || "Unknown error"}`
            );
          } else if (data.status === "cancelled") {
            addLog(`🚫 Job #${jobDisplayId} was cancelled`);
          }
        }
      } else {
        console.error("Failed to fetch job status:", response.status);
      }
    } catch (error) {
      console.error("Error polling job status:", error);
    }
  }, [jobId, jobDisplayId, addLog]);

  // poll job status
  useEffect(() => {
    if (jobId && !intervalRef.current) {
      pollJobStatus();
      intervalRef.current = setInterval(pollJobStatus, 60000);
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [jobId, pollJobStatus]);

  // stop polling job status
  useEffect(() => {
    if (
      jobStatus &&
      ["completed", "failed", "cancelled"].includes(jobStatus.status)
    ) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
  }, [jobStatus]);

  // display the UI
  return {
    jobStatus,
    logs,
    addLog,
  };
};
