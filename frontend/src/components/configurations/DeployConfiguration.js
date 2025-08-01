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
  EuiFlexGroup,
  EuiFlexItem,
  EuiPanel,
  EuiSpacer,
  EuiTitle,
} from "@opensearch-project/oui";
import CustomParameters from "./CustomParameters";

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
        <EuiTitle size="l" style={{ fontSize: "1.75rem", fontWeight: "bold" }}>
          <h3>Deploy Configuration</h3>
        </EuiTitle>
      </EuiFlexGroup>
      <EuiFlexGroup direction="column" gutterSize="xl">
        {!selectedTasks.build && (
          <EuiFlexItem grow={false}>
            <EuiFormRow
              label={<span className="required-field">Distribution URL</span>}
              fullWidth
            >
              <EuiFieldText
                fullWidth
                value={config.distribution_url}
                onChange={onChange("distribution_url")}
                placeholder={"Paste distribution URL here..."}
                isInvalid={
                  selectedTasks.deploy &&
                  !selectedTasks.build &&
                  !config.distribution_url
                }
              />
            </EuiFormRow>
          </EuiFlexItem>
        )}

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
          <EuiFlexItem>
            <EuiFormRow
              label="Data Instance Type"
              style={{ maxWidth: "490px" }}
            >
              <EuiFieldText
                fullWidth
                value={config.data_instance_type}
                onChange={onChange("data_instance_type")}
              />
            </EuiFormRow>
          </EuiFlexItem>
        </EuiFlexGroup>

        <EuiSpacer size="l" />

        <EuiFlexGroup gutterSize="m" style={{ marginLeft: "15px" }}>
          <EuiFlexItem>
            <EuiFormRow
              label="Distribution Version"
              style={{ maxWidth: "490px" }}
            >
              <EuiFieldText
                fullWidth
                value={config.dist_version}
                onChange={onChange("dist_version")}
                placeholder={"Paste distribution version here..."}
              />
            </EuiFormRow>
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiFormRow label="Data Node Count" style={{ maxWidth: "490px" }}>
              <EuiFieldText
                fullWidth
                type="number"
                value={config.data_node_count}
                onChange={onChange("data_node_count")}
                min={1}
                max={20}
              />
            </EuiFormRow>
          </EuiFlexItem>
        </EuiFlexGroup>

        <EuiSpacer size="m" />

        <EuiFlexGroup gutterSize="m" style={{ marginLeft: "15px" }}>
          <EuiFlexItem>
            <EuiFormRow label="CPU Architecture" style={{ maxWidth: "490px" }}>
              <EuiSelect
                fullWidth
                value={config.cpu_arch}
                onChange={onChange("cpu_arch")}
                options={[
                  { value: "arm64", text: "ARM64" },
                  { value: "x64", text: "x64" },
                  { value: "x86_64", text: "x86_64" },
                ]}
              />
            </EuiFormRow>
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiFormRow label="Security Disabled" style={{ maxWidth: "490px" }}>
              <EuiSelect
                fullWidth
                value={config.security_disabled ? "true" : "false"}
                onChange={(e) =>
                  onChange("security_disabled")({
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
        </EuiFlexGroup>

        <EuiSpacer size="m" />
        {/* Show Admin Password when Security is Enabled */}
        {!config.security_disabled && (
          <EuiFlexGroup gutterSize="m" style={{ marginLeft: "15px" }}>
            <EuiFlexItem>
              <EuiFormRow
                label={<span className="required-field">Admin Password</span>}
                helpText="Required when security is enabled and version >= 2.12.0"
                style={{ maxWidth: "490px" }}
              >
                <EuiFieldText
                  fullWidth
                  type="password"
                  value={config.admin_password || ""}
                  onChange={onChange("admin_password")}
                  placeholder="Enter admin password..."
                  isInvalid={!config.admin_password}
                />
              </EuiFormRow>
            </EuiFlexItem>
          </EuiFlexGroup>
        )}

        <EuiSpacer size="m" />

        <EuiFlexGroup gutterSize="m" style={{ marginLeft: "15px" }}>
          <EuiFlexItem>
            <EuiFormRow
              label="Single Node Cluster"
              style={{ maxWidth: "490px" }}
            >
              <EuiSelect
                fullWidth
                value={config.single_node_cluster ? "true" : "false"}
                onChange={(e) =>
                  onChange("single_node_cluster")({
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
          <EuiFlexItem>
            <EuiFormRow label="Use 50% Heap" style={{ maxWidth: "490px" }}>
              <EuiSelect
                fullWidth
                value={config.use_50_percent_heap ? "true" : "false"}
                onChange={(e) =>
                  onChange("use_50_percent_heap")({
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
        </EuiFlexGroup>

        <EuiSpacer size="m" />

        <EuiFlexGroup
          gutterSize="m"
          style={{ marginLeft: "15px", marginBottom: "10px" }}
        >
          <EuiFlexItem>
            <EuiFormRow
              label="Minimum Distribution"
              style={{ maxWidth: "490px" }}
            >
              <EuiSelect
                fullWidth
                value={config.min_distribution}
                onChange={onChange("min_distribution")}
                options={[
                  { value: "false", text: "False" },
                  { value: "true", text: "True" },
                ]}
              />
            </EuiFormRow>
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiFormRow label="Is Internal" style={{ maxWidth: "490px" }}>
              <EuiSelect
                fullWidth
                value={config.is_internal ? "true" : "false"}
                onChange={(e) =>
                  onChange("is_internal")({
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

        <EuiFlexGroup gutterSize="m" style={{ marginLeft: "15px" }}>
          <EuiFlexItem>
            <EuiFormRow
              label="Server Access Type"
              helpText="Choose how to restrict server access"
              style={{ maxWidth: "490px" }}
            >
              <EuiSelect
                fullWidth
                value={config.server_access_type || ""}
                onChange={onChange("server_access_type")}
                options={[
                  { value: "", text: "Use Default" },
                  { value: "prefixList", text: "Prefix List" },
                  { value: "ipv4", text: "IPv4 CIDR" },
                  { value: "ipv6", text: "IPv6 CIDR" },
                  { value: "securityGroupId", text: "Security Group ID" },
                ]}
              />
            </EuiFormRow>
          </EuiFlexItem>
          <EuiFlexItem>
            <EuiFormRow
              label="Restrict Server Access To"
              helpText="Value for server access type (e.g., pl-12345, 10.0.0.0/16)"
              style={{ maxWidth: "490px" }}
            >
              <EuiFieldText
                fullWidth
                value={config.restrict_server_access_to || ""}
                onChange={onChange("restrict_server_access_to")}
                placeholder="Leave blank for default"
              />
            </EuiFormRow>
          </EuiFlexItem>
        </EuiFlexGroup>

        <EuiSpacer size="m" />
      </EuiFlexGroup>

      <CustomParameters
        taskType="Deploy"
        customParams={config.custom_deploy_params || []}
        onChange={(params) =>
          onChange("custom_deploy_params")({ target: { value: params } })
        }
        placeholder="Enter deploy parameter (e.g., --profile production, --region us-west-2)"
      />
    </EuiPanel>
  );
};

export default DeployConfiguration;
