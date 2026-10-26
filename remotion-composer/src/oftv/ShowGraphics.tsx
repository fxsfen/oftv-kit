import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont as loadBaloo } from "@remotion/google-fonts/Baloo2";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

// "Show" graphics for OFTV edits: transparent 4K pop-ups rendered as VP9+alpha
// and composited by FFmpeg. Warm cozy palette, rounded display font, springy
// pops with overshoot; every element has an enter and an exit.

const { fontFamily: DISPLAY } = loadBaloo("normal", { weights: ["600", "700", "800"], subsets: ["latin"] });
const { fontFamily: TEXT } = loadInter("normal", { weights: ["500", "600", "700", "800"], subsets: ["latin"] });

export const C = {
  cream: "#FFF6EA",
  ink: "#1C1A22",
  orange: "#FF7A3D",
  pink: "#FF5C8A",
  teal: "#2EC4B6",
  yellow: "#FFC93C",
  violet: "#7C5CFF",
  shadow: "0 30px 70px rgba(20, 10, 0, 0.35)",
};
const PALETTE: Record<string, string> = { orange: C.orange, pink: C.pink, teal: C.teal, yellow: C.yellow, violet: C.violet };
const col = (c?: string) => (c && PALETTE[c]) || c || C.orange;

// ---------- motion helpers ----------
const usePop = (delay = 0, outFrames = 10) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 11, stiffness: 170, mass: 0.8 } });
  const exit = interpolate(frame, [durationInFrames - outFrames, durationInFrames - 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.back(1.6)),
  });
  return { frame, fps, enter, exit, durationInFrames };
};
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ---------- icons (simple inline SVG, stroke-based) ----------
export const Icon: React.FC<{ name: string; size: number; color?: string }> = ({ name, size, color = "#fff" }) => {
  const p = { fill: "none", stroke: color, strokeWidth: 2.4, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  const f = { fill: color };
  let body: React.ReactNode;
  switch (name) {
    case "box":
      body = (<><path {...p} d="M3 8l9-4 9 4v9l-9 4-9-4z" /><path {...p} d="M3 8l9 4 9-4M12 12v9" /></>);
      break;
    case "wrench":
      body = <path {...p} d="M14.5 6.5a4 4 0 0 0 5 5l-9 9a2.1 2.1 0 0 1-3-3l9-9a4 4 0 0 0-2-2zM16 3l-2 3.5" />;
      break;
    case "paw":
      body = (<><ellipse {...f} cx="12" cy="16" rx="4.6" ry="3.8" /><circle {...f} cx="6" cy="10.5" r="2.1" /><circle {...f} cx="18" cy="10.5" r="2.1" /><circle {...f} cx="9.2" cy="6.5" r="2.1" /><circle {...f} cx="14.8" cy="6.5" r="2.1" /></>);
      break;
    case "heart":
      body = <path {...f} d="M12 21s-7.5-4.6-9.3-9.2C1.4 8.4 3.6 5 7 5c2 0 3.3 1 5 3 1.7-2 3-3 5-3 3.4 0 5.6 3.4 4.3 6.8C19.5 16.4 12 21 12 21z" />;
      break;
    case "check":
      body = <path {...p} strokeWidth={3.2} d="M4.5 12.5l5 5 10-11" />;
      break;
    case "star":
      body = <path {...f} d="M12 2.8l2.8 5.9 6.4.8-4.7 4.4 1.2 6.4L12 17.2l-5.7 3.1 1.2-6.4-4.7-4.4 6.4-.8z" />;
      break;
    case "home":
      body = (<><path {...p} d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z" /></>);
      break;
    case "ruler":
      body = (<><rect {...p} x="2.5" y="8" width="19" height="8" rx="1.5" /><path {...p} d="M6.5 8v3M10 8v4M13.5 8v3M17 8v4" /></>);
      break;
    case "spark":
      body = <path {...f} d="M12 1.5l2.2 7.3 7.3 2.2-7.3 2.2L12 20.5l-2.2-7.3L2.5 11l7.3-2.2z" />;
      break;
    case "eyes":
      body = (<><ellipse {...p} cx="7.5" cy="12" rx="4" ry="5.5" /><ellipse {...p} cx="16.5" cy="12" rx="4" ry="5.5" /><circle {...f} cx="8.6" cy="13" r="1.9" /><circle {...f} cx="17.6" cy="13" r="1.9" /></>);
      break;
    case "clock":
      body = (<><circle {...p} cx="12" cy="12" r="9" /><path {...p} d="M12 7v5l3.5 2" /></>);
      break;
    case "crown":
      body = <path {...f} d="M3 18l-1-11 5.5 4L12 4l4.5 7L22 7l-1 11z" />;
      break;
    default:
      body = <circle {...f} cx="12" cy="12" r="6" />;
  }
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{ display: "block", overflow: "visible" }}>
      {body}
    </svg>
  );
};

