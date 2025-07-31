import React from "react";
import { EuiProgress, EuiSpacer, EuiText } from "@opensearch-project/oui";

// JobProgress component
const JobProgress = ({ jobStatus }) => {
  if (!jobStatus || jobStatus.status !== "running") {
    return null;
  }

  // display the UI
  return (
    <>
      <EuiSpacer size="m" />
      <EuiProgress color="primary" size="m" />
      <EuiSpacer size="s" />
      <EuiText size="s" color="subdued" textAlign="center">
        {jobStatus?.progress &&
          `${jobStatus.progress.completed_tasks}/${jobStatus.progress.total_tasks} tasks completed`}
      </EuiText>
    </>
  );
};

export default JobProgress;
