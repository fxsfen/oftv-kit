import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

// Shopping-themed cutout thumbnail (same build as CoverDreamy): model cut out of
// her photo (rembg) over a blurred frame of her own mall footage, neon title,
// hand-drawn bags / hearts / sparkles and a handwritten note. 1920x1080.

const anton = loadAnton("normal", { weights: ["400"], ignoreTooManyRequestsWarning: true });
const caveat = loadCaveat("normal", { weights: ["700"], ignoreTooManyRequestsWarning: true });
const inter = loadInter("normal", { weights: ["800"], ignoreTooManyRequestsWarning: true });

export type CoverShopProps = {
  bg: string;
  cutout: string;
  kicker: string;
  line1: string;
  line2: string;
  banner: string;
  note?: string;
  accent?: string;
  glow2?: string;
  cutX?: number;
  cutH?: number;
};

const ink = "#FFF6F0";
const stroke = { fill: "none", stroke: ink, strokeWidth: 5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

const Bag: React.FC<{ x: number; y: number; s: number; r: number; c: string }> = ({ x, y, s, r, c }) => (
  <svg style={{ position: "absolute", left: x, top: y, transform: `rotate(${r}deg)`, filter: `drop-shadow(0 0 14px ${c})` }}
    width={s} height={s * 1.1} viewBox="0 0 100 110">
    <path d="M14 34 L86 34 L92 104 L8 104 Z" fill={c} stroke={ink} strokeWidth={4} strokeLinejoin="round" />
    <path d="M34 34 C34 10 66 10 66 34" fill="none" stroke={ink} strokeWidth={5} strokeLinecap="round" />
  </svg>
);

const Heart: React.FC<{ x: number; y: number; s: number; r: number; fill?: string }> = ({ x, y, s, r, fill }) => (
  <svg style={{ position: "absolute", left: x, top: y, transform: `rotate(${r}deg)` }} width={s} height={s} viewBox="0 0 100 100">
    <path d="M50 86 C20 64 8 48 8 32 C8 18 20 8 32 8 C40 8 46 12 50 20 C54 12 60 8 68 8 C80 8 92 18 92 32 C92 48 80 64 50 86 Z"
      fill={fill || "none"} stroke={ink} strokeWidth={6} strokeLinejoin="round" />
  </svg>
);

const Spark: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) => (
  <svg style={{ position: "absolute", left: x, top: y, filter: "drop-shadow(0 0 8px rgba(255,220,180,0.9))" }} width={s} height={s} viewBox="0 0 100 100">
    <path d="M50 6 L58 42 L94 50 L58 58 L50 94 L42 58 L6 50 L42 42 Z" fill={ink} />
  </svg>
);

export const CoverShop: React.FC<CoverShopProps> = ({
  bg, cutout, kicker, line1, line2, banner, note, accent = "#FF4FA0", glow2 = "#FFC870", cutX = 1020, cutH = 1080,
}) => (
  <AbsoluteFill style={{ backgroundColor: "#1c0a16", overflow: "hidden" }}>
    <Img src={staticFile(bg)} style={{ position: "absolute", inset: -40, width: 2000, height: 1160, objectFit: "cover", filter: "blur(7px) saturate(1.2) brightness(0.85)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(40,8,30,0.9) 0%, rgba(48,10,36,0.72) 34%, rgba(48,10,36,0.18) 56%, rgba(48,10,36,0.05) 70%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(70% 80% at 72% 55%, rgba(255,120,190,0.22) 0%, rgba(0,0,0,0) 55%), radial-gradient(90% 90% at 70% 50%, rgba(0,0,0,0) 55%, rgba(12,2,10,0.6) 100%)" }} />

    <Img src={staticFile(cutout)} style={{ position: "absolute", left: cutX, bottom: -40, height: cutH,
      filter: `drop-shadow(0 0 16px ${accent}) drop-shadow(0 0 44px ${glow2}) saturate(1.06) contrast(1.04)` }} />

    {/* title */}
    <div style={{ position: "absolute", left: 70, top: 120, width: 960 }}>
      <div style={{ fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 92, color: ink, transform: "rotate(-6deg)", transformOrigin: "left", marginLeft: 8,
        textShadow: `0 0 18px ${accent}` }}>
        {kicker}
      </div>
      <div style={{ fontFamily: anton.fontFamily, fontSize: 220, lineHeight: 0.95, letterSpacing: 2, marginTop: 4, color: accent,
        textShadow: `0 6px 0 #3a0a22, 0 0 30px ${accent}, 0 0 70px rgba(255,80,160,0.55)` }}>
        {line1}
      </div>
      <div style={{ fontFamily: anton.fontFamily, fontSize: 250, lineHeight: 0.9, color: ink,
        textShadow: `0 6px 0 #3a1a26, 0 0 30px ${glow2}, 0 0 70px rgba(255,190,100,0.55)` }}>
        {line2}
      </div>
      <div style={{ position: "relative", marginTop: 34, marginLeft: -10, width: 760, height: 100, transform: "rotate(-3deg)" }}>
        <svg width={760} height={100} viewBox="0 0 760 100" style={{ position: "absolute", left: 0, top: 0, filter: `drop-shadow(0 0 16px ${glow2})` }}>
          <path d="M14 30 C130 14 410 10 744 18 C752 42 748 64 740 80 C490 92 230 94 20 86 C6 68 8 48 14 30 Z" fill={glow2} />
        </svg>
        <div style={{ position: "absolute", left: 0, right: 0, top: 20, textAlign: "center", fontFamily: inter.fontFamily, fontWeight: 800, fontSize: 40, letterSpacing: 3, color: "#2b0d1c" }}>
          {banner}
        </div>
      </div>
    </div>

    {/* doodles */}
    <Bag x={1640} y={120} s={150} r={10} c={accent} />
    <Bag x={1770} y={300} s={100} r={-8} c="#E9A23B" />
    <Heart x={960} y={140} s={90} r={-14} />
    <Heart x={1060} y={70} s={54} r={10} fill={accent} />
    <Spark x={1540} y={70} s={40} />
    <Spark x={1860} y={520} s={34} />
    <Spark x={990} y={430} s={30} />
    {note ? (
      <>
        <div style={{ position: "absolute", left: 1500, top: 760, fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 74, color: ink,
          transform: "rotate(-8deg)", textShadow: `0 0 14px ${accent}, 0 2px 6px rgba(0,0,0,0.6)` }}>{note}</div>
        <svg style={{ position: "absolute", left: 1420, top: 640 }} width={170} height={150} viewBox="0 0 170 150">
          <path d="M150 130 C110 120 70 90 40 40" {...stroke} />
          <path d="M34 72 L38 36 L70 50" {...stroke} />
        </svg>
      </>
    ) : null}
  </AbsoluteFill>
);
