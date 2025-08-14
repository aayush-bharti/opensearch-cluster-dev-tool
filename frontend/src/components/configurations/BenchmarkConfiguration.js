/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import {
  EuiIcon,
  EuiFieldText,
  EuiFormRow,
  EuiSelect,
  EuiTitle,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPanel,
  EuiSpacer,
  EuiSwitch,
  EuiFieldNumber,
} from "@opensearch-project/oui";
import CustomParameters from "./CustomParameters";

const BenchmarkConfiguration = ({ config, onChange, selectedTasks }) => {
  return (
    <EuiPanel paddingSize="l" hasShadow borderRadius="m">
      <EuiFlexGroup
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          marginBottom: "1.5rem",
        }}
      >
        <EuiIcon type="visBarVertical" color="primary" />
        <EuiTitle size="l" style={{ fontSize: "1.75rem", fontWeight: "bold" }}>
          <h3>Benchmark Configuration</h3>
        </EuiTitle>
      </EuiFlexGroup>

      {/* Cluster Endpoint */}
      {!selectedTasks.deploy && (
        <EuiFormRow
          label={<span className="required-field">Cluster Endpoint</span>}
          fullWidth
        >
          <EuiFieldText
            fullWidth
            value={config.cluster_endpoint || ""}
            onChange={onChange("cluster_endpoint")}
            placeholder="Enter cluster endpoint..."
            isInvalid={selectedTasks.benchmark && !config.cluster_endpoint}
            style={{ width: "100%", minWidth: "100%" }}
          />
        </EuiFormRow>
      )}

      <EuiSpacer size="m" />

      {/* Workload Type and Pipeline */}
      {/* uses workloads from: https://github.com/opensearch-project/opensearch-benchmark-workloads */}
      <EuiFlexGroup gutterSize="l">
        <EuiFlexItem>
          <EuiFormRow label="Workload Type" fullWidth>
            <EuiSelect
              fullWidth
              value={config.workload_type}
              onChange={onChange("workload_type")}
              options={[
                { value: "big5", text: "big5" },
                { value: "eventdata", text: "eventdata" },
                { value: "geonames", text: "geonames" },
                { value: "geopoint", text: "geopoint" },
                { value: "http_logs", text: "http_logs" },
                { value: "nested", text: "nested" },
                { value: "noaa", text: "noaa" },
                { value: "nyc_taxis", text: "nyc_taxis" },
                { value: "percolator", text: "percolator" },
                { value: "pmc", text: "pmc" },
                { value: "so", text: "so" },
                { value: "vectorsearch", text: "vectorsearch" },
              ]}
              placeholder="Choose workload type here..."
              style={{ width: "100%", minWidth: "100%" }}
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow label="Pipeline" fullWidth>
            <EuiFieldText
              fullWidth
              value={config.pipeline}
              onChange={onChange("pipeline")}
              placeholder="Enter pipeline type (e.g., benchmark-only)"
              style={{ width: "100%", minWidth: "100%" }}
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <CustomParameters
        taskType="Benchmark"
        customParams={config.custom_benchmark_params || []}
        onChange={(params) =>
          onChange("custom_benchmark_params")({ target: { value: params } })
        }
        placeholder="Enter benchmark parameter (e.g., --client-options timeout:60s)"
      />

      <EuiSpacer size="l" />

      {/* EC2 Benchmark Configuration: show when deploy is selected with benchmark */}
      {/* {selectedTasks.deploy && selectedTasks.benchmark && ( */}
      {selectedTasks.benchmark && (
        <>
          <EuiTitle size="m">
            <h4>EC2 Benchmark Configuration (Optional)</h4>
          </EuiTitle>

          <EuiSpacer size="m" />

          <EuiFormRow>
            <EuiSwitch
              id="use-ec2-benchmark"
              label="Use EC2 Instance for Benchmark"
              checked={config.use_ec2_benchmark || false}
              onChange={(e) =>
                onChange("use_ec2_benchmark")({
                  target: { value: e.target.checked },
                })
              }
            />
          </EuiFormRow>
        </>
      )}

      {config.use_ec2_benchmark && (
        <>
          <EuiSpacer size="m" />

          <EuiFlexGroup gutterSize="l">
            <EuiFlexItem>
              <EuiFormRow label="Instance Type" fullWidth>
                <EuiSelect
                  fullWidth
                  value={config.instance_type || "t3.medium"}
                  onChange={onChange("instance_type")}
                  options={[
                    { value: "t3.medium", text: "t3.medium (x86)" },
                    { value: "t3.large", text: "t3.large (x86)" },
                    { value: "t3.xlarge", text: "t3.xlarge (x86)" },
                    { value: "t4g.medium", text: "t4g.medium (ARM)" },
                    { value: "t4g.large", text: "t4g.large (ARM)" },
                    { value: "t4g.xlarge", text: "t4g.xlarge (ARM)" },
                    { value: "c5.large", text: "c5.large (x86)" },
                    { value: "c5.xlarge", text: "c5.xlarge (x86)" },
                    { value: "c6g.large", text: "c6g.large (ARM)" },
                    { value: "c6g.xlarge", text: "c6g.xlarge (ARM)" },
                    { value: "c7g.large", text: "c7g.large (ARM)" },
                    { value: "c7g.xlarge", text: "c7g.xlarge (ARM)" },
                    { value: "m5.large", text: "m5.large (x86)" },
                    { value: "m5.xlarge", text: "m5.xlarge (x86)" },
                    { value: "m6g.large", text: "m6g.large (ARM)" },
                    { value: "m6g.xlarge", text: "m6g.xlarge (ARM)" },
                    { value: "m7g.large", text: "m7g.large (ARM)" },
                    { value: "m7g.xlarge", text: "m7g.xlarge (ARM)" },
                    { value: "r6g.large", text: "r6g.large (ARM)" },
                    { value: "r6g.xlarge", text: "r6g.xlarge (ARM)" },
                    { value: "r7g.large", text: "r7g.large (ARM)" },
                    { value: "r7g.xlarge", text: "r7g.xlarge (ARM)" },
                  ]}
                />
              </EuiFormRow>
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiFormRow label="Key Pair Name" fullWidth>
                <EuiFieldText
                  fullWidth
                  value={config.key_name || ""}
                  onChange={onChange("key_name")}
                  placeholder="Enter EC2 key pair name..."
                />
              </EuiFormRow>
            </EuiFlexItem>
          </EuiFlexGroup>

          <EuiSpacer size="m" />

          <EuiFlexGroup gutterSize="l">
            <EuiFlexItem>
              <EuiFormRow label="Subnet ID (Optional)" fullWidth>
                <EuiFieldText
                  fullWidth
                  value={config.subnet_id || ""}
                  onChange={onChange("subnet_id")}
                  placeholder="Leave empty to use AWS default VPC & subnet..."
                />
              </EuiFormRow>
            </EuiFlexItem>
            <EuiFlexItem>
              <EuiFormRow label="Your Public IP (Optional)" fullWidth>
                <EuiFieldText
                  fullWidth
                  value={config.my_ip || ""}
                  onChange={onChange("my_ip")}
                  placeholder="Not needed - using default security group"
                  disabled={true}
                />
              </EuiFormRow>
            </EuiFlexItem>
          </EuiFlexGroup>

          <EuiSpacer size="m" />

          {!selectedTasks.deploy && (
            <EuiFormRow label="Security Group ID" fullWidth>
              <EuiFieldText
                fullWidth
                value={config.security_group_id || ""}
                onChange={onChange("security_group_id")}
                placeholder="Enter security group ID..."
              />
            </EuiFormRow>
          )}

          <EuiSpacer size="m" />

          <EuiFormRow label="Timeout (minutes)" fullWidth>
            <EuiFieldNumber
              fullWidth
              value={config.timeout_minutes || 60}
              onChange={onChange("timeout_minutes")}
              min={1}
              max={480}
              placeholder="60"
            />
          </EuiFormRow>
        </>
      )}
    </EuiPanel>
  );
};

export default BenchmarkConfiguration;
