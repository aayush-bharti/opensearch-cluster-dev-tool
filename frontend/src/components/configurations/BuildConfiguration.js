import React from "react";
import {
  EuiIcon,
  EuiFormRow,
  EuiTextArea,
  EuiTitle,
  EuiFlexGroup,
  EuiPanel,
} from "@opensearch-project/oui";

// build config component
const BuildConfiguration = ({ config, onChange, selectedTasks }) => {
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
        <EuiIcon type="package" color="primary" />
        <EuiTitle
          size="l"
          style={{ color: "#2c3e50", fontSize: "1.75rem", fontWeight: "bold" }}
        >
          <h3>Build Configuration</h3>
        </EuiTitle>
      </EuiFlexGroup>

      <EuiFormRow
        label={<span className="required-field">Manifest YAML</span>}
        fullWidth
      >
        <EuiTextArea
          fullWidth
          rows={12}
          value={config.manifest}
          onChange={onChange("manifest")}
          placeholder={"Paste your manifest YAML here..."}
          isInvalid={selectedTasks.build && !config.manifest.trim()}
          className="manifest-textarea"
        />
      </EuiFormRow>
    </EuiPanel>
  );
};

export default BuildConfiguration;
