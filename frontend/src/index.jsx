import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

// Step 1: Get the root DOM element from index.html
// - This is the <div id="root"></div> in index.html where React mounts
const rootElement = document.getElementById("root");

// Step 2: Create a React root and render the App component
// - StrictMode enables extra development warnings for best practices
const root = createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
