import React from "react";

// Shared Avatar types
export type AvatarType = "Professional" | "Neutral" | "Creative" | "Calm" | "Playful";

interface Avatar3DProps {
    name: string;
    type: AvatarType;
    onGreet?: () => void; // optional callback
}

const Avatar3D: React.FC<Avatar3DProps> = ({ name, type, onGreet }) => {
    return (
        <div className="avatar3d-container">
            <p className="avatar-name">{name} ({type})</p>
            {onGreet && (
                <button onClick={onGreet} className="greet-btn">
                    Say Hi
                </button>
            )}
        </div>
    );
};

export default Avatar3D;
