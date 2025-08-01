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
    </EuiPanel>
  );
};

export default BenchmarkConfiguration;
