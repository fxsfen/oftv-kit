import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

// Cutout cover with the model on the LEFT (for photos where her arm leaves the
// frame on the left) and the title block on the right. Dark villain palette,
// moon + bats + sparkles. 1920x1080.

const anton = loadAnton("normal", { weights: ["400"], ignoreTooManyRequestsWarning: true });
const caveat = loadCaveat("normal", { weights: ["700"], ignoreTooManyRequestsWarning: true });
const inter = loadInter("normal", { weights: ["800"], ignoreTooManyRequestsWarning: true });

export type CoverVillainProps = {
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
};

const ink = "#FFF1F0";

const BOKEH = Array.from({ length: 22 }, (_, i) => {
  const r = (n: number) => ((Math.sin(i * 12.9898 + n * 78.233) * 43758.5453) % 1 + 1) % 1;
  return { x: 900 + r(1) * 1020, y: r(2) * 1080, s: 14 + r(3) * 60, o: 0.15 + r(4) * 0.4, c: r(5) > 0.5 ? "230,40,70" : "150,80,255" };
});

const Bat: React.FC<{ x: number; y: number; s: number; r: number }> = ({ x, y, s, r }) => (
  <svg style={{ position: "absolute", left: x, top: y, transform: `rotate(${r}deg)` }} width={s} height={s * 0.5} viewBox="0 0 120 60">
    <path d="M60 22 C56 14 50 12 46 18 C38 6 20 6 4 18 C16 20 22 28 24 38 C30 30 38 30 42 36 C46 30 52 30 56 40 L60 46 L64 40 C68 30 74 30 78 36 C82 30 90 30 96 38 C98 28 104 20 116 18 C100 6 82 6 74 18 C70 12 64 14 60 22 Z" fill="#0d060c" stroke={ink} strokeWidth={2.5} />
  </svg>
);

const Spark: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) => (
  <svg style={{ position: "absolute", left: x, top: y, filter: "drop-shadow(0 0 8px rgba(255,200,200,0.9))" }} width={s} height={s} viewBox="0 0 100 100">
    <path d="M50 6 L58 42 L94 50 L58 58 L50 94 L42 58 L6 50 L42 42 Z" fill={ink} />
  </svg>
);

export const CoverVillain: React.FC<CoverVillainProps> = ({
  bg, cutout, kicker, line1, line2, banner, accent = "#E8203F", glow2 = "#9A5CFF", cutX = 0, cutH = 1080,
}) => (
  <AbsoluteFill style={{ backgroundColor: "#0e0509", overflow: "hidden" }}>
    <Img src={staticFile(bg)} style={{ position: "absolute", inset: -40, width: 2000, height: 1160, objectFit: "cover",
      filter: "blur(18px) saturate(0.6) brightness(0.28) hue-rotate(-20deg)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(270deg, rgba(14,4,10,0.92) 0%, rgba(20,6,14,0.75) 34%, rgba(40,6,20,0.25) 60%, rgba(0,0,0,0.1) 100%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(60% 70% at 30% 45%, rgba(200,20,60,0.35) 0%, rgba(0,0,0,0) 60%)" }} />
    {BOKEH.map((b, i) => (
      <div key={i} style={{ position: "absolute", left: b.x, top: b.y, width: b.s, height: b.s, borderRadius: "50%",
        background: `radial-gradient(circle, rgba(${b.c},${b.o}) 0%, rgba(${b.c},0) 70%)`, mixBlendMode: "screen" }} />
    ))}
    {/* moon behind her head */}
    <div style={{ position: "absolute", left: 470, top: 20, width: 420, height: 420, borderRadius: "50%",
      background: "radial-gradient(circle, rgba(255,90,110,0.55) 0%, rgba(200,30,70,0.18) 45%, rgba(0,0,0,0) 70%)" }} />
    <Img src={staticFile(cutout)} style={{ position: "absolute", left: cutX, bottom: 0, height: cutH,
      filter: `drop-shadow(0 0 16px ${accent}) drop-shadow(0 0 48px ${glow2}) contrast(1.05)` }} />

    {/* title, right side */}
    <div style={{ position: "absolute", right: 70, top: 130, width: 820, textAlign: "right" }}>
      <div style={{ fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 92, color: ink, transform: "rotate(-5deg)", transformOrigin: "right",
        textShadow: `0 0 18px ${accent}` }}>{kicker}</div>
      <div style={{ fontFamily: anton.fontFamily, fontSize: 236, lineHeight: 0.95, letterSpacing: 2, color: accent,
        textShadow: `0 6px 0 #2a0610, 0 0 30px ${accent}, 0 0 80px rgba(230,30,70,0.6)` }}>{line1}</div>
      <div style={{ fontFamily: anton.fontFamily, fontSize: 236, lineHeight: 0.9, color: ink,
        textShadow: `0 6px 0 #22101e, 0 0 30px ${glow2}, 0 0 80px rgba(150,90,255,0.6)` }}>{line2}</div>
      <div style={{ position: "relative", marginTop: 34, marginLeft: "auto", width: 700, height: 100, transform: "rotate(-3deg)" }}>
        <svg width={700} height={100} viewBox="0 0 700 100" style={{ position: "absolute", left: 0, top: 0, filter: `drop-shadow(0 0 16px ${accent})` }}>
          <path d="M14 30 C120 14 380 10 684 18 C692 42 688 64 680 80 C450 92 210 94 20 86 C6 68 8 48 14 30 Z" fill={accent} />
        </svg>
        <div style={{ position: "absolute", left: 0, right: 0, top: 20, textAlign: "center", fontFamily: inter.fontFamily, fontWeight: 800,
          fontSize: 42, letterSpacing: 3, color: ink }}>{banner}</div>
      </div>
    </div>

    <Bat x={1150} y={70} s={150} r={-8} />
    <Bat x={1330} y={160} s={90} r={12} />
    <Bat x={1020} y={560} s={100} r={-14} />
    <Spark x={1110} y={260} s={34} />
    <Spark x={1840} y={760} s={40} />
    <Spark x={1220} y={880} s={28} />
  </AbsoluteFill>
);

