import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadFredoka } from "@remotion/google-fonts/Fredoka";

// Daisy's cover in the same language as her section titles (DaisyGraphics): lavender bubble
// letters with a white rim and dark 3D drop, white dry-brush swipes and sparkle stars.
// variant "split": before | after photos with labels; variant "single": one photo + title block.

const { fontFamily: bubbly } = loadFredoka("normal", { weights: ["700"], ignoreTooManyRequestsWarning: true });
const LAV = "#D8A4F0";
const INK = "#24152F";

const Bubble: React.FC<{ text: string; size: number; color?: string; style?: React.CSSProperties }> = ({
  text, size, color = LAV, style,
}) => {
  const base: React.CSSProperties = {
    position: "absolute", left: 0, top: 0, fontFamily: bubbly, fontWeight: 700, fontSize: size,
    lineHeight: 1, whiteSpace: "pre", letterSpacing: 1,
  };
  const k = size / 215; // stroke widths scale with the title size used in the video
  return (
    <div style={{ position: "relative", ...style }}>
      <div style={{ ...base, position: "relative", visibility: "hidden" }}>{text}</div>
      <div style={{ ...base, color: INK, WebkitTextStroke: `${26 * k}px ${INK}`, transform: `translate(${12 * k}px, ${15 * k}px)`,
        filter: `drop-shadow(0 0 ${30 * k}px rgba(200,120,255,0.55))` }}>{text}</div>
      <div style={{ ...base, color: "white", WebkitTextStroke: `${22 * k}px white` }}>{text}</div>
      <div style={{ ...base, color }}>{text}</div>
    </div>
  );
};

const Brush: React.FC<{ w: number; h: number; style?: React.CSSProperties }> = ({ w, h, style }) => {
  const rows = 22;
  return (
    <svg width={w} height={h} style={{ position: "absolute", overflow: "visible", ...style }}>
      {Array.from({ length: rows }, (_, i) => {
        const r1 = ((i * 73) % 29) / 29;
        const r2 = ((i * 41) % 17) / 17;
        const y = (h * i) / rows;
        const t = (h / rows) * (1.25 + r2 * 0.6);
        const x0 = -20 + r2 * 60;
        const x1 = w * (0.8 + r1 * 0.2);
        return (
          <path key={i} fill={`rgba(255,255,255,${0.9 + r1 * 0.08})`}
            d={`M${x0},${y} L${x1 - 30},${y} L${x1},${y + t * 0.35} L${x1 - 55},${y + t * 0.6} L${x1 - 12},${y + t} L${x0 + 25},${y + t} Z`} />
        );
      })}
    </svg>
  );
};

const Star: React.FC<{ x: number; y: number; s: number; gold?: boolean }> = ({ x, y, s, gold }) => (
  <svg width={s} height={s} viewBox="-50 -50 100 100" style={{ position: "absolute", left: x - s / 2, top: y - s / 2, overflow: "visible" }}>
    <path d="M0,-50 C4,-12 12,-4 50,0 C12,4 4,12 0,50 C-4,12 -12,4 -50,0 C-12,-4 -4,-12 0,-50 Z"
      fill={gold ? "#FFE7A3" : "#FFF0FB"} style={{ filter: `drop-shadow(0 0 ${s * 0.15}px ${gold ? "#FFC94D" : "#E58CFF"})` }} />
  </svg>
);

export type CoverDaisyProps = {
  variant: "split" | "single";
  before?: string;
  after?: string;
  src?: string;
  labelA?: string;
  labelB?: string;
  lines?: string[];
  sub?: string;
  side?: "left" | "right";   // where the title block sits (single); keep it off the model
  size?: number;             // bubble title size (single), 300 by default
  x?: number;                // title block left edge (single), overrides the side default
};

