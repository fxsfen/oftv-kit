import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont as loadCreepster } from "@remotion/google-fonts/Creepster";
import { loadFont as loadBaloo } from "@remotion/google-fonts/Baloo2";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

// Halloween pop-ups for the Eva & Lily collab (vitya-oftv-1). Transparent 4K plates (VP9+alpha), composited
// by FFmpeg. Every element takes its position from props: the planner puts it on the side of the frame
// that is free of faces (mediapipe face boxes per shot), so a pop-up never covers a face.

const { fontFamily: SPOOK } = loadCreepster("normal", { weights: ["400"], subsets: ["latin"] });
const { fontFamily: ROUND } = loadBaloo("normal", { weights: ["700", "800"], subsets: ["latin"] });
const { fontFamily: TEXT } = loadInter("normal", { weights: ["600", "700", "800"], subsets: ["latin"] });

export const H = {
  night: "rgba(18, 10, 26, 0.86)",
  ink: "#120A1A",
  orange: "#FF7A1A",
  pumpkin: "#FF9F1C",
  purple: "#A259FF",
  slime: "#B6FF3B",
  blood: "#FF3B5C",
  bone: "#FFF4E2",
  glow: "0 0 60px rgba(255,122,26,0.55), 0 30px 80px rgba(0,0,0,0.55)",
};
const PAL: Record<string, string> = { orange: H.orange, purple: H.purple, slime: H.slime, blood: H.blood, pumpkin: H.pumpkin };
const col = (c?: string) => (c && PAL[c]) || c || H.orange;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const usePop = (delay = 0, outFrames = 10) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 10, stiffness: 160, mass: 0.8 } });
  const exit = interpolate(frame, [durationInFrames - outFrames, durationInFrames - 1], [0, 1], {
    ...clamp,
    easing: Easing.in(Easing.back(1.7)),
  });
  return { frame, fps, enter, exit, durationInFrames };
};

