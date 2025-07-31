import { EuiIcon } from "@opensearch-project/oui";

export const getStatusIcon = (status) => {
  switch (status) {
    case "pending":
      return <EuiIcon size="xl" type="clock" color="subdued" />;
    case "running":
      return <EuiIcon size="xl" type="playFilled" color="primary" />;
    case "completed":
      return <EuiIcon size="xl" type="checkInCircleFilled" color="success" />;
    case "failed":
      return <EuiIcon size="xl" type="crossInACircleFilled" color="danger" />;
    case "cancelled":
      return <EuiIcon size="xl" type="minusInCircleFilled" color="warning" />;
    default:
      return <EuiIcon size="xl" type="questionInCircle" color="subdued" />;
  }
};

export const getStatusColor = (status) => {
  switch (status) {
    case "pending":
      return "default";
    case "running":
      return "primary";
    case "completed":
      return "success";
    case "failed":
      return "danger";
    case "cancelled":
      return "warning";
    default:
      return "default";
  }
};