export const CoverDaisy: React.FC<CoverDaisyProps> = ({
  variant, before = "", after = "", src = "", labelA = "Basic", labelB = "Stylish", lines = [], sub = "", side = "right", size = 300, x,
}) => {
  if (variant === "split") {
    return (
      <AbsoluteFill style={{ background: "#EDE4F2" }}>
        <Img src={staticFile(before)} style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 2160, objectFit: "cover",
          filter: "saturate(0.85) brightness(0.98)" }} />
        <Img src={staticFile(after)} style={{ position: "absolute", left: 1920, top: 0, width: 1920, height: 2160, objectFit: "cover",
          filter: "saturate(1.08) contrast(1.04)" }} />
        {/* torn white seam between the halves */}
        <svg width={220} height={2160} style={{ position: "absolute", left: 1810, top: 0 }}>
          {Array.from({ length: 28 }, (_, i) => {
            const y = (2160 * i) / 27;
            const dx = ((i * 53) % 23) - 11;
            return <rect key={i} x={86 + dx} y={y} width={48 + ((i * 29) % 15)} height={2160 / 27 + 2} fill="white" />;
          })}
        </svg>
        <AbsoluteFill style={{ background: "linear-gradient(0deg, rgba(36,21,47,0.45) 0%, rgba(36,21,47,0) 30%)" }} />
        {/* labels sit on the empty wall next to the seam; she stands at the outer edges */}
        <div style={{ position: "absolute", left: 1180, top: 1420 }}>
          <Brush w={700} h={200} style={{ left: -60, top: 60 }} />
          <Bubble text={labelA} size={240} color="#BDB3C7" />
        </div>
        <div style={{ position: "absolute", left: 2010, top: 1420 }}>
          <Brush w={810} h={200} style={{ left: -60, top: 60 }} />
          <Bubble text={labelB} size={240} />
        </div>
        {/* arrow across the seam, above the labels */}
        <svg width={520} height={260} viewBox="0 0 520 260" style={{ position: "absolute", left: 1660, top: 1080, overflow: "visible" }}>
          <path d="M20 170 C 150 40, 330 40, 470 120" fill="none" stroke={INK} strokeWidth={38} strokeLinecap="round" />
          <path d="M20 170 C 150 40, 330 40, 470 120" fill="none" stroke="white" strokeWidth={22} strokeLinecap="round" />
          <path d="M400 70 L490 128 L392 160" fill="none" stroke={INK} strokeWidth={38} strokeLinecap="round" strokeLinejoin="round" />
          <path d="M400 70 L490 128 L392 160" fill="none" stroke="white" strokeWidth={22} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <Star x={1940} y={1880} s={170} gold />
        <Star x={2680} y={1760} s={90} />
        <Star x={1120} y={1380} s={110} />
        <Star x={1560} y={1800} s={80} />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ background: "#EDE4F2" }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(1.06) contrast(1.04)" }} />
      <AbsoluteFill style={{ background: `linear-gradient(${side === "left" ? 90 : 270}deg, rgba(36,21,47,0.38) 0%, rgba(36,21,47,0.12) 40%, rgba(36,21,47,0) 55%)` }} />
      <div style={{ position: "absolute", left: x ?? (side === "left" ? 150 : 2160), top: 600 }}>
        <Brush w={1500 * size / 300} h={520 * size / 300} style={{ left: -70, top: 140 * size / 300 }} />
        {lines.map((ln, i) => (
          <Bubble key={i} text={ln} size={size} style={{ marginTop: i ? -10 : 0 }} />
        ))}
        {sub ? (
          <div style={{ position: "relative", marginTop: 110, marginLeft: 20, display: "inline-block", padding: "26px 60px", borderRadius: 999,
            background: "rgba(255,255,255,0.95)", color: INK, fontFamily: bubbly, fontWeight: 700, fontSize: 104,
            boxShadow: "0 14px 40px rgba(36,21,47,0.3)" }}>{sub}</div>
        ) : null}
      </div>
      {side === "left" ? (<>
        <Star x={240} y={430} s={200} gold />
        <Star x={420} y={330} s={110} />
        <Star x={1500} y={1820} s={120} />
        <Star x={200} y={1900} s={80} />
      </>) : (<>
        <Star x={3600} y={430} s={200} gold />
        <Star x={3420} y={330} s={110} />
        <Star x={3500} y={1720} s={140} />
        <Star x={3700} y={1880} s={80} />
      </>)}
    </AbsoluteFill>
  );
};
