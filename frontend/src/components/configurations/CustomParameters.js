/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from "react";
import {
  EuiButton,
  EuiButtonEmpty,
  EuiFieldText,
  EuiFormRow,
  EuiFlexGroup,
  EuiFlexItem,
  EuiIcon,
  EuiText,
  EuiSpacer,
  EuiPanel,
  EuiHorizontalRule,
} from "@opensearch-project/oui";

// custom parameters component
const CustomParameters = ({
  taskType,
  customParams = [],
  onChange,
  placeholder = "Enter custom parameter (e.g., --verbose, --parallel 4)",
}) => {
  const [showCustomParams, setShowCustomParams] = useState(false);

  const addParameter = () => {
    const newParams = [...customParams, { key: Date.now(), value: "" }];
    onChange(newParams);
  };

  const removeParameter = (keyToRemove) => {
    const newParams = customParams.filter((param) => param.key !== keyToRemove);
    onChange(newParams);
  };

  const updateParameter = (key, newValue) => {
    const newParams = customParams.map((param) =>
      param.key === key ? { ...param, value: newValue } : param
    );
    onChange(newParams);
  };

  return (
    <>
      <EuiHorizontalRule margin="m" />

      <EuiFlexGroup alignItems="center" gutterSize="s">
        <EuiFlexItem grow={false}>
          <EuiButtonEmpty
            iconType={showCustomParams ? "arrowDown" : "arrowRight"}
            onClick={() => setShowCustomParams(!showCustomParams)}
            size="s"
          >
            <EuiText size="s" style={{ fontWeight: "bold" }}>
              Custom {taskType} Parameters
            </EuiText>
          </EuiButtonEmpty>
        </EuiFlexItem>
        <EuiFlexItem grow={false}>
          <EuiIcon type="help" color="subdued" />
        </EuiFlexItem>
      </EuiFlexGroup>

      {showCustomParams && (
        <EuiPanel color="subdued" paddingSize="m">
          <EuiText size="s" color="subdued" style={{ marginBottom: "1rem" }}>
            Add custom command-line parameters that will be appended to the{" "}
            {taskType.toLowerCase()} command.
          </EuiText>

          {customParams.map((param) => (
            <EuiFlexGroup key={param.key} gutterSize="s" alignItems="center">
              <EuiFlexItem>
                <EuiFormRow>
                  <EuiFieldText
                    fullWidth
                    value={param.value}
                    onChange={(e) => updateParameter(param.key, e.target.value)}
                    placeholder={placeholder}
                  />
                </EuiFormRow>
              </EuiFlexItem>
              <EuiFlexItem grow={false}>
                <EuiButtonEmpty
                  iconType="trash"
                  color="danger"
                  size="s"
                  onClick={() => removeParameter(param.key)}
                  aria-label="Remove parameter"
                />
              </EuiFlexItem>
            </EuiFlexGroup>
          ))}

          <EuiSpacer size="s" />

          <EuiButton iconType="plus" size="s" onClick={addParameter}>
            Add Parameter
          </EuiButton>
        </EuiPanel>
      )}
    </>
  );
};

export default CustomParameters;
