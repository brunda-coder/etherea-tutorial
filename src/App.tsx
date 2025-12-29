import React from "react";
import Welcome from "./components/Welcome";

function App() {
  return (
    <div style={{ padding: "24px" }}>
      <h1>Etherea — Desktop Mode</h1>
      <p>Calm workspace. Minimal distractions. You’re in control.</p>
      <Welcome />
    </div>
  );
}

export default App;