// ---------- icons ----------
export const HIcon: React.FC<{ name: string; size: number; color?: string }> = ({ name, size, color = H.ink }) => {
  let b: React.ReactNode;
  switch (name) {
    case "pumpkin":
      b = (<>
        <path fill={H.orange} d="M12 6c-2.2-1.6-6.4-1.4-8 1.6C2.4 10.8 3 16 5.4 18.4c2 2 4.4 2 6.6 1.2 2.2.8 4.6.8 6.6-1.2C21 16 21.6 10.8 20 7.6 18.4 4.6 14.2 4.4 12 6z" />
        <path fill="#5B8C2A" d="M11.2 6.4c.2-1.6.9-3 2.4-3.9l.8 1c-1 .7-1.5 1.6-1.6 2.9z" />
        <path fill={H.ink} d="M7.4 10.6l2.2 1.2-2.4 1zM16.6 10.6l-2.2 1.2 2.4 1zM7.6 15c1.4 1.4 3 1.9 4.4 1.9s3-.5 4.4-1.9l-1.2.2-.8.9-.8-.9-1.6.4-1.6-.4-.8.9-.8-.9z" />
      </>);
      break;
    case "spider":
      b = (<>
        <g stroke={color} strokeWidth={1.6} strokeLinecap="round" fill="none">
          <path d="M9 11L4 8M9 12.5L3.5 12.5M9 14L4 17M15 11l5-3M15 12.5h5.5M15 14l5 3M9.5 15.5L6 20M14.5 15.5L18 20" />
          <path d="M12 2v6" />
        </g>
        <ellipse fill={color} cx="12" cy="13" rx="3.6" ry="4.2" /><circle fill={color} cx="12" cy="8.6" r="2.2" />
        <circle fill={H.blood} cx="11.2" cy="8.4" r=".6" /><circle fill={H.blood} cx="12.8" cy="8.4" r=".6" />
      </>);
      break;
    case "ghost":
      b = (<>
        <path fill={H.bone} d="M12 3c-4 0-6.6 3-6.6 7v10l2.2-1.6 2.2 1.6 2.2-1.6 2.2 1.6 2.2-1.6 2.2 1.6V10c0-4-2.6-7-6.6-7z" />
        <circle fill={H.ink} cx="9.6" cy="10" r="1.2" /><circle fill={H.ink} cx="14.4" cy="10" r="1.2" /><ellipse fill={H.ink} cx="12" cy="13.6" rx="1.1" ry="1.5" />
      </>);
      break;
    case "bat":
      b = <path fill={color} d="M12 9.5c.6-1 1.4-1.6 1.4-1.6l.2 1.2c2-1.4 5.4-2 8.4-.8-1.4.6-2 1.6-2 2.8-1.4-.6-2.6 0-3 1.2-1-.8-2.4-.4-2.8.8L12 15l-2.2-1.9c-.4-1.2-1.8-1.6-2.8-.8-.4-1.2-1.6-1.8-3-1.2 0-1.2-.6-2.2-2-2.8 3-1.2 6.4-.6 8.4.8l.2-1.2s.8.6 1.4 1.6z" />;
      break;
    case "berry":
      b = (<>
        <circle fill={H.blood} cx="9" cy="14" r="3.4" /><circle fill={H.blood} cx="15" cy="14" r="3.4" /><circle fill={H.blood} cx="12" cy="10" r="3.4" />
        <circle fill="rgba(255,255,255,0.5)" cx="8" cy="13" r=".7" /><circle fill="rgba(255,255,255,0.5)" cx="11" cy="9" r=".7" />
        <path fill="#5B8C2A" d="M12 6.6c-1.6-1.4-3.4-1.2-4.4-.4 1.4.4 2.6.2 4.4.4zm0 0c1.6-1.4 3.4-1.2 4.4-.4-1.4.4-2.6.2-4.4.4z" />
      </>);
      break;
    case "pizza":
      b = (<>
        <path fill="#F6C453" d="M12 21L3 5.5c5.6-3 12.4-3 18 0z" /><path fill="#E0803B" d="M3 5.5c5.6-3 12.4-3 18 0l-1 1.8c-5-2.6-11-2.6-16 0z" />
        <circle fill={H.blood} cx="10" cy="9" r="1.5" /><circle fill={H.blood} cx="14.4" cy="11" r="1.4" /><circle fill={H.ink} cx="12" cy="14.6" r="1.1" />
      </>);
      break;
    case "oven":
      b = (<>
        <rect fill={color} x="3" y="4" width="18" height="16" rx="2.5" /><rect fill={H.orange} x="5.5" y="9" width="13" height="8.5" rx="1.4" />
        <circle fill={H.bone} cx="7" cy="6.4" r=".9" /><circle fill={H.bone} cx="10" cy="6.4" r=".9" /><path fill="#FFD27A" d="M8 14.6c1-1.6 2-1 2-2.4.9.9.6 1.6 1.4 2.2.4-.8 1-.9 1-1.8 1 1 1.6 2 .6 2.8z" />
      </>);
      break;
    case "star":
      b = <path fill={color} d="M12 2.5l2.6 6 6.4.6-4.8 4.3 1.5 6.3L12 16.4l-5.7 3.3 1.5-6.3L3 9.1l6.4-.6z" />;
      break;
    case "knife":
      b = (<><path fill={H.bone} d="M4 18L17 5c1.4.4 2.2 1.4 2.4 2.8L8.6 18.6z" /><rect fill={color} x="2.2" y="17.2" width="6" height="3" rx="1.2" transform="rotate(-45 5.2 18.7)" /></>);
      break;
    default: // sparkle
      b = <path fill={color} d="M12 2l1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8zM19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z" />;
  }
  return <svg width={size} height={size} viewBox="0 0 24 24">{b}</svg>;
};

