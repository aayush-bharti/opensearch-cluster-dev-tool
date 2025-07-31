import React, { useState } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import {
  EuiPage,
  EuiPageBody,
  EuiPageContent,
  EuiPageContentBody,
  EuiSpacer,
} from "@opensearch-project/oui";
import ClusterDevUI from "./pages/clusterDevUI";
import "./App.css";

// main app component
function App() {
  const [selectedPageId] = useState("clusterDevUI");

  const pages = [
    {
      id: "clusterDevUI",
      name: "Cluster Dev UI",
      component: ClusterDevUI,
    },
  ];

  // render the content
  const renderContent = () => {
    const selectedPage = pages.find((page) => page.id === selectedPageId);
    const Component = selectedPage.component;
    return <Component />;
  };

  // display the UI
  return (
    <Router>
      <div className="App">
        <EuiPage paddingSize="l">
          <EuiPageBody>
            <EuiPageContent
              hasBorder={false}
              hasShadow={false}
              paddingSize="none"
              color="transparent"
              borderRadius="none"
            >
              <EuiPageContentBody>
                <EuiSpacer size="l" />
                {renderContent()}
              </EuiPageContentBody>
            </EuiPageContent>
          </EuiPageBody>
        </EuiPage>
      </div>
    </Router>
  );
}

export default App;
