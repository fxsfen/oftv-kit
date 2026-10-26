import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont as loadFredoka } from "@remotion/google-fonts/Fredoka";
import { loadFont as loadNunito } from "@remotion/google-fonts/Nunito";

// Daisy's look (from her reference edit): an OnlyFans pill that types her handle, and
// bubbly lavender section titles on a white brush swipe with a sparkle flash + twinkles.
// Both sit top-left, 4K transparent, length from the `dur` prop.

const { fontFamily: bubbly } = loadFredoka("normal", { weights: ["700"] });
const { fontFamily: rounded } = loadNunito("normal", { weights: ["800", "900"] });

const OF_BLUE = "#12AEEF";
const LAVENDER_FILL = "#D8A4F0";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const useOut = (outFrames: number) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return interpolate(frame, [durationInFrames - outFrames, durationInFrames - 1], [0, 1], {
    ...clamp,
    easing: Easing.in(Easing.cubic),
  });
};

// Four-point sparkle star.
const Sparkle: React.FC<{ size: number; color: string; glow?: string; style?: React.CSSProperties }> = ({
  size,
  color,
  glow,
  style,
}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100" style={{ position: "absolute", overflow: "visible", ...style }}>
    <path
      d="M0,-50 C4,-12 12,-4 50,0 C12,4 4,12 0,50 C-4,12 -12,4 -50,0 C-12,-4 -4,-12 0,-50 Z"
      fill={color}
      style={{ filter: glow ? `drop-shadow(0 0 ${size * 0.12}px ${glow})` : undefined }}
    />
  </svg>
);

const OfMark: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <circle cx="36" cy="54" r="24" fill="none" stroke={OF_BLUE} strokeWidth="15" />
    <path d="M52,34 C64,30 82,30 96,30 C90,44 78,52 64,54 C72,56 80,56 86,55 C78,68 64,74 50,72 Z" fill={OF_BLUE} />
  </svg>
);

export type DaisyTagProps = { tag: string; dur?: number };

