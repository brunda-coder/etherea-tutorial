import React, { useState } from "react";
import Avatar3D, { AvatarType } from "./Avatar3D";
import Background3D from "./Background3D";
import EIVisualizer from "./EIVisualizer";
import AudioPlayer from "./AudioPlayer";

interface AvatarItem {
    name: string;
    type: AvatarType;
}

interface ScenePlayerProps {
    sceneName: string;
    avatars?: AvatarItem[];
    focus?: number;
    stress?: number;
    narrationSrc?: string;
}

const ScenePlayer: React.FC<ScenePlayerProps> = ({
    sceneName,
    avatars = [],
    focus = 50,
    stress = 50,
    narrationSrc,
}) => {
    const [currentAvatar, setCurrentAvatar] = useState<number>(0);

    const nextAvatar = (): void => {
        if (!avatars.length) return;
        setCurrentAvatar((prev) => (prev + 1) % avatars.length);
    };

    const current: AvatarItem | null =
        avatars.length > 0 ? avatars[currentAvatar] : null;

    return (
        <div className="scene-player w-full h-full relative">
            <Background3D scene={sceneName} />

            {current && (
                <div className="absolute inset-0 pointer-events-none">
                    <Avatar3D
                        name={current.name}
                        type={current.type}
                        onGreet={nextAvatar}
                    />
                </div>
            )}

            <div className="absolute bottom-8 left-8 right-8 pointer-events-auto">
                <EIVisualizer
                    focus={Math.max(0, Math.min(100, focus))}
                    stress={Math.max(0, Math.min(100, stress))}
                />
            </div>

            {narrationSrc && (
                <AudioPlayer
                    src={narrationSrc}
                    autoplay
                    onEnded={() =>
                        console.log(`Finished playing narration: ${narrationSrc}`)
                    }
                />
            )}
        </div>
    );
};

export default ScenePlayer;
