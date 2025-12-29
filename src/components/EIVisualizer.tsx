import React from "react";

interface EIVisualizerProps {
    focus: number; // 0-100
    stress: number; // 0-100
}

const EIVisualizer: React.FC<EIVisualizerProps> = ({ focus, stress }) => {
    return (
        <div className="ei-visualizer">
            <p>Focus: {focus}%</p>
            <p>Stress: {stress}%</p>
            <div className="bars">
                <div className="focus-bar" style={{ width: `${focus}%` }} />
                <div className="stress-bar" style={{ width: `${stress}%` }} />
            </div>
        </div>
    );
};

export default EIVisualizer;