export const DaisyTag: React.FC<DaisyTagProps> = ({ tag }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const out = useOut(12);
  const H = 250;
  // 1) logo bubble pops, 2) pill stretches out, 3) handle types in.
  const pop = spring({ frame, fps, config: { damping: 9, stiffness: 170, mass: 0.7 } });
  const grow = spring({ frame: frame - 7, fps, config: { damping: 18, stiffness: 120 } });
  const typed = Math.round(interpolate(frame, [11, 11 + tag.length * 1.6], [0, tag.length], clamp));
  const textW = tag.length * 92 + 90;
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 240,
          top: 150,
          height: H,
          width: H + textW * grow,
          borderRadius: H / 2,
          background: "rgba(232, 236, 240, 0.94)",
          boxShadow: "0 16px 44px rgba(0,0,0,0.22)",
          opacity: 1 - out,
          transform: `scale(${pop * (1 - out * 0.15)})`,
          transformOrigin: `${H / 2}px ${H / 2}px`,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
        }}
      >
        <div style={{ width: H, height: H, flex: "none", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <OfMark size={H * 0.66} />
        </div>
        <div
          style={{
            fontFamily: rounded,
            fontWeight: 900,
            fontSize: 150,
            color: OF_BLUE,
            whiteSpace: "nowrap",
            marginLeft: -10,
            letterSpacing: 1,
          }}
        >
          {tag.slice(0, typed)}
          <span style={{ opacity: 0.35 }}>{tag.slice(typed, typed + 2)}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Dry-brush swipe: a stack of white bristle strokes with ragged ends and a few gaps,
// wiped in from the left.
const BrushSwipe: React.FC<{ w: number; h: number; reveal: number }> = ({ w, h, reveal }) => {
  const rows = 26;
  const strokes = Array.from({ length: rows }, (_, i) => {
    const r1 = ((i * 73) % 29) / 29;
    const r2 = ((i * 41) % 17) / 17;
    return {
      y: (h * i) / rows,
      x0: -20 + r2 * 60,
      x1: w * (0.78 + r1 * 0.22),
      t: (h / rows) * (1.25 + r2 * 0.6),
      a: 0.9 + r1 * 0.08,
    };
  });
  return (
    <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
      <defs>
        <clipPath id="brushReveal">
          <rect x={-80} y={-40} width={(w + 160) * reveal} height={h + 80} />
        </clipPath>
      </defs>
      <g clipPath="url(#brushReveal)">
        {strokes.map((st, i) => (
          <path key={i}
            d={`M${st.x0},${st.y} L${st.x1 - 30},${st.y} L${st.x1},${st.y + st.t * 0.35} L${st.x1 - 55},${st.y + st.t * 0.6}
               L${st.x1 - 12},${st.y + st.t} L${st.x0 + 25},${st.y + st.t} Z`}
            fill={`rgba(255,255,255,${st.a})`} />
        ))}
      </g>
    </svg>
  );
};

export type DaisyTitleProps = { lines: string[]; dur?: number };

export const DaisyTitle: React.FC<DaisyTitleProps> = ({ lines }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const out = useOut(12);
  const FS = 215;
  const lineH = FS * 0.98;
  const longest = Math.max(...lines.map((l) => l.length));
  const textW = longest * FS * 0.5;
  const textH = lines.length * lineH;
  const reveal = interpolate(frame, [3, 13], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  // Big sparkle flash that opens the title, and a purple glow that settles.
  const flash = interpolate(frame, [0, 5, 13], [0, 1, 0], clamp);
  const flashRot = interpolate(frame, [0, 13], [-20, 25], clamp);
  const glow = interpolate(frame, [6, 14, 34], [0, 1, 0.25], clamp);
  const base: React.CSSProperties = {
    position: "absolute",
    left: 0,
    top: 0,
    fontFamily: bubbly,
    fontWeight: 700,
    fontSize: FS,
    lineHeight: `${lineH}px`,
    letterSpacing: 1,
  };
  const layers: React.CSSProperties[] = [
    // dark 3D drop under the letters
    { ...base, color: "#24152F", WebkitTextStroke: "26px #24152F", transform: "translate(12px, 15px)",
      filter: `drop-shadow(0 0 ${40 * glow}px rgba(200,120,255,${glow}))` },
    // white rim
    { ...base, color: "white", WebkitTextStroke: "22px white" },
    // lavender fill
    { ...base, color: LAVENDER_FILL },
  ];
  // Letters pop in one by one (same timing on every layer).
  const renderLines = () =>
    lines.map((ln, li) => (
      <div key={li} style={{ whiteSpace: "pre" }}>
        {ln.split("").map((ch, ci) => {
          const s = spring({ frame: frame - 6 - ci * 0.9 - li * 5, fps,
            config: { damping: 10, stiffness: 200, mass: 0.6 } });
          return (
            <span key={ci} style={{ display: "inline-block", transform: `scale(${s}) translateY(${(1 - s) * 40}px)` }}>
              {ch}
            </span>
          );
        })}
      </div>
    ));
  const L = 110, T = 80;
  const twinkles = [
    { x: 90, y: textH + 70, s: 120, d: 14 },
    { x: 260, y: textH + 50, s: 150, d: 18, gold: true },
    { x: 430, y: textH + 80, s: 110, d: 22 },
    { x: textW + 40, y: 60, s: 90, d: 26 },
    { x: textW * 0.6, y: textH + 90, s: 70, d: 30 },
  ];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: L, top: T, opacity: 1 - out,
        transform: `scale(${1 - out * 0.12})`, transformOrigin: "0 0" }}>
        <div style={{ position: "absolute", left: -110, top: lineH * 0.45 }}>
          <BrushSwipe w={textW + 120} h={textH - lineH * 0.2} reveal={reveal} />
        </div>
        <div style={{ position: "relative", width: textW, height: textH }}>
          {layers.map((st, i) => <div key={i} style={st}>{renderLines()}</div>)}
        </div>
        {twinkles.map((t, i) => {
          const a = interpolate(frame - t.d, [0, 6, 16, 26], [0, 1, 0.55, 1], clamp);
          const sc = 0.6 + 0.4 * Math.abs(Math.sin((frame - t.d) / 6));
          return frame > t.d ? (
            <Sparkle key={i} size={t.s * sc} color={t.gold ? "#FFE7A3" : "#FFE8F7"}
              glow={t.gold ? "#FFC94D" : "#E58CFF"}
              style={{ left: t.x - (t.s * sc) / 2, top: t.y - (t.s * sc) / 2, opacity: a }} />
          ) : null;
        })}
      </div>
      {flash > 0 && (
        <Sparkle size={900 * (0.4 + flash * 0.8)} color="#FFFFFF" glow="#C77DFF"
          style={{ left: 420 - 450 * (0.4 + flash * 0.8), top: 260 - 450 * (0.4 + flash * 0.8), opacity: flash,
            transform: `rotate(${flashRot}deg)` }} />
      )}
    </AbsoluteFill>
  );
};
