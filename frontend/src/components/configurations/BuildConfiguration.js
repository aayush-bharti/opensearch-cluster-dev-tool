/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import {
  EuiIcon,
  EuiFormRow,
  EuiTextArea,
  EuiTitle,
  EuiFlexGroup,
  EuiPanel,
} from "@opensearch-project/oui";
import CustomParameters from "./CustomParameters";

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
        <EuiTitle size="l" style={{ fontSize: "1.75rem", fontWeight: "bold" }}>
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
          value={config.manifest_yml}
          onChange={onChange("manifest_yml")}
          placeholder="Enter manifest YAML content..."
          isInvalid={selectedTasks.build && !config.manifest_yml.trim()}
          className="manifest-textarea"
        />
      </EuiFormRow>

      <CustomParameters
        taskType="Build"
        customParams={config.custom_build_params || []}
        onChange={(params) =>
          onChange("custom_build_params")({ target: { value: params } })
        }
        placeholder="Enter build parameter (e.g., --verbose, --parallel 4)"
      />
    </EuiPanel>
  );
};

export default BuildConfiguration;
