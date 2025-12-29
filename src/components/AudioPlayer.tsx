import React, { useRef } from "react";

interface AudioPlayerProps {
    src: string;
    autoplay?: boolean;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ src, autoplay = false }) => {
    const audioRef = useRef<HTMLAudioElement>(null);

    const play = () => audioRef.current?.play();
    const pause = () => audioRef.current?.pause();

    return (
        <div className="audio-player">
            <audio ref={audioRef} src={src} autoPlay={autoplay} />
            <button onClick={play}>Play</button>
            <button onClick={pause}>Pause</button>
        </div>
    );
};

export default AudioPlayer;
