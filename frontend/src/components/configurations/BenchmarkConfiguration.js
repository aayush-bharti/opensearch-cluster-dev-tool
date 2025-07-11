import React from "react";
import {
  EuiIcon,
  EuiFieldText,
  EuiFormRow,
  EuiSelect,
  EuiTitle,
  EuiFlexGroup,
  EuiPanel,
} from "@opensearch-project/oui";

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
        <EuiTitle
          size="l"
          style={{ color: "#2c3e50", fontSize: "1.75rem", fontWeight: "bold" }}
        >
          <h3>Benchmark Configuration</h3>
        </EuiTitle>
      </EuiFlexGroup>

      {/* Cluster Endpoint */}
      {!selectedTasks.deploy && (
        <div style={{ marginBottom: "1rem", width: "100%" }}>
          <EuiFormRow
            label={<span className="required-field">Cluster Endpoint</span>}
            fullWidth
            style={{ width: "100%" }}
          >
            <EuiFieldText
              fullWidth
              value={config.clusterEndpoint}
              onChange={onChange("clusterEndpoint")}
              placeholder={"Paste cluster endpoint here..."}
              isInvalid={
                selectedTasks.benchmark &&
                !selectedTasks.deploy &&
                !config.clusterEndpoint
              }
              style={{ width: "100%", minWidth: "100%" }}
            />
          </EuiFormRow>
        </div>
      )}

      {/* Workload Type */}
      {/* uses workloads from: https://github.com/opensearch-project/opensearch-benchmark-workloads */}
      <div style={{ marginBottom: "1rem", width: "100%" }}>
        <EuiFormRow label="Workload Type" fullWidth style={{ width: "100%" }}>
          <EuiSelect
            fullWidth
            value={config.workloadType}
            onChange={onChange("workloadType")}
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
            placeholder={"Choose workload type here..."}
            style={{ width: "100%", minWidth: "100%" }}
          />
        </EuiFormRow>
      </div>
    </EuiPanel>
  );
};

export default BenchmarkConfiguration;
