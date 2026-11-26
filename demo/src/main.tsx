// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "@fontsource/young-serif/latin-400.css";
import "./style.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
