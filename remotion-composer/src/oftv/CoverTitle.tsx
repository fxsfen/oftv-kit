import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";

// Reusable video cover: real photo + left-side title block
// (eyebrow / bold grotesk headline / hand-written accent line / subline).

const inter = loadInter("normal", { weights: ["600", "900"], ignoreTooManyRequestsWarning: true });
const caveat = loadCaveat("normal", { weights: ["700"], ignoreTooManyRequestsWarning: true });

const CREAM = "#FFF6EA";

export type CoverTitleProps = {
  src: string;
  eyebrow: string;
  headline: string;
  script: string;
  sub: string;
  accent?: string;
  shade?: number; // strength of the readability shade (0-1)
  side?: "left" | "right"; // which side carries the title block
  top?: number; // px from the top; omitted = vertically centred
  objectPosition?: string;
  scale?: number; // shrink the whole title block (e.g. 0.55) to keep a prop / face visible
};

const Stroke: React.FC<{ width: number; color: string }> = ({ width, color }) => (
  <svg width={width} height={70} viewBox="0 0 600 70" style={{ display: "block" }}>
    <path d="M8 44 C 120 22, 260 18, 420 26 S 560 38, 592 30" fill="none" stroke={color} strokeWidth={11} strokeLinecap="round" />
    <path d="M40 58 C 170 40, 330 38, 470 44 S 560 52, 580 48" fill="none" stroke={color} strokeWidth={6} strokeLinecap="round" opacity={0.75} />
  </svg>
);

export const CoverTitle: React.FC<CoverTitleProps> = ({
  src, eyebrow, headline, script, sub, accent = "#F4C04E", shade = 0.85, side = "left", top, objectPosition = "50% 50%", scale = 1,
}) => (
  <AbsoluteFill style={{ backgroundColor: "#1a1716" }}>
    <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition, filter: "saturate(1.05) contrast(1.04)" }} />
    <AbsoluteFill
      style={{
        background: `linear-gradient(${side === "left" ? 90 : 270}deg, rgba(22,17,16,${shade}) 0%, rgba(22,17,16,${shade * 0.78}) 28%, rgba(22,17,16,${shade * 0.2}) 42%, rgba(22,17,16,0) 50%)`,
      }}
    />
    <AbsoluteFill style={{ background: "radial-gradient(120% 90% at 65% 40%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.25) 100%)" }} />
    <div style={{ position: "absolute", ...(side === "left" ? { left: 150 } : { right: 150 }), top: top ?? 0, bottom: top === undefined ? 0 : undefined, width: 1400, display: "flex", flexDirection: "column", justifyContent: top === undefined ? "center" : "flex-start", textAlign: side === "right" ? "right" : "left", alignItems: side === "right" ? "flex-end" : "flex-start",
      transform: `scale(${scale})`, transformOrigin: `${side === "right" ? "right" : "left"} ${top === undefined ? "center" : "top"}` }}>
      <div style={{ fontFamily: inter.fontFamily, fontWeight: 600, fontSize: 64, letterSpacing: 12, color: accent }}>{eyebrow}</div>
      <div
        style={{
          fontFamily: inter.fontFamily, fontWeight: 900, fontSize: 210, lineHeight: 0.95, letterSpacing: -3,
          color: CREAM, marginTop: 24, textShadow: "0 8px 40px rgba(0,0,0,0.35)", whiteSpace: "pre-line",
        }}
      >
        {headline}
      </div>
      <div
        style={{
          fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 330, lineHeight: 0.85, color: accent,
          marginTop: 6, transform: "rotate(-4deg)", transformOrigin: "left center", textShadow: "0 8px 36px rgba(0,0,0,0.4)",
        }}
      >
        {script}
      </div>
      <div style={{ marginTop: 4, marginLeft: 16, transform: "rotate(-3deg)" }}>
        <Stroke width={820} color={accent} />
      </div>
      <div style={{ marginTop: 44, fontFamily: inter.fontFamily, fontWeight: 600, fontSize: 62, color: "rgba(255,246,234,0.9)" }}>
        {sub}
      </div>
    </div>
  </AbsoluteFill>
);


