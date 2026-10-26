import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";

// Split cover: photo on the left, calm colour panel with the title on the
// right — for photos where the subject fills the frame and leaves no clean
// space for type.

const inter = loadInter("normal", { weights: ["600", "900"], ignoreTooManyRequestsWarning: true });
const caveat = loadCaveat("normal", { weights: ["700"], ignoreTooManyRequestsWarning: true });

export type CoverSplitProps = {
  src: string;
  focus?: string; // CSS object-position for the photo
  photoWidth?: number; // fraction of the frame
  eyebrow: string;
  headline: string;
  script: string;
  sub: string;
  panel?: string;
  ink?: string;
  accent?: string;
};

const Stroke: React.FC<{ width: number; color: string }> = ({ width, color }) => (
  <svg width={width} height={70} viewBox="0 0 600 70" style={{ display: "block" }}>
    <path d="M8 44 C 120 22, 260 18, 420 26 S 560 38, 592 30" fill="none" stroke={color} strokeWidth={11} strokeLinecap="round" />
    <path d="M40 58 C 170 40, 330 38, 470 44 S 560 52, 580 48" fill="none" stroke={color} strokeWidth={6} strokeLinecap="round" opacity={0.7} />
  </svg>
);

export const CoverSplit: React.FC<CoverSplitProps> = ({
  src, focus = "35% 20%", photoWidth = 0.6, eyebrow, headline, script, sub,
  panel = "#F4ECE3", ink = "#2A2320", accent = "#C9785F",
}) => {
  const pw = Math.round(3840 * photoWidth);
  return (
    <AbsoluteFill style={{ backgroundColor: panel }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: pw, height: 2160, overflow: "hidden" }}>
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: focus, filter: "saturate(1.05) contrast(1.03)" }} />
        {/* soft hand-off into the panel instead of a hard seam */}
        <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: 260, background: `linear-gradient(90deg, rgba(0,0,0,0), ${panel})` }} />
      </div>
      <div
        style={{
          position: "absolute", left: pw - 40, right: 120, top: 0, bottom: 0,
          display: "flex", flexDirection: "column", justifyContent: "center",
        }}
      >
        <div style={{ fontFamily: inter.fontFamily, fontWeight: 600, fontSize: 72, letterSpacing: 14, color: accent }}>{eyebrow}</div>
        <div style={{ fontFamily: inter.fontFamily, fontWeight: 900, fontSize: 186, lineHeight: 0.95, letterSpacing: -3, color: ink, marginTop: 26, whiteSpace: "pre-line" }}>
          {headline}
        </div>
        <div
          style={{
            fontFamily: caveat.fontFamily, fontWeight: 700, fontSize: 390, lineHeight: 0.85, color: accent,
            marginTop: 8, transform: "rotate(-4deg)", transformOrigin: "left center",
          }}
        >
          {script}
        </div>
        <div style={{ marginTop: 6, marginLeft: 12, transform: "rotate(-3deg)" }}>
          <Stroke width={900} color={accent} />
        </div>
        <div style={{ marginTop: 48, fontFamily: inter.fontFamily, fontWeight: 600, fontSize: 70, color: ink, opacity: 0.8 }}>
          {sub}
        </div>
      </div>
    </AbsoluteFill>
  );
};

