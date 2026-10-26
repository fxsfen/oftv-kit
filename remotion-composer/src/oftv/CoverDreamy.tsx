import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

// Punchier thumbnail: the model cut out of her photo (rembg, no generation)
// over a blurred frame of her own "dream" insert, with glow, bokeh, moon,
// fog and the hand-drawn doodle language the model likes. 1920x1080.

const anton = loadAnton("normal", { weights: ["400"], ignoreTooManyRequestsWarning: true });
const caveat = loadCaveat("normal", { weights: ["700"], ignoreTooManyRequestsWarning: true });
const inter = loadInter("normal", { weights: ["800"], ignoreTooManyRequestsWarning: true });

export type CoverDreamyProps = {
  bg: string;
  cutout: string;
  kicker: string;
  line1: string;
  line2: string;
  banner: string;
  accent?: string;
  glow2?: string;
  cutX?: number;
  cutH?: number;
  bgBlur?: number;
};

const ink = "#FFF3E6";
const stroke = { fill: "none", stroke: ink, strokeWidth: 5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

// fixed pseudo-random bokeh so every render is identical
const BOKEH = Array.from({ length: 26 }, (_, i) => {
  const r = (n: number) => ((Math.sin(i * 12.9898 + n * 78.233) * 43758.5453) % 1 + 1) % 1;
  return { x: r(1) * 1920, y: r(2) * 1080, s: 14 + r(3) * 70, o: 0.18 + r(4) * 0.45, c: r(5) > 0.5 ? "255,150,60" : "185,120,255" };
});

const Star: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) => (
  <svg style={{ position: "absolute", left: x, top: y, filter: "drop-shadow(0 0 8px rgba(255,220,150,0.9))" }} width={s} height={s} viewBox="0 0 100 100">
    <path d="M50 6 L58 42 L94 50 L58 58 L50 94 L42 58 L6 50 L42 42 Z" fill={ink} />
  </svg>
);

const Bat: React.FC<{ x: number; y: number; s: number; r: number }> = ({ x, y, s, r }) => (
  <svg style={{ position: "absolute", left: x, top: y, transform: `rotate(${r}deg)` }} width={s} height={s * 0.5} viewBox="0 0 120 60">
    <path d="M60 22 C56 14 50 12 46 18 C38 6 20 6 4 18 C16 20 22 28 24 38 C30 30 38 30 42 36 C46 30 52 30 56 40 L60 46 L64 40 C68 30 74 30 78 36 C82 30 90 30 96 38 C98 28 104 20 116 18 C100 6 82 6 74 18 C70 12 64 14 60 22 Z" fill="#120a18" stroke={ink} strokeWidth={2.5} />
  </svg>
);

