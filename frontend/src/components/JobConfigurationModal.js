/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import {
  EuiModal,
  EuiModalHeader,
  EuiModalHeaderTitle,
  EuiModalBody,
  EuiModalFooter,
  EuiButton,
  EuiText,
  EuiSpacer,
  EuiPanel,
  EuiTitle,
  EuiFlexGroup,
  EuiFlexItem,
  EuiBadge,
  EuiHorizontalRule,
} from "@opensearch-project/oui";

// handles the job configuration in the task history section
// for each job, it shows the configuration that was selected for the task
const JobConfigurationModal = ({ isVisible, onClose, job }) => {
  if (!isVisible || !job) return null;

  const formatConfigValue = (value) => {
    if (typeof value === "boolean") {
      return value ? "True" : "False";
    }
    if (value === null || value === undefined) {
      return "Not set";
    }
    if (typeof value === "string" && value.trim() === "") {
      return "Not set";
    }
    return value.toString();
  };

  const renderConfigSection = (title, config, fields, taskName) => {
    // Only show section if the task was selected for this job
    if (taskName !== null && !job.tasks[taskName]) {
      return null;
    }

    const hasConfig = fields.some(
      (field) =>
        config[field] !== undefined &&
        config[field] !== null &&
        config[field] !== ""
    );

    if (!hasConfig) return null;

    return (
      <EuiPanel
        paddingSize="m"
        hasShadow={false}
        style={{ marginBottom: "1rem" }}
      >
        <EuiTitle size="s">
          <h4>{title}</h4>
        </EuiTitle>
        <EuiSpacer size="s" />
        <EuiFlexGroup direction="column" gutterSize="s">
          {fields.map((field) => {
            const value = config[field];
            if (
              value === undefined ||
              value === null ||
              (typeof value === "string" && value.trim() === "")
            ) {
              return null;
            }

            return (
              <EuiFlexItem key={field}>
                <EuiFlexGroup alignItems="center" gutterSize="m">
                  <EuiFlexItem grow={false}>
                    <EuiText
                      size="s"
                      style={{ fontWeight: "bold", minWidth: "120px" }}
                    >
                      {field === "manifest_yml"
                        ? "Manifest YAML"
                        : field === "s3_bucket"
                        ? "S3 Bucket"
                        : field
                            .replace(/([A-Z])/g, " $1")
                            .replace(/^./, (str) => str.toUpperCase())}
                      :
                    </EuiText>
                  </EuiFlexItem>
                  <EuiFlexItem>
                    <EuiText size="s">
                      {field === "manifest_yml" ? (
                        <div
                          style={{
                            backgroundColor: "#f8f9fa",
                            padding: "8px",
                            borderRadius: "4px",
                            fontFamily: "monospace",
                            fontSize: "0.8em",
                            maxHeight: "200px",
                            overflowY: "auto",
                            whiteSpace: "pre-wrap",
                          }}
                        >
                          {value}
                        </div>
                      ) : (
                        formatConfigValue(value)
                      )}
                    </EuiText>
                  </EuiFlexItem>
                </EuiFlexGroup>
              </EuiFlexItem>
            );
          })}
        </EuiFlexGroup>
      </EuiPanel>
    );
  };

  const buildFields = ["manifest_yml"];
  const deployFields = [
    "distribution_url",
    "suffix",
    "security_disabled",
    "cpu_arch",
    "single_node_cluster",
    "data_instance_type",
    "data_node_count",
    "dist_version",
    "min_distribution",
    "server_access_type",
    "restrict_server_access_to",
    "use_50_percent_heap",
    "is_internal",
    "admin_password",
  ];
  const benchmarkFields = ["cluster_endpoint", "workload_type", "pipeline"];
  const s3Fields = ["s3_bucket"];

  return (
    <EuiModal onClose={onClose} maxWidth={800}>
      <EuiModalHeader>
        <EuiModalHeaderTitle>
          Job #{job.displayId} Configuration
        </EuiModalHeaderTitle>
      </EuiModalHeader>

      <EuiModalBody>
        <EuiText size="s" color="subdued">
          Configuration used for this job execution
        </EuiText>
        <EuiSpacer size="m" />

        {/* Selected Tasks */}
        <EuiPanel
          paddingSize="m"
          hasShadow={false}
          style={{ marginBottom: "1rem" }}
        >
          <EuiTitle size="s">
            <h4>Selected Tasks</h4>
          </EuiTitle>
          <EuiSpacer size="s" />
          <EuiFlexGroup gutterSize="s">
            {Object.entries(job.tasks).map(([task, isSelected]) => (
              <EuiFlexItem grow={false} key={task}>
                <EuiBadge
                  color={isSelected ? "primary" : "hollow"}
                  style={{ borderRadius: "999px" }}
                >
                  {task.charAt(0).toUpperCase() + task.slice(1)}
                </EuiBadge>
              </EuiFlexItem>
            ))}
          </EuiFlexGroup>
        </EuiPanel>

        {/* Build Configuration */}
        {renderConfigSection(
          "Build Configuration",
          job.config,
          buildFields,
          "build"
        )}

        {/* Deploy Configuration */}
        {renderConfigSection(
          "Deploy Configuration",
          job.config,
          deployFields,
          "deploy"
        )}

        {/* Benchmark Configuration */}
        {renderConfigSection(
          "Benchmark Configuration",
          job.config,
          benchmarkFields,
          "benchmark"
        )}

        {/* S3 Configuration */}
        {renderConfigSection("S3 Configuration", job.config, s3Fields, null)}

        {/* Job Metadata */}
        <EuiHorizontalRule margin="m" />
        <EuiPanel paddingSize="s" hasShadow={false}>
          <EuiText size="s" color="subdued">
            <strong>Job ID:</strong> {job.jobId}
            <br />
            <strong>Created:</strong> {job.timestamp}
          </EuiText>
        </EuiPanel>
      </EuiModalBody>

      <EuiModalFooter>
        <EuiButton onClick={onClose} fill>
          Close
        </EuiButton>
      </EuiModalFooter>
    </EuiModal>
  );
};

export default JobConfigurationModal;
