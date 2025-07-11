import React from "react";
import ReactDOM from "react-dom/client";
import "@opensearch-project/oui/dist/eui_theme_light.css";
import "./index.css";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
