import { Player } from "@remotion/player";
import { HarjamuktiDemo } from "./Composition";

const FPS = 30;
const DURATION_FRAMES = 18 * FPS; // 18 seconds

export const App: React.FC = () => {
  return (
    <div className="stage">
      <a href="../../index.html" className="back">
        ← HargaRumah
      </a>
      <div className="brand">
        <strong>Rumah123</strong> · strict filter · main keyword
      </div>
      <div className="player-wrap">
        <Player
          component={HarjamuktiDemo}
          durationInFrames={DURATION_FRAMES}
          compositionWidth={1920}
          compositionHeight={1080}
          fps={FPS}
          autoPlay
          loop
          controls={false}
          clickToPlay={false}
          showPlaybackRateControl={false}
          allowFullscreen={false}
          style={{ width: "100%", height: "100%" }}
        />
      </div>
    </div>
  );
};
