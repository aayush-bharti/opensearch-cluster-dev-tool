import React from "react";
import {
  EuiIcon,
  EuiFieldText,
  EuiFormRow,
  EuiSelect,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPanel,
  EuiSpacer,
  EuiTitle,
} from "@opensearch-project/oui";

// deploy config component
const DeployConfiguration = ({ config, onChange, selectedTasks }) => {
  // display the UI
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
        <EuiIcon type="redeploy" color="primary" />
        <EuiTitle
          size="l"
          style={{ color: "#2c3e50", fontSize: "1.75rem", fontWeight: "bold" }}
        >
          <h3>Deploy Configuration</h3>
        </EuiTitle>
      </EuiFlexGroup>

      {/* distribution url input */}
      <EuiFlexGroup direction="column" gutterSize="xl">
        {!selectedTasks.build && (
          <EuiFlexItem grow={false}>
            <EuiFormRow
              label={<span className="required-field">Distribution URL</span>}
              fullWidth
            >
              <EuiFieldText
                fullWidth
                value={config.distributionUrl}
                onChange={onChange("distributionUrl")}
                placeholder={"Paste distribution URL here..."}
                isInvalid={
                  selectedTasks.deploy &&
                  !selectedTasks.build &&
                  !config.distributionUrl
                }
              />
            </EuiFormRow>
          </EuiFlexItem>
        )}

        {/* deployment suffix input */}
        <EuiSpacer size="m" />
        <EuiFlexGroup gutterSize="m" style={{ marginLeft: "15px" }}>
          <EuiFlexItem>
            <EuiFormRow
              label={<span className="required-field">Deployment Suffix</span>}
              style={{ maxWidth: "490px" }}
            >
              <EuiFieldText
                fullWidth
                value={config.suffix}
                onChange={onChange("suffix")}
                placeholder={"Paste suffix here..."}
                isInvalid={selectedTasks.deploy && !config.suffix}
              />
            </EuiFormRow>
          </EuiFlexItem>

          {/* data instance type input */}
          <EuiFlexItem>
            <EuiFormRow
              label="Data Instance Type"
              style={{ maxWidth: "490px" }}
            >
              <EuiFieldText
                fullWidth
                value={config.dataInstanceType}
                onChange={onChange("dataInstanceType")}
              />
            </EuiFormRow>
          </EuiFlexItem>
        </EuiFlexGroup>

        {/* distribution version input */}
        <EuiSpacer size="l" />
        <EuiFlexGroup gutterSize="m" style={{ marginLeft: "15px" }}>
          <EuiFlexItem>
            <EuiFormRow
              label="Distribution Version"
              style={{ maxWidth: "490px" }}
            >
              <EuiFieldText
                fullWidth
                value={config.distVersion}
                onChange={onChange("distVersion")}
                placeholder={"Paste distribution version here..."}
              />
            </EuiFormRow>
          </EuiFlexItem>

          {/* data node count input */}
          <EuiFlexItem>
            <EuiFormRow label="Data Node Count" style={{ maxWidth: "490px" }}>
              <EuiFieldText
                fullWidth
                type="number"
                value={config.dataNodeCount}
                onChange={onChange("dataNodeCount")}
                min={1}
                max={20}
              />
            </EuiFormRow>
          </EuiFlexItem>
        </EuiFlexGroup>

        {/* cpu architecture input */}
        <EuiSpacer size="m" />
        <EuiFlexItem grow={false}>
          <EuiFormRow label="CPU Architecture" fullWidth>
            <EuiSelect
              fullWidth
              value={config.cpuArch}
              onChange={onChange("cpuArch")}
              options={[
                { value: "arm64", text: "ARM64" },
                { value: "x64", text: "x64" },
                { value: "x86_64", text: "x86_64" },
              ]}
            />
          </EuiFormRow>
        </EuiFlexItem>

        {/* security disabled input */}
        <EuiSpacer size="m" />
        <EuiFlexGroup gutterSize="m" style={{ marginLeft: "15px" }}>
          <EuiFlexItem>
            <EuiFormRow label="Security Disabled" style={{ maxWidth: "490px" }}>
              <EuiSelect
                fullWidth
                value={config.securityDisabled ? "true" : "false"}
                onChange={(e) =>
                  onChange("securityDisabled")({
                    target: { value: e.target.value === "true" },
                  })
                }
                options={[
                  { value: "true", text: "True" },
                  { value: "false", text: "False" },
                ]}
              />
            </EuiFormRow>
          </EuiFlexItem>

          {/* single node cluster input */}
          <EuiFlexItem>
            <EuiFormRow
              label="Single Node Cluster"
              style={{ maxWidth: "490px" }}
            >
              <EuiSelect
                fullWidth
                value={config.singleNodeCluster ? "true" : "false"}
                onChange={(e) =>
                  onChange("singleNodeCluster")({
                    target: { value: e.target.value === "true" },
                  })
                }
                options={[
                  { value: "false", text: "False" },
                  { value: "true", text: "True" },
                ]}
              />
            </EuiFormRow>
          </EuiFlexItem>
        </EuiFlexGroup>

        {/* use 50% heap input */}
        <EuiSpacer size="l" />
        <EuiFlexGroup
          gutterSize="m"
          style={{ marginLeft: "15px", marginBottom: "10px" }}
        >
          <EuiFlexItem>
            <EuiFormRow label="Use 50% Heap" style={{ maxWidth: "490px" }}>
              <EuiSelect
                fullWidth
                value={config.use50PercentHeap ? "true" : "false"}
                onChange={(e) =>
                  onChange("use50PercentHeap")({
                    target: { value: e.target.value === "true" },
                  })
                }
                options={[
                  { value: "true", text: "True" },
                  { value: "false", text: "False" },
                ]}
              />
            </EuiFormRow>
          </EuiFlexItem>

          {/* minimum distribution input */}
          <EuiFlexItem>
            <EuiFormRow
              label="Minimum Distribution"
              style={{ maxWidth: "490px" }}
            >
              <EuiSelect
                fullWidth
                value={config.minDistribution}
                onChange={onChange("minDistribution")}
                options={[
                  { value: "false", text: "False" },
                  { value: "true", text: "True" },
                ]}
              />
            </EuiFormRow>
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiFlexGroup>
    </EuiPanel>
  );
};

export default DeployConfiguration;