export const CoverDreamy: React.FC<CoverDreamyProps> = ({
  bg, cutout, kicker, line1, line2, banner, accent = "#FF8A2B", glow2 = "#A770FF", cutX = 1010, cutH = 1240, bgBlur = 9,
}) => (
  <AbsoluteFill style={{ backgroundColor: "#12081c", overflow: "hidden" }}>
    <Img src={staticFile(bg)} style={{ position: "absolute", inset: -40, width: 2000, height: 1160, objectFit: "cover", filter: `blur(${bgBlur}px) saturate(1.3) brightness(0.78)` }} />
    {/* colour + readability */}
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(20,6,30,0.9) 0%, rgba(26,8,40,0.72) 32%, rgba(26,8,40,0.15) 55%, rgba(26,8,40,0) 70%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(80% 90% at 70% 55%, rgba(0,0,0,0) 45%, rgba(8,2,14,0.7) 100%)" }} />
    {/* bokeh */}
    {BOKEH.map((b, i) => (
      <div key={i} style={{ position: "absolute", left: b.x, top: b.y, width: b.s, height: b.s, borderRadius: "50%",
        background: `radial-gradient(circle, rgba(${b.c},${b.o}) 0%, rgba(${b.c},0) 70%)`, mixBlendMode: "screen" }} />
    ))}
    {/* moon */}
    <div style={{ position: "absolute", left: 1560, top: 40, width: 300, height: 300, borderRadius: "50%",
      background: "radial-gradient(circle, rgba(255,214,140,0.55) 0%, rgba(255,170,80,0.15) 45%, rgba(255,170,80,0) 70%)" }} />
    <svg style={{ position: "absolute", left: 1640, top: 110, filter: "drop-shadow(0 0 30px rgba(255,210,130,0.9))" }} width={150} height={150} viewBox="0 0 100 100">
      <path d="M62 10 C30 14 18 48 32 72 C46 94 78 94 90 76 C66 82 46 66 46 44 C46 28 52 18 62 10 Z" fill="#FFD98A" />
    </svg>
    {/* the model, with a two-tone rim glow */}
    <Img src={staticFile(cutout)} style={{ position: "absolute", left: cutX, bottom: -120, height: cutH,
      filter: `drop-shadow(0 0 18px ${accent}) drop-shadow(0 0 46px ${glow2}) saturate(1.08) contrast(1.05)` }} />
    {/* low fog */}
    <AbsoluteFill style={{ background: "linear-gradient(0deg, rgba(220,190,255,0.28) 0%, rgba(220,190,255,0.08) 14%, rgba(220,190,255,0) 26%)" }} />

    {/* title */}
    <div style={{ position: "absolute", left: 70, top: 110, width: 900 }}>
      <div style={{ fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 92, color: ink, transform: "rotate(-6deg)", transformOrigin: "left", marginLeft: 8,
        textShadow: `0 0 18px ${glow2}` }}>
        {kicker}
      </div>
      <div style={{ fontFamily: anton.fontFamily, fontSize: 214, lineHeight: 0.95, letterSpacing: 2, marginTop: 4, color: accent,
        textShadow: `0 6px 0 #2a0f06, 0 0 30px ${accent}, 0 0 70px rgba(255,120,40,0.6)` }}>
        {line1}
      </div>
      <div style={{ fontFamily: anton.fontFamily, fontSize: 272, lineHeight: 0.9, color: ink,
        textShadow: `0 6px 0 #241232, 0 0 34px ${glow2}, 0 0 80px rgba(160,100,255,0.7)` }}>
        {line2}
      </div>
      <div style={{ position: "relative", marginTop: 34, marginLeft: -10, width: 700, height: 100, transform: "rotate(-3deg)" }}>
        <svg width={700} height={100} viewBox="0 0 700 100" style={{ position: "absolute", left: 0, top: 0, filter: `drop-shadow(0 0 16px ${accent})` }}>
          <path d="M14 30 C120 14 380 10 684 18 C692 42 688 64 680 80 C450 92 210 94 20 86 C6 68 8 48 14 30 Z" fill={accent} />
        </svg>
        <div style={{ position: "absolute", left: 0, right: 0, top: 20, textAlign: "center", fontFamily: inter.fontFamily, fontWeight: 800, fontSize: 42, letterSpacing: 3, color: "#1d0b06" }}>
          {banner}
        </div>
      </div>
    </div>

    {/* doodles */}
    <div style={{ position: "absolute", left: 930, top: 150, fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 104, color: ink, transform: "rotate(-14deg)",
      textShadow: `0 0 16px ${glow2}` }}>zzz</div>
    <Star x={1780} y={330} s={46} />
    <Star x={1500} y={90} s={30} />
    <Star x={960} y={380} s={36} />
    <Star x={1850} y={60} s={26} />
    <Bat x={1660} y={430} s={170} r={-10} />
    <Bat x={1520} y={300} s={100} r={14} />
    <svg style={{ position: "absolute", left: 1000, top: 70 }} width={90} height={90} viewBox="0 0 90 90">
      <path d="M10 30 L28 40 M20 10 L34 28 M44 4 L44 26" {...stroke} />
    </svg>
  </AbsoluteFill>
);

