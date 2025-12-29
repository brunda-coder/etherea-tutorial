import React from "react";
import Welcome from "./components/Welcome";
import AudioPlayer from "./components/AudioPlayer";
import Background3D from "./components/Background3D";
import Avatar3D from "./components/Avatar3D";

function App() {
  return (
    <div style={{ padding: "24px" }}>
      <h1>Etherea — Desktop Mode</h1>
      <p>Calm workspace. Minimal distractions. You’re in control.</p>

      {/* Iteration 1 */}
      <Welcome />

      {/* Iteration 3 */}
      <AudioPlayer />

      {/* Iteration 4 */}
      <Background3D />

      {/* Iteration 5 */}
      <Avatar3D />
    </div>
  );
}

export default App;
