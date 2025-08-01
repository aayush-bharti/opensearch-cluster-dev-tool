/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import {
  EuiFieldText,
  EuiFormRow,
  EuiSelect,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPanel,
  EuiSpacer,
} from "@opensearch-project/oui";

const AdvancedDeployConfiguration = ({ config, onChange }) => {
  return (
    <EuiPanel>
      {/* Additional Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Additional Config"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.additional_config || ""}
              onChange={onChange("additional_config")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="Additional OSD Config"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.additional_osd_config || ""}
              onChange={onChange("additional_osd_config")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Certificate and CIDR */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Certificate ARN"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.certificate_arn || ""}
              onChange={onChange("certificate_arn")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow label="CIDR Block" style={{ maxWidth: "490px" }}>
            <EuiFieldText
              fullWidth
              value={config.cidr || ""}
              onChange={onChange("cidr")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Node Counts Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Client Node Count"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              type="number"
              value={config.client_node_count || ""}
              onChange={onChange("client_node_count")}
              placeholder="Leave blank for default"
              min={0}
              max={10}
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow label="Context Key" style={{ maxWidth: "490px" }}>
            <EuiFieldText
              fullWidth
              value={config.context_key || ""}
              onChange={onChange("context_key")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Custom Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Custom Config Files"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.custom_config_files || ""}
              onChange={onChange("custom_config_files")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="Custom Role ARN"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.custom_role_arn || ""}
              onChange={onChange("custom_role_arn")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Storage Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Data Node Storage (GB)"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              type="number"
              value={config.data_node_storage || ""}
              onChange={onChange("data_node_storage")}
              placeholder="Leave blank for default"
              min={20}
              max={1000}
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="Enable Monitoring"
            style={{ maxWidth: "490px" }}
          >
            <EuiSelect
              fullWidth
              value={
                config.enable_monitoring === undefined
                  ? ""
                  : config.enable_monitoring
                  ? "true"
                  : "false"
              }
              onChange={(e) =>
                onChange("enable_monitoring")({
                  target: {
                    value:
                      e.target.value === ""
                        ? undefined
                        : e.target.value === "true",
                  },
                })
              }
              options={[
                { value: "", text: "Use Default" },
                { value: "false", text: "False" },
                { value: "true", text: "True" },
              ]}
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Additional Feature Flags */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Enable Remote Store"
            style={{ maxWidth: "490px" }}
          >
            <EuiSelect
              fullWidth
              value={
                config.enable_remote_store === undefined
                  ? ""
                  : config.enable_remote_store
                  ? "true"
                  : "false"
              }
              onChange={(e) =>
                onChange("enable_remote_store")({
                  target: {
                    value:
                      e.target.value === ""
                        ? undefined
                        : e.target.value === "true",
                  },
                })
              }
              options={[
                { value: "", text: "Use Default" },
                { value: "false", text: "False" },
                { value: "true", text: "True" },
              ]}
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="Ingest Node Count"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              type="number"
              value={config.ingest_node_count || ""}
              onChange={onChange("ingest_node_count")}
              placeholder="Leave blank for default"
              min={0}
              max={10}
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* JVM and Load Balancer */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="JVM System Properties"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.jvm_sys_props || ""}
              onChange={onChange("jvm_sys_props")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="Load Balancer Type"
            style={{ maxWidth: "490px" }}
          >
            <EuiSelect
              fullWidth
              value={config.load_balancer_type || ""}
              onChange={onChange("load_balancer_type")}
              options={[
                { value: "", text: "Use Default" },
                { value: "nlb", text: "Network Load Balancer (NLB)" },
                { value: "alb", text: "Application Load Balancer (ALB)" },
              ]}
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Manager and ML Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Manager Node Count"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              type="number"
              value={config.manager_node_count || ""}
              onChange={onChange("manager_node_count")}
              placeholder="Leave blank for default"
              min={1}
              max={10}
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="ML Instance Type"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.ml_instance_type || ""}
              onChange={onChange("ml_instance_type")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* ML Node Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow label="ML Node Count" style={{ maxWidth: "490px" }}>
            <EuiFieldText
              fullWidth
              type="number"
              value={config.ml_node_count || ""}
              onChange={onChange("ml_node_count")}
              placeholder="Leave blank for default"
              min={0}
              max={10}
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="ML Node Storage (GB)"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              type="number"
              value={config.ml_node_storage || ""}
              onChange={onChange("ml_node_storage")}
              placeholder="Leave blank for default"
              min={20}
              max={1000}
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Network Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Network Stack Suffix"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.network_stack_suffix || ""}
              onChange={onChange("network_stack_suffix")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="OpenSearch Port"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              type="number"
              value={config.map_opensearch_port_to || ""}
              onChange={onChange("map_opensearch_port_to")}
              placeholder="Leave blank for default"
              min={1}
              max={65535}
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Additional Load Balancer Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Dashboards Port"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              type="number"
              value={config.map_opensearch_dashboards_port_to || ""}
              onChange={onChange("map_opensearch_dashboards_port_to")}
              placeholder="Leave blank for default"
              min={1}
              max={65535}
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="Security Group ID"
            style={{ maxWidth: "490px" }}
          >
            <EuiFieldText
              fullWidth
              value={config.security_group_id || ""}
              onChange={onChange("security_group_id")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* Storage and Instance Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow
            label="Storage Volume Type"
            style={{ maxWidth: "490px" }}
          >
            <EuiSelect
              fullWidth
              value={config.storage_volume_type || ""}
              onChange={onChange("storage_volume_type")}
              options={[
                { value: "", text: "Use Default" },
                { value: "gp2", text: "General Purpose SSD (gp2)" },
                { value: "gp3", text: "General Purpose SSD (gp3)" },
                { value: "io1", text: "Provisioned IOPS SSD (io1)" },
                { value: "io2", text: "Provisioned IOPS SSD (io2)" },
                { value: "st1", text: "Throughput Optimized HDD (st1)" },
                { value: "sc1", text: "Cold HDD (sc1)" },
              ]}
            />
          </EuiFormRow>
        </EuiFlexItem>
        <EuiFlexItem>
          <EuiFormRow
            label="Use Instance Storage"
            style={{ maxWidth: "490px" }}
          >
            <EuiSelect
              fullWidth
              value={
                config.use_instance_based_storage === undefined
                  ? ""
                  : config.use_instance_based_storage
                  ? "true"
                  : "false"
              }
              onChange={(e) =>
                onChange("use_instance_based_storage")({
                  target: {
                    value:
                      e.target.value === ""
                        ? undefined
                        : e.target.value === "true",
                  },
                })
              }
              options={[
                { value: "", text: "Use Default" },
                { value: "false", text: "False" },
                { value: "true", text: "True" },
              ]}
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="m" />

      {/* VPC Configuration */}
      <EuiFlexGroup gutterSize="m">
        <EuiFlexItem>
          <EuiFormRow label="VPC ID" style={{ maxWidth: "490px" }}>
            <EuiFieldText
              fullWidth
              value={config.vpc_id || ""}
              onChange={onChange("vpc_id")}
              placeholder="Leave blank for default"
            />
          </EuiFormRow>
        </EuiFlexItem>
      </EuiFlexGroup>
    </EuiPanel>
  );
};

export default AdvancedDeployConfiguration; 