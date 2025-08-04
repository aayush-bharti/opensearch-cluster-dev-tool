/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import {
  EuiTitle,
  EuiText,
  EuiSpacer,
  EuiPanel,
  EuiAccordion,
  EuiFlexGroup,
  EuiFlexItem,
  EuiBadge,
  EuiCallOut,
} from "@opensearch-project/oui";
import { getStatusIcon, getStatusColor } from "../utils/statusUtils";

// JobStatus component
const JobStatus = ({ jobStatus, jobId }) => {
  if (!jobStatus) {
    return null;
  }

  // display the UI
  return (
    <>
      {/* Job Information */}
      <EuiTitle size="s">
        <h4>Job Information</h4>
      </EuiTitle>
      <EuiSpacer size="s" />
      <EuiPanel color="subdued" paddingSize="m" borderRadius="m">
        <EuiText size="s">
          <strong>Job ID:</strong> {jobId}
          <br />
          <strong>Status:</strong> {jobStatus.status}
          <br />
          <strong>Created:</strong>{" "}
          {jobStatus.created_at &&
            new Date(jobStatus.created_at).toLocaleString()}
          <br />
          {jobStatus.started_at && (
            <>
              <strong>Started:</strong>{" "}
              {new Date(jobStatus.started_at).toLocaleString()}
              <br />
            </>
          )}
          {jobStatus.completed_at && (
            <>
              <strong>Completed:</strong>{" "}
              {new Date(jobStatus.completed_at).toLocaleString()}
              <br />
            </>
          )}
          {jobStatus.workflow_timestamp && (
            <>
              <strong>Workflow Timestamp:</strong>{" "}
              {jobStatus.workflow_timestamp}
              <br />
            </>
          )}
        </EuiText>
      </EuiPanel>
      <EuiSpacer size="m" />

      {/* Task Status */}
      {jobStatus.tasks && (
        <>
          <EuiTitle size="s">
            <h4>Task Status</h4>
          </EuiTitle>
          <EuiSpacer size="s" />
          <EuiFlexGroup direction="column" gutterSize="m">
            {Object.entries(jobStatus.tasks).map(([taskName, taskData]) => (
              <EuiFlexItem key={taskName}>
                <EuiPanel color="subdued" paddingSize="m" borderRadius="m">
                  <EuiFlexGroup alignItems="center" gutterSize="m">
                    <EuiFlexItem grow={false}>
                      {getStatusIcon(taskData.status)}
                    </EuiFlexItem>
                    <EuiFlexItem grow={false}>
                      <EuiBadge
                        color={getStatusColor(taskData.status)}
                        style={{
                          borderRadius: "999px",
                          fontWeight: 600,
                          fontSize: "0.85rem",
                          letterSpacing: "0.03em",
                          padding: "0.25em 1em",
                        }}
                      >
                        {taskName.charAt(0).toUpperCase() + taskName.slice(1)}
                      </EuiBadge>
                    </EuiFlexItem>
                    <EuiFlexItem grow={false}>
                      <EuiBadge
                        color={getStatusColor(taskData.status)}
                        style={{
                          borderRadius: "999px",
                          fontSize: "0.75rem",
                          letterSpacing: "0.03em",
                          padding: "0.25em 0.75em",
                        }}
                      >
                        {taskData.status.toUpperCase()}
                      </EuiBadge>
                    </EuiFlexItem>
                    <EuiFlexItem>
                      <EuiText
                        size="s"
                        color="subdued"
                        style={{ marginRight: "225px" }}
                      >
                        {taskData.started_at && (
                          <>
                            Started:{" "}
                            {new Date(taskData.started_at).toLocaleTimeString()}{" "}
                          </>
                        )}
                        {taskData.completed_at && (
                          <>
                            | Completed:{" "}
                            {new Date(
                              taskData.completed_at
                            ).toLocaleTimeString()}
                          </>
                        )}
                      </EuiText>
                    </EuiFlexItem>
                  </EuiFlexGroup>
                  {taskData.result &&
                    (taskData.result.output ||
                      taskData.result.stdout ||
                      taskData.result.stderr ||
                      taskData.result.full_output) && (
                      <EuiAccordion
                        style={{ marginTop: 8 }}
                        id={`task-output-${jobId}-${taskName}`}
                        buttonContent={
                          <EuiText size="m">View Terminal Output</EuiText>
                        }
                        paddingSize="s"
                      >
                        <EuiText
                          size="xs"
                          style={{
                            background: "black",
                            color: "white",
                            borderRadius: 4,
                            fontFamily: "monospace",
                            fontSize: "0.8em",
                            maxHeight: 400,
                            overflowY: "auto",
                            overflowX: "auto",
                            whiteSpace: "pre-wrap",
                            border: "1px solid #333",
                            marginTop: 8,
                            marginBottom: 8,
                            padding: 12,
                          }}
                        >
                          {taskData.result.stdout && (
                            <>
                              <br />
                              {taskData.result.stdout}
                              <br />
                            </>
                          )}
                          {taskData.result.stderr &&
                            taskData.result.stderr.trim() && (
                              <>
                                <br />
                                {taskData.result.stderr}
                                <br />
                              </>
                            )}
                          {!taskData.result.stdout &&
                            !taskData.result.stderr &&
                            taskData.result.full_output && (
                              <>
                                <br />
                                {taskData.result.full_output}
                                <br />
                              </>
                            )}
                          {!taskData.result.stdout &&
                            !taskData.result.stderr &&
                            !taskData.result.full_output &&
                            taskData.result.output && (
                              <>
                                <br />
                                {taskData.result.output}
                                <br />
                              </>
                            )}
                        </EuiText>
                      </EuiAccordion>
                    )}
                  {taskData.error && (
                    <EuiCallOut title="Error" color="danger" iconType="alert">
                      {taskData.error}
                    </EuiCallOut>
                  )}
                </EuiPanel>
              </EuiFlexItem>
            ))}
          </EuiFlexGroup>
          <EuiSpacer size="m" />
        </>
      )}
    </>
  );
};

export default JobStatus;
