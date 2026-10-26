import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";

// Video cover (thumbnail) for the drawing talk. Real photo, typographic
// treatment only: a clean grotesk paired with a hand-drawn script so the
// title itself feels sketched.

const inter = loadInter("normal", { weights: ["600", "800", "900"] });
const caveat = loadCaveat("normal", { weights: ["700"] });

const CREAM = "#FFF6EA";
const PENCIL = "#F4C04E"; // picks up the yellow pencil in her hand

// Loose pencil-stroke underline (two passes, like a quick sketch).
const Scribble: React.FC<{ width: number }> = ({ width }) => (
  <svg width={width} height={70} viewBox="0 0 600 70" style={{ display: "block" }}>
    <path
      d="M8 44 C 120 22, 260 18, 420 26 S 560 38, 592 30"
      fill="none"
      stroke={PENCIL}
      strokeWidth={11}
      strokeLinecap="round"
    />
    <path
      d="M40 58 C 170 40, 330 38, 470 44 S 560 52, 580 48"
      fill="none"
      stroke={PENCIL}
      strokeWidth={6}
      strokeLinecap="round"
      opacity={0.75}
    />
  </svg>
);

export type CoverProps = { variant: "a" | "b" };

export const Cover: React.FC<CoverProps> = ({ variant }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1716" }}>
      <Img
        src={staticFile("oftv/cover_src.jpg")}
        style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(1.06) contrast(1.04)" }}
      />
      {/* readability: soft warm shade on the left third only, face stays untouched */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(90deg, rgba(22,17,16,0.82) 0%, rgba(22,17,16,0.62) 28%, rgba(22,17,16,0.15) 44%, rgba(22,17,16,0) 52%)",
        }}
      />
      <AbsoluteFill
        style={{ background: "radial-gradient(120% 90% at 60% 40%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.28) 100%)" }}
      />

      {variant === "a" ? (
        <div style={{ position: "absolute", left: 150, top: 470, width: 1300 }}>
          <div
            style={{
              fontFamily: inter.fontFamily,
              fontWeight: 900,
              fontSize: 205,
              lineHeight: 0.95,
              letterSpacing: -2,
              color: CREAM,
              textShadow: "0 8px 40px rgba(0,0,0,0.35)",
            }}
          >
            WHY I
            <br />
            LOVE
          </div>
          <div
            style={{
              fontFamily: caveat.fontFamily,
              fontWeight: 700,
              fontSize: 400,
              lineHeight: 0.85,
              color: PENCIL,
              marginTop: 6,
              marginLeft: -8,
              transform: "rotate(-4deg)",
              transformOrigin: "left center",
              textShadow: "0 8px 36px rgba(0,0,0,0.4)",
            }}
          >
            drawing
          </div>
          <div style={{ marginTop: -4, marginLeft: 10, transform: "rotate(-3deg)" }}>
            <Scribble width={980} />
          </div>
          <div
            style={{
              marginTop: 40,
              fontFamily: inter.fontFamily,
              fontWeight: 600,
              fontSize: 62,
              letterSpacing: 10,
              color: "rgba(255,246,234,0.86)",
            }}
          >
            MY CREATIVE ESCAPE
          </div>
        </div>
      ) : (
        <div style={{ position: "absolute", left: 150, top: 470, width: 1350 }}>
          <div
            style={{
              fontFamily: inter.fontFamily,
              fontWeight: 600,
              fontSize: 64,
              letterSpacing: 12,
              color: PENCIL,
            }}
          >
            SKETCHBOOK DIARIES
          </div>
          <div
            style={{
              fontFamily: inter.fontFamily,
              fontWeight: 900,
              fontSize: 200,
              lineHeight: 0.95,
              letterSpacing: -3,
              color: CREAM,
              marginTop: 22,
              textShadow: "0 8px 40px rgba(0,0,0,0.35)",
            }}
          >
            MY CREATIVE
          </div>
          <div
            style={{
              fontFamily: caveat.fontFamily,
              fontWeight: 700,
              fontSize: 400,
              lineHeight: 0.8,
              color: PENCIL,
              marginTop: 0,
              transform: "rotate(-4deg)",
              transformOrigin: "left center",
              textShadow: "0 8px 36px rgba(0,0,0,0.4)",
            }}
          >
            escape
          </div>
          <div style={{ marginTop: 0, marginLeft: 20, transform: "rotate(-3deg)" }}>
            <Scribble width={860} />
          </div>
          <div
            style={{
              marginTop: 40,
              fontFamily: inter.fontFamily,
              fontWeight: 600,
              fontSize: 60,
              color: "rgba(255,246,234,0.88)",
            }}
          >
            Why drawing means so much to me
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};