// ---------- opening title ----------
export type HwTitleProps = { eyebrow: string; lines: string[]; sub?: string; side?: "left" | "right"; top?: number };
export const HwTitle: React.FC<HwTitleProps> = ({ eyebrow, lines, sub, side = "left", top = 520 }) => {
  const { frame, fps, enter, exit } = usePop(0, 14);
  const flicker = 0.85 + 0.15 * Math.sin(frame * 0.9) * Math.sin(frame * 0.37);
  return (
    <AbsoluteFill style={{ opacity: 1 - exit }}>
      <div style={{ position: "absolute", [side]: 220, top, textAlign: side, transform: `translateY(${exit * 80}px)` }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 24, padding: "16px 46px 16px 22px", borderRadius: 999,
          background: H.purple, transform: `scale(${enter})`, transformOrigin: `${side} center`, boxShadow: H.glow }}>
          <HIcon name="bat" size={92} color={H.ink} />
          <span style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 60, color: "#fff", letterSpacing: 12 }}>{eyebrow.toUpperCase()}</span>
        </div>
        {lines.map((ln, li) => {
          const s = spring({ frame: frame - 6 - li * 7, fps, config: { damping: 9, stiffness: 120 } });
          return (
            <div key={li} style={{ fontFamily: SPOOK, fontSize: 270, lineHeight: 0.98, marginTop: li ? -10 : 24,
              color: li === lines.length - 1 ? H.orange : H.bone, opacity: Math.min(1, s * 1.3) * (li === lines.length - 1 ? flicker : 1),
              transform: `translateY(${(1 - s) * 180}px) scale(${0.8 + 0.2 * s})`, transformOrigin: `${side} bottom`,
              textShadow: li === lines.length - 1 ? "0 0 50px rgba(255,122,26,0.8), 0 16px 40px rgba(0,0,0,0.7)" : "0 16px 40px rgba(0,0,0,0.7)" }}>
              {ln}
            </div>
          );
        })}
        {sub && (
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 92, color: H.slime, marginTop: 16,
            opacity: interpolate(frame, [0.9 * fps, 1.3 * fps], [0, 1], clamp), textShadow: "0 8px 26px rgba(0,0,0,0.7)" }}>{sub}</div>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ---------- name tag ----------
export type HwNameProps = { name: string; role: string; icon?: string; color?: string; x: number; y: number; anchor?: "left" | "right" };
export const HwName: React.FC<HwNameProps> = ({ name, role, icon = "pumpkin", color = "orange", x, y, anchor = "left" }) => {
  const { frame, fps, enter, exit } = usePop(0, 12);
  const c = col(color);
  const roleIn = spring({ frame: frame - 8, fps, config: { damping: 14 } });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", [anchor]: anchor === "left" ? x : 3840 - x, top: y, textAlign: anchor,
        transform: `translateX(${(anchor === "left" ? -1 : 1) * ((1 - enter) * 900 + exit * 1200)}px)` }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 34, padding: "26px 60px 26px 30px", borderRadius: 60,
          background: H.night, border: `8px solid ${c}`, boxShadow: H.glow }}>
          <div style={{ transform: `rotate(${(1 - enter) * -90}deg) scale(${enter})` }}><HIcon name={icon} size={190} color={c} /></div>
          <div>
            <div style={{ fontFamily: SPOOK, fontSize: 210, color: H.bone, lineHeight: 0.95 }}>{name}</div>
            <div style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 58, letterSpacing: 9, color: c, opacity: roleIn,
              transform: `translateY(${(1 - roleIn) * 30}px)` }}>{role.toUpperCase()}</div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- ingredient list ----------