// ---------- 1. Show opener title ----------
export type ShowTitleProps = { eyebrow: string; lines: string[]; sub?: string };
export const ShowTitle: React.FC<ShowTitleProps> = ({ eyebrow, lines, sub }) => {
  const { frame, fps, enter, exit } = usePop(0, 14);
  const fade = 1 - exit;
  const words = lines.map((l) => l.split(" "));
  let k = 0;
  const swoosh = interpolate(frame, [0.9 * fps, 1.5 * fps], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ opacity: fade }}>
      {/* soft vignette behind the type so it reads on any footage */}
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 60% 70% at 18% 62%, rgba(20,10,0,0.55), rgba(20,10,0,0) 70%)", opacity: enter }} />
      <div style={{ position: "absolute", left: 230, top: 760, transform: `translateY(${exit * 60}px)` }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 26, padding: "18px 44px 18px 26px", borderRadius: 999, background: C.orange, transform: `scale(${enter})`, transformOrigin: "left center", boxShadow: C.shadow }}>
          <Icon name="paw" size={64} />
          <span style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 58, color: "#fff", letterSpacing: 10 }}>{eyebrow.toUpperCase()}</span>
        </div>
        <div style={{ marginTop: 30 }}>
          {words.map((ws, li) => (
            <div key={li} style={{ display: "flex", gap: 44, lineHeight: 1 }}>
              {ws.map((w) => {
                const d = 6 + k++ * 4;
                const s = spring({ frame: frame - d, fps, config: { damping: 12, stiffness: 160 } });
                return (
                  <span key={w + d} style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 290, color: li === lines.length - 1 ? C.yellow : C.cream, textShadow: "0 14px 40px rgba(0,0,0,0.45)", transform: `translateY(${(1 - s) * 140}px) rotate(${(1 - s) * -8}deg)`, opacity: Math.min(1, s * 1.4), display: "inline-block" }}>
                    {w}
                  </span>
                );
              })}
            </div>
          ))}
        </div>
        <svg width={1500} height={80} style={{ marginTop: -10 }}>
          <path d="M10 50 C 300 10, 700 80, 1490 30" stroke={C.orange} strokeWidth={22} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - swoosh} />
        </svg>
        {sub && (
          <div style={{ fontFamily: TEXT, fontWeight: 600, fontSize: 70, color: "#fff", marginTop: 10, opacity: interpolate(frame, [1.2 * fps, 1.6 * fps], [0, 1], clamp), textShadow: "0 6px 20px rgba(0,0,0,0.5)" }}>
            {sub}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ---------- 2. Pop sticker (the main "semantic pop-up") ----------
export type PopStickerProps = { text: string; sub?: string; icon?: string; color?: string; x: number; y: number; tilt?: number; anchor?: "left" | "right" };
export const PopSticker: React.FC<PopStickerProps> = ({ text, sub, icon = "spark", color, x, y, tilt = -3, anchor = "left" }) => {
  const { frame, fps, enter, exit } = usePop(0, 10);
  const c = col(color);
  const s = enter * (1 - exit);
  const bob = Math.sin((frame / fps) * 2.4) * 8;
  const iconPop = spring({ frame: frame - 5, fps, config: { damping: 8, stiffness: 200 } });
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: anchor === "left" ? x : undefined,
          right: anchor === "right" ? 3840 - x : undefined,
          top: y,
          transform: `translateY(${bob}px) rotate(${tilt + (1 - enter) * 10}deg) scale(${s})`,
          transformOrigin: anchor === "left" ? "left center" : "right center",
          display: "flex",
          alignItems: "center",
          gap: 40,
          padding: "34px 64px 34px 34px",
          borderRadius: 64,
          background: C.cream,
          boxShadow: `${C.shadow}, inset 0 -10px 0 rgba(0,0,0,0.06)`,
          border: `8px solid ${c}`,
        }}
      >
        <div style={{ width: 170, height: 170, borderRadius: 48, background: c, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${iconPop}) rotate(${(1 - iconPop) * -30}deg)` }}>
          <Icon name={icon} size={110} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 112, color: C.ink, lineHeight: 1.0, whiteSpace: "nowrap" }}>{text}</div>
          {sub && <div style={{ fontFamily: TEXT, fontWeight: 600, fontSize: 56, color: "rgba(28,26,34,0.62)", whiteSpace: "nowrap" }}>{sub}</div>}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- 3. Cat name tag (lower third) ----------
export type NameTagProps = { name: string; role: string; color?: string; x?: number; y?: number };
export const NameTag: React.FC<NameTagProps> = ({ name, role, color = "pink", x = 200, y = 1340 }) => {
  const { frame, fps, enter, exit } = usePop(0, 12);
  const c = col(color);
  const slide = (1 - enter) * -500 - exit * 500;
  const roleIn = spring({ frame: frame - 8, fps, config: { damping: 14, stiffness: 150 } });
  const beat = 1 + Math.max(0, Math.sin((frame / fps) * 7)) * 0.12;
  return (
    <AbsoluteFill style={{ opacity: 1 - exit }}>
      <div style={{ position: "absolute", left: x, top: y, transform: `translateX(${slide}px)` }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 20, padding: "8px 34px", borderRadius: 999, background: C.ink, transform: `scale(${roleIn})`, transformOrigin: "left bottom" }}>
          <div style={{ transform: `scale(${beat})` }}><Icon name="heart" size={54} color={c} /></div>
          <span style={{ fontFamily: TEXT, fontWeight: 700, fontSize: 52, letterSpacing: 8, color: "#fff" }}>MEET THE BOSS</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 36, marginTop: 18, padding: "10px 80px 22px 50px", borderRadius: 60, background: c, boxShadow: C.shadow }}>
          <Icon name="paw" size={130} />
          <span style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 230, color: "#fff", lineHeight: 1.05 }}>{name}</span>
        </div>
        <div style={{ marginTop: 20, marginLeft: 20, fontFamily: TEXT, fontWeight: 600, fontSize: 66, color: "#fff", textShadow: "0 6px 20px rgba(0,0,0,0.6)", opacity: roleIn, transform: `translateY(${(1 - roleIn) * 30}px)` }}>
          {role}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- 4. "In the box" checklist ----------
export type ChecklistProps = { title: string; items: string[]; every?: number; side?: "left" | "right" };
export const Checklist: React.FC<ChecklistProps> = ({ title, items, every = 0.7, side = "right" }) => {
  const dir = side === "right" ? 1 : -1;
  const { frame, fps, enter, exit } = usePop(0, 12);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", [side]: 200, top: 300, width: 1180, transform: `translateX(${dir * ((1 - enter) * 1500 + exit * 1500)}px) rotate(${dir * 2}deg)`, background: C.cream, borderRadius: 70, padding: "60px 70px 70px", boxShadow: C.shadow, borderTop: `26px solid ${C.orange}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 28, marginBottom: 30 }}>
          <Icon name="box" size={100} color={C.orange} />
          <span style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 110, color: C.ink }}>{title}</span>
        </div>
        {items.map((it, i) => {
          const t0 = (0.5 + i * every) * fps;
          const s = spring({ frame: frame - t0, fps, config: { damping: 13, stiffness: 180 } });
          const tick = spring({ frame: frame - t0 - 6, fps, config: { damping: 9, stiffness: 220 } });
          return (
            <div key={it} style={{ display: "flex", alignItems: "center", gap: 36, padding: "20px 0", borderTop: i ? "4px dashed rgba(28,26,34,0.15)" : undefined, opacity: s, transform: `translateX(${(1 - s) * 80}px)` }}>
              <div style={{ width: 96, height: 96, borderRadius: 30, background: tick > 0.05 ? C.teal : "rgba(28,26,34,0.1)", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.6 + tick * 0.4})` }}>
                <div style={{ transform: `scale(${tick})` }}><Icon name="check" size={70} /></div>
              </div>
              <span style={{ fontFamily: TEXT, fontWeight: 700, fontSize: 80, color: C.ink }}>{it}</span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------- 5. Assembly progress HUD ----------
export type StepHudProps = { step: number; total: number; label: string };
export const StepHud: React.FC<StepHudProps> = ({ step, total, label }) => {
  const { frame, fps, enter, exit } = usePop(0, 12);
  const fill = interpolate(frame, [0.35 * fps, 1.1 * fps], [step - 1, step], { ...clamp, easing: Easing.out(Easing.cubic) });
  const pct = Math.round((fill / total) * 100);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 170, top: 150, transform: `translateY(${(1 - enter) * -400 - exit * 400}px)`, background: "rgba(28,26,34,0.82)", borderRadius: 56, padding: "40px 60px 50px", boxShadow: C.shadow, minWidth: 1300 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 60 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
            <Icon name="wrench" size={84} color={C.yellow} />
            <span style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 56, letterSpacing: 10, color: C.yellow }}>{`STEP ${step} / ${total}`}</span>
          </div>
          <span style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 90, color: "#fff" }}>{`${pct}%`}</span>
        </div>
        <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 120, color: "#fff", lineHeight: 1.1, margin: "8px 0 26px" }}>{label}</div>
        <div style={{ display: "flex", gap: 16 }}>
          {Array.from({ length: total }).map((_, i) => {
            const f = Math.max(0, Math.min(1, fill - i));
            return (
              <div key={i} style={{ flex: 1, height: 34, borderRadius: 17, background: "rgba(255,255,255,0.16)", overflow: "hidden" }}>
                <div style={{ width: `${f * 100}%`, height: "100%", background: `linear-gradient(90deg, ${C.orange}, ${C.yellow})`, borderRadius: 17 }} />
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- 6. Rubber stamp ----------
export type StampProps = { text: string; sub?: string; color?: string; x?: number; y?: number };
export const Stamp: React.FC<StampProps> = ({ text, sub, color = "pink", x = 2500, y = 520 }) => {
  const { frame, fps, exit } = usePop(0, 12);
  const c = col(color);
  const slam = interpolate(frame, [0, 0.22 * fps], [3.2, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const shake = frame > 0.22 * fps && frame < 0.5 * fps ? Math.sin(frame * 3) * 10 : 0;
  const op = interpolate(frame, [0, 0.12 * fps], [0, 1], clamp) * (1 - exit);
  return (
    <AbsoluteFill style={{ transform: `translate(${shake}px, ${shake * 0.6}px)` }}>
      <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%, -50%) rotate(-11deg) scale(${slam * (1 - exit * 0.3)})`, opacity: op, padding: "36px 80px 40px", border: `18px solid ${c}`, borderRadius: 50, outline: `6px solid ${c}`, outlineOffset: 16, background: "rgba(255,246,234,0.88)", textAlign: "center", boxShadow: C.shadow }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 30 }}>
          <Icon name="paw" size={120} color={c} />
          <span style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 150, color: c, letterSpacing: 6, lineHeight: 1, whiteSpace: "nowrap" }}>{text}</span>
        </div>
        {sub && <div style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 60, letterSpacing: 14, color: c, marginTop: 6 }}>{sub}</div>}
      </div>
    </AbsoluteFill>
  );
};

