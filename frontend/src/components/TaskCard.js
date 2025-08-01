/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from "react";
import {
  EuiTitle,
  EuiText,
  EuiHorizontalRule,
  EuiSpacer,
  EuiPanel,
  EuiAccordion,
} from "@opensearch-project/oui";
import JobHeader from "./JobHeader";
import JobProgress from "./JobProgress";
import JobResults from "./JobResults";
import JobStatus from "./JobStatus";
import { useJobStatusPolling } from "./JobStatusPolling";

// TaskCard component
const TaskCard = ({ job, onDelete }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { jobStatus, logs } = useJobStatusPolling(job.jobId, job.id);

  // display the UI
  return (
    <EuiPanel paddingSize="l" borderRadius="l" hasShadow>
      {/* Job Header */}
      <JobHeader job={job} jobStatus={jobStatus} onDelete={onDelete} />

      {/* Job Progress */}
      <JobProgress jobStatus={jobStatus} />

      {/* Job Details */}
      <EuiSpacer size="m" />
      <EuiAccordion
        id={`job-details-${job.id}`}
        buttonContent={
          <EuiText size="l">
            {isExpanded ? "Hide Details" : "Show Details"}
          </EuiText>
        }
        isOpen={isExpanded}
        onToggle={() => setIsExpanded(!isExpanded)}
        paddingSize="m"
      >
        <EuiHorizontalRule margin="none" />
        <EuiSpacer size="m" />

        {/* Job Status Information */}
        <JobStatus jobStatus={jobStatus} jobId={job.jobId} />

        {/* Execution Logs */}
        <EuiTitle size="s">
          <h4>Execution Logs</h4>
        </EuiTitle>
        <EuiSpacer size="s" />
        <EuiText
          size="xs"
          style={{
            fontFamily: "monospace",
            maxHeight: 300,
            minHeight: 100,
            overflowY: "auto",
            overflowX: "auto",
            borderRadius: 4,
            padding: "1em",
            marginBottom: "1em",
          }}
        >
          <pre style={{ margin: 0, whiteSpace: "pre" }}>
            {logs
              .map((log, index) => `[${log.timestamp}] ${log.message}`)
              .join("\n")}
          </pre>
        </EuiText>

        {/* Results */}
        <JobResults jobStatus={jobStatus} jobId={job.id} />
      </EuiAccordion>
    </EuiPanel>
  );
};

export default TaskCard;
