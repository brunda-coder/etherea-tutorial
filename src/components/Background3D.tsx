import React from "react";

interface Background3DProps {
    scene: string;
}

const Background3D: React.FC<Background3DProps> = ({ scene }) => {
    return (
        <div className={`background3d scene-${scene}`}>
            {/* Placeholder for 3D scene */}
            <p className="scene-label">Scene: {scene}</p>
        </div>
    );
};

export default Background3D;
