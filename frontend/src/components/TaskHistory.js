import React from "react";
import {
  EuiPanel,
  EuiTitle,
  EuiIcon,
  EuiText,
  EuiFlexGroup,
  EuiFlexItem,
  EuiLoadingSpinner,
  EuiButton,
  EuiSpacer,
} from "@opensearch-project/oui";
import TaskCard from "./TaskCard";

// TaskHistory component
const TaskHistory = ({ jobs, isLoading, onRefresh, onDelete }) => {
  // display the UI
  return (
    <EuiPanel paddingSize="l" hasShadow>
      {/* Task History Header */}
      <EuiFlexGroup direction="column" alignItems="center">
        {/* Task History Icon */}
        <EuiFlexItem grow={false}>
          <EuiIcon type="history" size="xl" color="primary" />
        </EuiFlexItem>
        <EuiFlexItem grow={false}>
          <EuiTitle size="l" style={{ fontSize: "2rem", fontWeight: "bold" }}>
            <h2>Task History</h2>
          </EuiTitle>
          <EuiText
            color="subdued"
            style={{ fontSize: "1rem", marginTop: "0.5rem" }}
          >
            View and monitor your job executions
          </EuiText>
        </EuiFlexItem>

        {/* Refresh Jobs Button */}
        {onRefresh && (
          <EuiFlexItem grow={false}>
            <EuiButton
              fill
              size="m"
              iconType="refresh"
              onClick={onRefresh}
              disabled={isLoading}
              style={{ fontSize: "1rem" }}
            >
              Refresh Jobs
            </EuiButton>
          </EuiFlexItem>
        )}

        {/* Task History Content */}
        <EuiSpacer size="m" />

        {/* Loading */}
        {isLoading ? (
          <EuiFlexItem
            grow={false}
            style={{ textAlign: "center", padding: "2rem" }}
          >
            <EuiLoadingSpinner size="xl" />
            <EuiText style={{ marginTop: "1rem" }}>
              Loading job history...
            </EuiText>
          </EuiFlexItem>
        ) : jobs.length > 0 ? (
          <EuiFlexItem grow={false} style={{ width: "100%" }}>
            <EuiFlexGroup direction="column" gutterSize="m">
              {jobs.map((job) => (
                <EuiFlexItem key={job.id}>
                  <TaskCard job={job} onDelete={onDelete} />
                </EuiFlexItem>
              ))}
            </EuiFlexGroup>
          </EuiFlexItem>
        ) : (
          <EuiFlexItem grow={false} style={{ textAlign: "center" }}>
            <EuiTitle size="s">
              <h4>No tasks have been run yet</h4>
            </EuiTitle>
            <EuiText color="subdued">
              Configure and launch a job above to see results here.
            </EuiText>
          </EuiFlexItem>
        )}
      </EuiFlexGroup>
    </EuiPanel>
  );
};

export default TaskHistory;
