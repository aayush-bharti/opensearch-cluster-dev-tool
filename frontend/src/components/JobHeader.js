/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from "react";
import {
  EuiTitle,
  EuiButton,
  EuiText,
  EuiSpacer,
  EuiBadge,
  EuiFlexItem,
  EuiFlexGroup,
} from "@opensearch-project/oui";
import { getStatusIcon, getStatusColor } from "../utils/statusUtils";
import JobConfigurationModal from "./JobConfigurationModal";

// JobHeader component
const JobHeader = ({ job, jobStatus, onDelete }) => {
  const [isConfigModalVisible, setIsConfigModalVisible] = useState(false);
  const taskNames = Object.keys(job.tasks)
    .filter((k) => job.tasks[k])
    .map((k) => k.charAt(0).toUpperCase() + k.slice(1));
  const status = jobStatus?.status || "queued";
  const currentStep = jobStatus?.progress?.current_step || "Initializing...";

  // display the UI
  return (
    <>
      <EuiFlexGroup alignItems="center" justifyContent="spaceBetween">
        <EuiFlexItem>
          <EuiFlexGroup alignItems="center" gutterSize="m">
            <EuiFlexItem grow={false}>{getStatusIcon(status)}</EuiFlexItem>
            <EuiFlexItem>
              <EuiFlexGroup alignItems="center" gutterSize="s">
                <EuiFlexItem grow={false}>
                  {/* job id and task names */}
                  <EuiTitle size="s">
                    <h3>
                      Job #{job.displayId}: {taskNames.join(" & ")}
                    </h3>
                  </EuiTitle>
                </EuiFlexItem>
                <EuiFlexItem grow={false}>
                  {/* job status */}
                  <EuiBadge
                    color={getStatusColor(status)}
                    style={{
                      borderRadius: "999px",
                      fontSize: "0.85rem",
                      letterSpacing: "0.03em",
                      padding: "0.25em 1em",
                    }}
                  >
                    {status.toUpperCase()}
                  </EuiBadge>
                </EuiFlexItem>
              </EuiFlexGroup>
              <EuiSpacer size="xs" />
              {/* task names */}
              <EuiFlexGroup gutterSize="s">
                {taskNames.map((tag) => (
                  <EuiFlexItem grow={false} key={tag}>
                    <EuiBadge color="hollow" style={{ borderRadius: "999px" }}>
                      {tag}
                    </EuiBadge>
                  </EuiFlexItem>
                ))}
              </EuiFlexGroup>
              {/* current step */}
              {jobStatus && (
                <>
                  <EuiSpacer size="xs" />
                  <EuiText
                    size="s"
                    color="subdued"
                    style={{ marginLeft: "100px" }}
                  >
                    {currentStep}
                  </EuiText>
                </>
              )}
            </EuiFlexItem>
          </EuiFlexGroup>
        </EuiFlexItem>
        {/* job timestamp */}
        <EuiFlexItem grow={false}>
          <EuiFlexGroup direction="column" alignItems="flexEnd" gutterSize="s">
            <EuiFlexItem grow={false}>
              <EuiText size="s" color="subdued">
                {job.timestamp}
              </EuiText>
            </EuiFlexItem>
            {/* buttons for delete and viewing configuration */}
            <EuiFlexItem grow={false}>
              <EuiFlexGroup gutterSize="s">
                <EuiFlexItem grow={false}>
                  <EuiButton
                    size="s"
                    iconType="gear"
                    onClick={() => setIsConfigModalVisible(true)}
                  >
                    View Config
                  </EuiButton>
                </EuiFlexItem>
                {onDelete && (
                  <EuiFlexItem grow={false}>
                    <EuiButton
                      size="s"
                      fill
                      color="danger"
                      iconType="trash"
                      onClick={() => onDelete(job.jobId)}
                    >
                      Delete
                    </EuiButton>
                  </EuiFlexItem>
                )}
              </EuiFlexGroup>
            </EuiFlexItem>
          </EuiFlexGroup>
        </EuiFlexItem>
      </EuiFlexGroup>

      {/* Configuration Modal */}
      <JobConfigurationModal
        isVisible={isConfigModalVisible}
        onClose={() => setIsConfigModalVisible(false)}
        job={job}
      />
    </>
  );
};

export default JobHeader;
