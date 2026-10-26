import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

// Thumbnail in the style the model likes (bold display title, one hand-written
// line, brush-stroke banner, hand-drawn doodles). 1920x1080 composition.

const anton = loadAnton("normal", { weights: ["400"], ignoreTooManyRequestsWarning: true });
const caveat = loadCaveat("normal", { weights: ["700"], ignoreTooManyRequestsWarning: true });
const inter = loadInter("normal", { weights: ["800"], ignoreTooManyRequestsWarning: true });

export type CoverDoodleProps = {
  src: string;
  kicker: string;
  line1: string;
  line2: string;
  banner: string;
  accent?: string;
  objectPosition?: string;
};

const ink = "#FFF3E6";
const stroke = { fill: "none", stroke: ink, strokeWidth: 5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

const Moon: React.FC<{ x: number; y: number; s: number; c: string }> = ({ x, y, s, c }) => (
  <svg style={{ position: "absolute", left: x, top: y }} width={s} height={s} viewBox="0 0 100 100">
    <path d="M62 10 C30 14 18 48 32 72 C46 94 78 94 90 76 C66 82 46 66 46 44 C46 28 52 18 62 10 Z" fill={c} opacity={0.95} />
  </svg>
);

const Star: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) => (
  <svg style={{ position: "absolute", left: x, top: y }} width={s} height={s} viewBox="0 0 100 100">
    <path d="M50 6 L58 42 L94 50 L58 58 L50 94 L42 58 L6 50 L42 42 Z" fill={ink} />
  </svg>
);

const Bat: React.FC<{ x: number; y: number; s: number; r: number }> = ({ x, y, s, r }) => (
  <svg style={{ position: "absolute", left: x, top: y, transform: `rotate(${r}deg)` }} width={s} height={s * 0.5} viewBox="0 0 120 60">
    <path d="M60 22 C56 14 50 12 46 18 C38 6 20 6 4 18 C16 20 22 28 24 38 C30 30 38 30 42 36 C46 30 52 30 56 40 L60 46 L64 40 C68 30 74 30 78 36 C82 30 90 30 96 38 C98 28 104 20 116 18 C100 6 82 6 74 18 C70 12 64 14 60 22 Z" fill="#141018" stroke={ink} strokeWidth={2.5} />
  </svg>
);

export const CoverDoodle: React.FC<CoverDoodleProps> = ({
  src, kicker, line1, line2, banner, accent = "#FF8A2B", objectPosition = "50% 40%",
}) => (
  <AbsoluteFill style={{ backgroundColor: "#160d10" }}>
    <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition, filter: "saturate(1.12) contrast(1.06) brightness(0.97)" }} />
    {/* moody night grade + left shade for the title */}
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(18,8,14,0.86) 0%, rgba(18,8,14,0.62) 30%, rgba(18,8,14,0.08) 48%, rgba(18,8,14,0) 56%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(90% 80% at 62% 45%, rgba(0,0,0,0) 50%, rgba(10,4,20,0.45) 100%)" }} />

    {/* title block */}
    <div style={{ position: "absolute", left: 70, top: 120, width: 820 }}>
      <div style={{ fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 88, color: ink, transform: "rotate(-6deg)", transformOrigin: "left", marginLeft: 8 }}>
        {kicker}
      </div>
      <div
        style={{
          fontFamily: anton.fontFamily, fontSize: 196, lineHeight: 0.95, letterSpacing: 2, marginTop: 6,
          color: accent, textShadow: "0 6px 0 #2a0f06, 0 14px 40px rgba(0,0,0,0.55)",
        }}
      >
        {line1}
      </div>
      <div style={{ fontFamily: anton.fontFamily, fontSize: 250, lineHeight: 0.9, color: ink, textShadow: "0 6px 0 #2a1a1a, 0 14px 40px rgba(0,0,0,0.55)" }}>
        {line2}
      </div>
      {/* brush-stroke banner */}
      <div style={{ position: "relative", marginTop: 34, marginLeft: -10, width: 680, height: 96, transform: "rotate(-3deg)" }}>
        <svg width={680} height={96} viewBox="0 0 680 96" style={{ position: "absolute", left: 0, top: 0 }}>
          <path d="M14 30 C120 14 360 10 664 18 C672 40 668 62 660 78 C440 90 200 92 20 84 C6 66 8 46 14 30 Z" fill={ink} opacity={0.94} />
        </svg>
        <div style={{ position: "absolute", left: 0, right: 0, top: 18, textAlign: "center", fontFamily: inter.fontFamily, fontWeight: 800, fontSize: 40, letterSpacing: 3, color: "#2a1418" }}>
          {banner}
        </div>
      </div>
    </div>

    {/* doodles around her */}
    <Moon x={1500} y={70} s={150} c="#FFD27A" />
    <Star x={1690} y={210} s={46} />
    <Star x={1420} y={260} s={30} />
    <Star x={1760} y={90} s={34} />
    <div style={{ position: "absolute", left: 1270, top: 120, fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 96, color: ink, transform: "rotate(-12deg)" }}>
      zzz
    </div>
    <Bat x={1600} y={420} s={150} r={-10} />
    <Bat x={1740} y={540} s={100} r={12} />
    {/* little sparkle marks like the reference thumbnails */}
    <svg style={{ position: "absolute", left: 1180, top: 330 }} width={90} height={90} viewBox="0 0 90 90">
      <path d="M10 30 L28 40 M20 10 L34 28 M44 4 L44 26" {...stroke} />
    </svg>
  </AbsoluteFill>
);