export type HwListProps = { title: string; items: string[]; icon?: string; color?: string; side?: "left" | "right"; top?: number; every?: number };
export const HwList: React.FC<HwListProps> = ({ title, items, icon = "berry", color = "orange", side = "left", top = 260, every = 0.55 }) => {
  const { frame, fps, enter, exit } = usePop(0, 12);
  const c = col(color);
  const dir = side === "left" ? -1 : 1;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", [side]: 180, top, width: 1220, borderRadius: 70, padding: "54px 64px 60px",
        background: H.night, border: `6px solid ${c}`, boxShadow: H.glow,
        transform: `translateX(${dir * ((1 - enter) * 1500 + exit * 1500)}px) rotate(${dir * 1.5}deg)` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 26, marginBottom: 26 }}>
          <HIcon name={icon} size={120} color={c} />
          <span style={{ fontFamily: SPOOK, fontSize: 132, color: c, lineHeight: 1 }}>{title}</span>
        </div>
        {items.map((it, i) => {
          const s = spring({ frame: frame - 10 - i * every * fps, fps, config: { damping: 12, stiffness: 170 } });
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 30, margin: "16px 0", opacity: Math.min(1, s * 1.5),
              transform: `translateX(${dir * (1 - s) * 220}px)` }}>
              <div style={{ width: 30, height: 30, borderRadius: 15, background: c, boxShadow: `0 0 24px ${c}`, transform: `scale(${s})` }} />
              <span style={{ fontFamily: ROUND, fontWeight: 700, fontSize: 82, color: H.bone, whiteSpace: "nowrap" }}>{it}</span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------- step chip ----------
export type HwStepProps = { step: number; total: number; label: string; who?: string; color?: string; x: number; y: number; anchor?: "left" | "right" };
export const HwStep: React.FC<HwStepProps> = ({ step, total, label, who, color = "orange", x, y, anchor = "left" }) => {
  const { frame, fps, enter, exit } = usePop(0, 10);
  const c = col(color);
  const fill = interpolate(frame, [6, 6 + 0.6 * fps], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", [anchor]: anchor === "left" ? x : 3840 - x, top: y,
        transform: `translateY(${(1 - enter) * -260 - exit * 260}px)`, opacity: 1 - exit }}>
        <div style={{ display: "flex", alignItems: "center", gap: 36, padding: "30px 58px 30px 30px", borderRadius: 64,
          background: H.night, border: `5px solid rgba(255,255,255,0.12)`, boxShadow: H.glow, minWidth: 1100 }}>
          <div style={{ width: 200, height: 200, borderRadius: 56, background: c, display: "flex", alignItems: "center", justifyContent: "center",
            transform: `scale(${enter}) rotate(${(1 - enter) * 30 - 4}deg)` }}>
            <span style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 150, color: H.ink, lineHeight: 1, marginTop: 18 }}>{step}</span>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 50, letterSpacing: 10, color: c }}>
              {`${who ? who.toUpperCase() + " · " : ""}STEP ${step} OF ${total}`}
            </div>
            <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 116, color: H.bone, lineHeight: 1.08, whiteSpace: "nowrap" }}>{label}</div>
            <div style={{ display: "flex", gap: 14, marginTop: 16 }}>
              {Array.from({ length: total }).map((_, i) => (
                <div key={i} style={{ flex: 1, height: 22, borderRadius: 11, background: "rgba(255,255,255,0.14)", overflow: "hidden" }}>
                  <div style={{ height: "100%", borderRadius: 11, background: c,
                    width: `${(i < step - 1 ? 1 : i === step - 1 ? fill : 0) * 100}%` }} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- sticker ----------
export type HwStickerProps = { text: string; sub?: string; icon?: string; color?: string; x: number; y: number; tilt?: number; anchor?: "left" | "right" };
export const HwSticker: React.FC<HwStickerProps> = ({ text, sub, icon = "spark", color = "purple", x, y, tilt = -4, anchor = "left" }) => {
  const { frame, enter, exit } = usePop(0, 9);
  const c = col(color);
  const wob = Math.sin(frame / 7) * 1.8;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", [anchor]: anchor === "left" ? x : 3840 - x, top: y,
        transform: `rotate(${tilt + wob}deg) scale(${enter * (1 - exit)})`, transformOrigin: `${anchor} center`,
        display: "flex", alignItems: "center", gap: 30, flexDirection: anchor === "left" ? "row" : "row-reverse",
        padding: "26px 56px 26px 26px", borderRadius: 999, background: H.bone, boxShadow: `0 0 0 10px ${c}, ${H.glow}` }}>
        <div style={{ width: 170, height: 170, borderRadius: 85, background: H.ink, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <HIcon name={icon} size={128} color={c} />
        </div>
        <div style={{ textAlign: anchor }}>
          <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 104, color: H.ink, lineHeight: 1.0, whiteSpace: "nowrap" }}>{text}</div>
          {sub && <div style={{ fontFamily: TEXT, fontWeight: 700, fontSize: 52, color: "rgba(18,10,26,0.6)", whiteSpace: "nowrap" }}>{sub}</div>}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- stamp ----------
export type HwStampProps = { text: string; sub?: string; color?: string; x: number; y: number };
export const HwStamp: React.FC<HwStampProps> = ({ text, sub, color = "slime", x, y }) => {
  const { frame, enter, exit } = usePop(0, 10);
  const c = col(color);
  const slam = interpolate(enter, [0, 1], [2.6, 1]);
  const shake = frame < 9 ? Math.sin(frame * 2.5) * (9 - frame) * 2.2 : 0;
  return (
    <AbsoluteFill style={{ transform: `translate(${shake}px, ${shake * 0.6}px)` }}>
      <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%, -50%) rotate(-9deg) scale(${slam * (1 - exit * 0.4)})`,
        opacity: Math.min(1, enter * 2) * (1 - exit), padding: "30px 80px 36px", border: `16px solid ${c}`, borderRadius: 46,
        background: "rgba(18,10,26,0.82)", textAlign: "center", boxShadow: `0 0 70px ${c}` }}>
        <div style={{ fontFamily: SPOOK, fontSize: 200, color: c, letterSpacing: 6, lineHeight: 1, whiteSpace: "nowrap" }}>{text}</div>
        {sub && <div style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 56, letterSpacing: 12, color: H.bone, marginTop: 4 }}>{sub}</div>}
      </div>
    </AbsoluteFill>
  );
};

// ---------- scene card ----------
export type HwSceneProps = { index: number; title: string; who: string; color?: string; side?: "left" | "right"; bottom?: number };
export const HwScene: React.FC<HwSceneProps> = ({ index, title, who, color = "orange", side = "left", bottom = 300 }) => {
  const { frame, fps, enter, exit } = usePop(0, 12);
  const c = col(color);
  const titleIn = spring({ frame: frame - 5, fps, config: { damping: 13 } });
  const bar = interpolate(frame, [8, 8 + 0.7 * fps], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", [side]: 190, bottom, display: "flex", alignItems: "center", gap: 44,
        flexDirection: side === "left" ? "row" : "row-reverse", transform: `translateX(${(side === "left" ? -1 : 1) * exit * 400}px)`, opacity: 1 - exit }}>
        <div style={{ width: 290, height: 290, borderRadius: 145, background: c, display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: H.glow, transform: `scale(${enter}) rotate(${(1 - enter) * -40}deg)` }}>
          <span style={{ fontFamily: SPOOK, fontSize: 210, color: H.ink, lineHeight: 1, marginTop: 20 }}>{String(index).padStart(2, "0")}</span>
        </div>
        <div style={{ textAlign: side }}>
          <div style={{ fontFamily: TEXT, fontWeight: 800, fontSize: 56, letterSpacing: 14, color: c, textShadow: "0 4px 18px rgba(0,0,0,0.8)" }}>{who.toUpperCase()}</div>
          <div style={{ fontFamily: SPOOK, fontSize: 196, color: H.bone, lineHeight: 1.0, whiteSpace: "nowrap",
            textShadow: "0 10px 34px rgba(0,0,0,0.8)", transform: `translateY(${(1 - titleIn) * 150}px)`, opacity: titleIn }}>{title}</div>
          <div style={{ height: 16, width: `${bar * 100}%`, borderRadius: 8, background: c, marginTop: 10, marginLeft: side === "right" ? "auto" : 0 }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- split-screen labels (final shot) ----------
export type HwSplitProps = { left: string; right: string };
export const HwSplit: React.FC<HwSplitProps> = ({ left, right }) => {
  const { frame, fps, enter, exit } = usePop(0, 12);
  const lab = (t: string, side: "left" | "right", c: string, d: number) => {
    const s = spring({ frame: frame - d, fps, config: { damping: 11 } });
    return (
      <div style={{ position: "absolute", [side]: 120, bottom: 120, padding: "18px 56px", borderRadius: 999, background: c,
        transform: `translateY(${(1 - s) * 300 + exit * 300}px)`, fontFamily: SPOOK, fontSize: 130, color: H.ink, boxShadow: H.glow }}>{t}</div>
    );
  };
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 1916, top: 0, width: 8, height: 2160, background: H.orange,
        transform: `scaleY(${enter * (1 - exit)})`, boxShadow: `0 0 40px ${H.orange}` }} />
      {lab(left, "left", H.purple, 4)}
      {lab(right, "right", H.orange, 10)}
    </AbsoluteFill>
  );
};
