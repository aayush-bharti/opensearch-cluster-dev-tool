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
} from "@opensearch-project/oui";
import BenchmarkResultsTable from "./BenchmarkResultsTable";

// JobResults component
const JobResults = ({ jobStatus, jobId }) => {
  if (
    !jobStatus ||
    !jobStatus.results ||
    Object.keys(jobStatus.results).length === 0
  ) {
    return null;
  }

  // display the UI
  return (
    <>
      <EuiSpacer size="m" />
      <EuiTitle size="s">
        <h4>Results</h4>
      </EuiTitle>
      <EuiSpacer size="s" />

      {/* Build Results */}
      {jobStatus.results.build && (
        <EuiAccordion
          id={`build-output-${jobId}`}
          buttonContent={<EuiText size="m">Build Output</EuiText>}
          paddingSize="s"
        >
          <EuiPanel
            color="success"
            paddingSize="s"
            borderRadius="m"
            style={{ marginTop: 8 }}
          >
            <strong>✅ Build completed successfully!</strong>
            <br />
            <strong>Status:</strong> {jobStatus.results.build.status}
            <br />
            <strong>Message:</strong> {jobStatus.results.build.message}
            <br />
          </EuiPanel>

          {/* Results Summary */}
          <EuiPanel
            color="success"
            paddingSize="s"
            borderRadius="m"
            style={{ marginTop: 8 }}
          >
            <EuiText size="m">
              <strong>Bucket:</strong>{" "}
              {jobStatus.results.build.output_s3_info?.bucket_name ? (
                jobStatus.results.build.output_s3_info.bucket_name
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - S3 bucket information not found
                </span>
              )}
              <br />
              <strong>Upload Timestamp:</strong>{" "}
              {jobStatus.results.build.output_s3_info?.timestamp ? (
                jobStatus.results.build.output_s3_info.timestamp
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - upload timestamp not recorded
                </span>
              )}
              <br />
              <strong>Results S3 URI:</strong>{" "}
              {jobStatus.results.build.results_s3_uri ? (
                <code>{jobStatus.results.build.results_s3_uri}</code>
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - results S3 URI not found
                </span>
              )}
              <br />
              <strong>Terminal Output S3 URI:</strong>{" "}
              {jobStatus.results.build.output_s3_info?.s3_uri ? (
                <code>{jobStatus.results.build.output_s3_info.s3_uri}</code>
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - terminal output S3 URI not found
                </span>
              )}
              <br />
              <strong>Build Artifact S3 URI:</strong>{" "}
              {jobStatus.results.build.s3_info?.s3_uri ? (
                <code>{jobStatus.results.build.s3_info.s3_uri}</code>
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - build artifact S3 URI not found
                </span>
              )}
              <br />
            </EuiText>
          </EuiPanel>
        </EuiAccordion>
      )}

      {/* Deploy Results */}
      {jobStatus.results.deploy && (
        <EuiAccordion
          id={`deploy-output-${jobId}`}
          buttonContent={<EuiText size="m">Deploy Output</EuiText>}
          paddingSize="s"
        >
          <EuiPanel
            color="success"
            paddingSize="s"
            borderRadius="m"
            style={{ marginTop: 8 }}
          >
            <EuiText size="m">
              <strong>✅ Deployment completed successfully!</strong>
              <br />
              <strong>Status:</strong> {jobStatus.results.deploy.status}
              <br />
              <strong>Message:</strong> {jobStatus.results.deploy.message}
              <br />
            </EuiText>
          </EuiPanel>

          {/* Cluster Information */}
          <EuiPanel
            color="success"
            paddingSize="s"
            borderRadius="m"
            style={{ marginTop: 8 }}
          >
            <EuiText size="m">
              <strong>Cluster Information:</strong>
              <br />
              <strong>Total Time:</strong>{" "}
              {jobStatus.results.deploy.cluster_info?.total_time ? (
                jobStatus.results.deploy.cluster_info.total_time
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - timing data could not be captured
                </span>
              )}
              <br />
              <strong>Deployment Time:</strong>{" "}
              {jobStatus.results.deploy.cluster_info?.deployment_time ? (
                jobStatus.results.deploy.cluster_info.deployment_time
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - deployment timing not recorded
                </span>
              )}
              <br />
              <strong>Stack Name:</strong>{" "}
              {jobStatus.results.deploy.cluster_info?.stack_name ? (
                jobStatus.results.deploy.cluster_info.stack_name
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - stack name not found in output
                </span>
              )}
              <br />
              <strong>Cluster Endpoint:</strong>{" "}
              {jobStatus.results.deploy.cluster_info?.cluster_endpoint ? (
                <a
                  href={jobStatus.results.deploy.cluster_info.cluster_endpoint}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {jobStatus.results.deploy.cluster_info.cluster_endpoint}
                </a>
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - endpoint not found in deployment output
                </span>
              )}
              <br />
            </EuiText>
          </EuiPanel>

          {/* Results Summary */}
          <EuiPanel
            color="success"
            paddingSize="s"
            borderRadius="m"
            style={{ marginTop: 8 }}
          >
            <EuiText size="m">
              <strong>Bucket:</strong>{" "}
              {jobStatus.results.deploy.output_s3_info?.bucket_name ? (
                jobStatus.results.deploy.output_s3_info.bucket_name
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - S3 bucket information not found
                </span>
              )}
              <br />
              <strong>Upload Timestamp:</strong>{" "}
              {jobStatus.results.deploy.output_s3_info?.timestamp ? (
                jobStatus.results.deploy.output_s3_info.timestamp
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - upload timestamp not recorded
                </span>
              )}
              <br />
              <strong>Results S3 URI:</strong>{" "}
              {jobStatus.results.deploy.s3_info?.results_s3_uri ? (
                <code>{jobStatus.results.deploy.s3_info.results_s3_uri}</code>
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - results S3 URI not found
                </span>
              )}
              <br />
              <strong>Terminal Output S3 URI:</strong>{" "}
              {jobStatus.results.deploy.output_s3_info?.s3_uri ? (
                <code>{jobStatus.results.deploy.output_s3_info.s3_uri}</code>
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - terminal output S3 URI not found
                </span>
              )}
              <br />
            </EuiText>
          </EuiPanel>
        </EuiAccordion>
      )}

      {/* Benchmark Results */}
      {jobStatus.results.benchmark && (
        <EuiAccordion
          id={`benchmark-output-${jobId}`}
          buttonContent={<EuiText size="m">Benchmark Output</EuiText>}
          paddingSize="s"
        >
          <EuiPanel
            color="success"
            paddingSize="s"
            borderRadius="m"
            style={{ marginTop: 8 }}
          >
            <EuiText size="m">
              <strong>✅ Benchmark completed successfully!</strong>
              <br />
              <strong>Status:</strong> {jobStatus.results.benchmark.status}
              <br />
              <strong>Message:</strong> {jobStatus.results.benchmark.message}
              <br />
              <strong>Benchmark ID:</strong>{" "}
              {jobStatus.results.benchmark.benchmark_id ? (
                jobStatus.results.benchmark.benchmark_id
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - benchmark ID not generated
                </span>
              )}
              <br />
            </EuiText>
          </EuiPanel>

          {/* Results Summary */}
          <EuiPanel
            color="success"
            paddingSize="s"
            borderRadius="m"
            style={{ marginTop: 8 }}
          >
            <EuiText size="m">
              <strong>Bucket:</strong>{" "}
              {jobStatus.results.benchmark.output_s3_info?.bucket_name ? (
                jobStatus.results.benchmark.output_s3_info.bucket_name
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - S3 bucket information not found
                </span>
              )}
              <br />
              <strong>Upload Timestamp:</strong>{" "}
              {jobStatus.results.benchmark.output_s3_info?.timestamp ? (
                jobStatus.results.benchmark.output_s3_info.timestamp
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - upload timestamp not recorded
                </span>
              )}
              <br />
              <strong>Results S3 URI:</strong>{" "}
              {jobStatus.results.benchmark.results_s3_uri ? (
                <code>{jobStatus.results.benchmark.results_s3_uri}</code>
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - results S3 URI not found
                </span>
              )}
              <br />
              <strong>Terminal Output S3 URI:</strong>{" "}
              {jobStatus.results.benchmark.output_s3_info?.s3_uri ? (
                <code>{jobStatus.results.benchmark.output_s3_info.s3_uri}</code>
              ) : (
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Not available - terminal output S3 URI not found
                </span>
              )}
              <br />
            </EuiText>
          </EuiPanel>

          {/* Benchmark Table */}
          {jobStatus.results.benchmark.results_file_content ? (
            <EuiAccordion
              id={`benchmark-results-file-${jobId}`}
              buttonContent={
                <EuiText size="m">View Benchmark Results Table</EuiText>
              }
              paddingSize="s"
            >
              <EuiPanel
                color="subdued"
                paddingSize="s"
                borderRadius="m"
                style={{ marginTop: 8 }}
              >
                <EuiText
                  size="xs"
                  style={{
                    fontFamily: "monospace",
                    maxHeight: 400,
                    overflowY: "auto",
                    borderRadius: 4,
                    padding: "1em",
                  }}
                >
                  <BenchmarkResultsTable
                    resultsText={
                      jobStatus.results.benchmark.results_file_content
                    }
                  />
                </EuiText>
              </EuiPanel>
            </EuiAccordion>
          ) : (
            <EuiPanel
              color="subdued"
              paddingSize="s"
              borderRadius="m"
              style={{ marginTop: 8 }}
            >
              <EuiText size="m">
                <span style={{ color: "subdued", fontStyle: "italic" }}>
                  Benchmark results file not available - results may not have
                  been generated or uploaded
                </span>
              </EuiText>
            </EuiPanel>
          )}
        </EuiAccordion>
      )}
    </>
  );
};

export default JobResults;
