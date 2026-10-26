import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { loadFont as loadCreepster } from "@remotion/google-fonts/Creepster";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { HIcon, H } from "./HalloweenGraphics";

// Collab cover: two photos (left / right panels) and the title in a dark middle column, so the text can never
// touch either model.
const { fontFamily: SPOOK } = loadCreepster("normal", { weights: ["400"], subsets: ["latin"] });
const { fontFamily: TEXT } = loadInter("normal", { weights: ["700", "800"], subsets: ["latin"], ignoreTooManyRequestsWarning: true });

export type CoverDuoProps = {
  left: string; right: string; leftFocus?: string; rightFocus?: string;
  eyebrow: string; lines: string[]; sub: string; leftName: string; rightName: string;
};

const Panel: React.FC<{ src: string; focus: string; side: "left" | "right"; name: string; color: string }> = ({ src, focus, side, name, color }) => (
  <div style={{ position: "absolute", top: 0, [side]: 0, width: 1290, height: 2160, overflow: "hidden" }}>
    <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: focus, filter: "saturate(1.08) contrast(1.05)" }} />
    <div style={{ position: "absolute", inset: 0, background: `linear-gradient(${side === "left" ? 270 : 90}deg, rgba(18,10,26,0.85) 0%, rgba(18,10,26,0) 22%)` }} />
    <div style={{ position: "absolute", bottom: 90, [side === "left" ? "left" : "right"]: 80, padding: "14px 54px", borderRadius: 999,
      background: color, fontFamily: SPOOK, fontSize: 130, color: H.ink, boxShadow: H.glow }}>{name}</div>
  </div>
);

export const CoverDuo: React.FC<CoverDuoProps> = ({ left, right, leftFocus = "50% 30%", rightFocus = "50% 30%", eyebrow, lines, sub, leftName, rightName }) => (
  <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 40%, #3A1650 0%, ${H.ink} 70%)` }}>
    <Panel src={left} focus={leftFocus} side="left" name={leftName} color={H.purple} />
    <Panel src={right} focus={rightFocus} side="right" name={rightName} color={H.orange} />
    <div style={{ position: "absolute", left: 1290, width: 1260, top: 0, height: 2160, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", textAlign: "center" }}>
      <div style={{ display: "flex", gap: 40, marginBottom: 40 }}>
        <HIcon name="bat" size={150} color={H.purple} /><HIcon name="pumpkin" size={170} /><HIcon name="bat" size={150} color={H.purple} />
      </div>
      <div style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 64, letterSpacing: 16, color: H.slime }}>{eyebrow.toUpperCase()}</div>
      {lines.map((l, i) => (
        <div key={i} style={{ fontFamily: SPOOK, fontSize: 250, lineHeight: 1.0, color: i === lines.length - 1 ? H.orange : H.bone,
          textShadow: i === lines.length - 1 ? "0 0 60px rgba(255,122,26,0.8)" : "0 10px 30px rgba(0,0,0,0.7)" }}>{l}</div>
      ))}
      <div style={{ fontFamily: TEXT, fontWeight: 700, fontSize: 70, color: H.bone, marginTop: 40, lineHeight: 1.3, maxWidth: 1100 }}>{sub}</div>
    </div>
  </AbsoluteFill>
);
