/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import {
  EuiIcon,
  EuiText,
  EuiButton,
  EuiFlexGroup,
  EuiFlexItem,
  EuiTitle,
} from "@opensearch-project/oui";
import BuildConfiguration from "./configurations/BuildConfiguration";
import DeployConfiguration from "./configurations/DeployConfiguration";
import BenchmarkConfiguration from "./configurations/BenchmarkConfiguration";
import S3Configuration from "./configurations/S3Configuration";

// JobConfiguration component
const JobConfiguration = ({
  selectedTasks,
  onTaskToggle,
  config,
  onConfigChange,
  onLaunchJob,
  validationErrors,
  isLaunchDisabled,
  isButtonPressed,
  isWorkflowValid,
}) => {
  // display the UI
  return (
    <div className="card">
      <EuiFlexGroup direction="column" alignItems="center" gutterSize="m">
        <EuiIcon type="gear" color="primary" size="xl" />
        <EuiTitle size="l" style={{ fontSize: "2rem", fontWeight: "bold" }}>
          <h2>Configure New Job</h2>
        </EuiTitle>
        <EuiText
          color="subdued"
          style={{ fontSize: "1rem", marginTop: "0.5rem" }}
        >
          Select tasks and configure settings for your OpenSearch workflow
        </EuiText>
      </EuiFlexGroup>

      {/* AWS Credentials Info */}
      <div className="info-callout">
        <EuiFlexGroup alignItems="center" gutterSize="m">
          <EuiFlexItem grow={false}></EuiFlexItem>
          <EuiFlexItem>
            <EuiText>
              <strong>AWS Credentials Required:</strong> This tool reads
              credentials from your <code>~/.aws/credentials</code> file. Please
              ensure you have run <code>aws configure</code> to set up your
              credentials.
            </EuiText>
          </EuiFlexItem>
        </EuiFlexGroup>
      </div>

      {/* Task Selection */}
      <div className="info-callout">
        <EuiText size="l">
          <strong>Valid Workflows:</strong> Build; Deploy; Benchmark;
          Build+Deploy; Deploy+Benchmark; Build+Deploy+Benchmark
        </EuiText>
      </div>

      <div className="task-selector">
        {Object.keys(selectedTasks).map((task) => (
          <div
            key={task}
            className={`task-option ${selectedTasks[task] ? "selected" : ""}`}
            onClick={() => onTaskToggle(task)}
          >
            <EuiFlexGroup
              direction="column"
              alignItems="center"
              gutterSize="xs"
            >
              {task === "build" && (
                <EuiIcon type="package" color="primary" size="l" />
              )}
              {task === "deploy" && (
                <EuiIcon type="redeploy" color="primary" size="l" />
              )}
              {task === "benchmark" && (
                <EuiIcon type="visBarVertical" color="primary" size="l" />
              )}
            </EuiFlexGroup>
            <EuiText
              size="m"
              color="text"
              style={{
                fontSize: "1.125rem",
                fontWeight: "600",
                margin: "0.5rem 0",
              }}
            >
              {task.charAt(0).toUpperCase() + task.slice(1)}
            </EuiText>
            <EuiText
              size="m"
              color="subdued"
              style={{ fontSize: "0.875rem", lineHeight: "1.4" }}
            >
              {task === "build" && "Build OpenSearch Cluster from source"}
              {task === "deploy" && "Deploy OpenSearch Cluster to AWS"}
              {task === "benchmark" && "Run OpenSearch Benchmarks"}
            </EuiText>
          </div>
        ))}
      </div>

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="error-callout">
          <EuiText>
            <strong>Configuration Issues:</strong>
            <ul style={{ margin: "0.5rem 0" }}>
              {validationErrors.map((error, index) => (
                <EuiText size="m" key={index}>
                  {error}
                </EuiText>
              ))}
            </ul>
          </EuiText>
        </div>
      )}

      {/* Configuration Forms */}
      {isWorkflowValid && (
        <>
          {selectedTasks.build && (
            <div style={{ marginBottom: "1rem" }}>
              <BuildConfiguration
                config={config}
                onChange={onConfigChange}
                selectedTasks={selectedTasks}
              />
            </div>
          )}
          {selectedTasks.deploy && (
            <div style={{ marginBottom: "1rem" }}>
              <DeployConfiguration
                config={config}
                onChange={onConfigChange}
                selectedTasks={selectedTasks}
              />
            </div>
          )}
          {selectedTasks.benchmark && (
            <div style={{ marginBottom: "1rem" }}>
              <BenchmarkConfiguration
                config={config}
                onChange={onConfigChange}
                selectedTasks={selectedTasks}
              />
            </div>
          )}

          {/* S3 Configuration */}
          <div style={{ marginBottom: "1rem" }}>
            <S3Configuration config={config} onChange={onConfigChange} />
          </div>

          {/* Launch Button */}
          <div style={{ textAlign: "center", marginTop: "2rem" }}>
            <EuiButton
              fill
              size="m"
              onClick={onLaunchJob}
              isDisabled={isLaunchDisabled || isButtonPressed}
              style={{ width: "20%", fontSize: "1.2rem" }}
              iconType="playFilled"
              iconSize="l"
            >
              {isButtonPressed ? "Launching..." : "Launch Job"}
            </EuiButton>
          </div>
        </>
      )}
    </div>
  );
};

export default JobConfiguration;