// ---------- 7. Big word punch (comic reaction) ----------
export type PunchProps = { text: string; color?: string; x?: number; y?: number; tilt?: number };
export const Punch: React.FC<PunchProps> = ({ text, color = "yellow", x = 1920, y = 700, tilt = -6 }) => {
  const { frame, fps, enter, exit } = usePop(0, 10);
  const c = col(color);
  const rays = interpolate(frame, [0, 0.5 * fps], [0.3, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%, -50%) rotate(${tilt}deg) scale(${enter * (1 - exit)})` }}>
        <svg width={1400} height={900} viewBox="-700 -450 1400 900" style={{ position: "absolute", left: -700, top: -450, opacity: 0.95 }}>
          {Array.from({ length: 14 }).map((_, i) => {
            const a = (i / 14) * Math.PI * 2 + frame * 0.01;
            return <line key={i} x1={Math.cos(a) * 330 * rays} y1={Math.sin(a) * 230 * rays} x2={Math.cos(a) * 560 * rays} y2={Math.sin(a) * 380 * rays} stroke={c} strokeWidth={26} strokeLinecap="round" />;
          })}
        </svg>
        <div style={{ position: "relative", fontFamily: DISPLAY, fontWeight: 800, fontSize: 260, color: "#fff", WebkitTextStroke: `18px ${C.ink}`, paintOrder: "stroke", textShadow: `12px 14px 0 ${c}`, whiteSpace: "nowrap", lineHeight: 1 }}>
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- 8. Chapter card (section plate in the show style) ----------
export type ChapterCardProps = { index: number; title: string; color?: string };
export const ChapterCard: React.FC<ChapterCardProps> = ({ index, title, color = "orange" }) => {
  const { frame, fps, enter, exit } = usePop(0, 12);
  const c = col(color);
  const num = spring({ frame: frame - 2, fps, config: { damping: 10, stiffness: 160 } });
  const bar = interpolate(frame, [0.15 * fps, 0.7 * fps], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const titleIn = spring({ frame: frame - 7, fps, config: { damping: 14, stiffness: 150 } });
  return (
    <AbsoluteFill style={{ opacity: 1 - exit }}>
      <div style={{ position: "absolute", left: 170, bottom: 400, display: "flex", alignItems: "center", gap: 46, transform: `translateX(${-exit * 300}px)` }}>
        <div style={{ width: 300, height: 300, borderRadius: 90, background: c, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${num}) rotate(${(1 - num) * -25 - 4}deg)`, boxShadow: C.shadow }}>
          <span style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 200, color: "#fff", lineHeight: 1, marginTop: 24 }}>{String(index).padStart(2, "0")}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, overflow: "hidden", padding: "0 30px 20px 0" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 20, opacity: titleIn }}>
            <Icon name="paw" size={56} color={c} />
            <span style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 56, letterSpacing: 12, color: "#fff", textShadow: "0 4px 16px rgba(0,0,0,0.6)" }}>CHAPTER</span>
          </div>
          <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 170, color: "#fff", lineHeight: 1.05, whiteSpace: "nowrap", textShadow: "0 10px 34px rgba(0,0,0,0.55)", transform: `translateY(${(1 - titleIn) * 160}px)` }}>{title}</div>
          <div style={{ height: 18, width: `${bar * 100}%`, borderRadius: 9, background: c }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
