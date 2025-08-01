/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import {
  EuiPanel,
  EuiFlexGroup,
  EuiIcon,
  EuiTitle,
  EuiText,
  EuiFormRow,
  EuiFieldText,
  EuiFlexItem,
} from "@opensearch-project/oui";

// handles the S3 bucket configuration
const S3Configuration = ({ config, onChange }) => {
  return (
    <EuiPanel paddingSize="l">
      <EuiFlexGroup direction="column" alignItems="center" gutterSize="m">
        <EuiIcon type="storage" color="primary" size="l" />
        <EuiTitle
          size="m"
          style={{
            fontSize: "1.5rem",
            fontWeight: "bold",
            marginTop: "0.25rem",
          }}
        >
          <h3>S3 Configuration</h3>
        </EuiTitle>
        <EuiText color="subdued" style={{ fontSize: "0.9rem" }}>
          Configure S3 bucket for storing results
        </EuiText>
      </EuiFlexGroup>

      {/* S3 Information */}
      <div className="info-callout">
        <EuiFlexGroup alignItems="center" gutterSize="m">
          <EuiFlexItem grow={false}></EuiFlexItem>
          <EuiFlexItem>
            <EuiText>
              <strong>
                Please ensure your AWS account has the necessary permissions to
                create and manage S3 buckets.
              </strong>
            </EuiText>
          </EuiFlexItem>
        </EuiFlexGroup>
      </div>

      <div style={{ marginTop: "1.5rem" }}>
        <EuiFormRow
          label="S3 Bucket Name"
          isRequired
          helpText="Bucket will be created automatically if it doesn't exist. Used for storing build artifacts, deployment results, and benchmark data."
        >
          <EuiFieldText
            value={config.s3_bucket || ""}
            onChange={onChange("s3_bucket")}
            placeholder="Enter S3 bucket name (e.g., my-opensearch-bucket)"
            fullWidth
          />
        </EuiFormRow>
      </div>
    </EuiPanel>
  );
};

export default S3Configuration;
