import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Inter";
import { Cover } from "./Cover";
import { CoverTitle } from "./CoverTitle";
import { CoverSplit } from "./CoverSplit";
import { CoverDoodle } from "./CoverDoodle";
import { CoverDreamy } from "./CoverDreamy";
import { CoverShop } from "./CoverShop";
import { CoverVillain } from "./CoverVillain";
import { DaisyTag, DaisyTitle } from "./DaisyGraphics";
import { CoverDaisy } from "./CoverDaisy";
import { CoverDuo } from "./CoverDuo";
import { ChapterCard, Checklist, NameTag, PopSticker, Punch, ShowTitle, Stamp, StepHud } from "./ShowGraphics";
import { HwList, HwName, HwScene, HwSplit, HwStamp, HwStep, HwSticker, HwTitle } from "./HalloweenGraphics";

// Show graphics take their length from a `dur` prop (seconds).
const byDur = ({ props }: { props: Record<string, unknown> }) => ({
  durationInFrames: Math.round(((props.dur as number) || 3) * 30),
});
const SHOW: [string, React.FC<any>, Record<string, unknown>][] = [
  ["ShowTitle", ShowTitle, { eyebrow: "Episode", lines: ["Title", "Here"], dur: 4 }],
  ["PopSticker", PopSticker, { text: "Sticker", sub: "sub", icon: "box", x: 2400, y: 400, dur: 3 }],
  ["NameTag", NameTag, { name: "Name", role: "Role", dur: 3.5 }],
  ["Checklist", Checklist, { title: "In the box", items: ["One", "Two"], dur: 4 }],
  ["StepHud", StepHud, { step: 1, total: 4, label: "Step", dur: 3.5 }],
  ["Stamp", Stamp, { text: "APPROVED", dur: 2.5 }],
  ["Punch", Punch, { text: "WOW!", dur: 1.6 }],
  ["ChapterCard", ChapterCard, { index: 1, title: "Chapter", dur: 4 }],
  ["DaisyTag", DaisyTag, { tag: "@daisyyyli", dur: 4.5 }],
  ["DaisyTitle", DaisyTitle, { lines: ["Preparing", "Ingredients"], dur: 4 }],
  ["HwTitle", HwTitle, { eyebrow: "Eva x Lily", lines: ["Halloween", "Dinner"], sub: "a spooky collab", dur: 4.5 }],
  ["HwName", HwName, { name: "Eva", role: "raspberry pie", x: 200, y: 1500, dur: 3.5 }],
  ["HwList", HwList, { title: "Ingredients", items: ["250 g flour", "120 g butter"], dur: 6 }],
  ["HwStep", HwStep, { step: 1, total: 5, label: "Make the dough", x: 160, y: 160, dur: 3.5 }],
  ["HwSticker", HwSticker, { text: "Spooky face!", icon: "ghost", x: 2300, y: 400, dur: 2.6 }],
  ["HwStamp", HwStamp, { text: "READY!", x: 2800, y: 700, dur: 2.4 }],
  ["HwScene", HwScene, { index: 1, title: "The Ingredients", who: "Eva", dur: 3.6 }],
  ["HwSplit", HwSplit, { left: "Lily", right: "Eva", dur: 6 }],
];

// Transparent 4K overlays for the OFTV talking-head edit. Rendered as short
// VP9+alpha clips and composited onto the footage by FFmpeg.

const { fontFamily } = loadFont("normal", { weights: ["500", "600", "700"] });

const ACCENT = "#00AFF0";
const PLATE_BG = "rgba(14, 14, 18, 0.62)";
const PLATE_BORDER = "rgba(255, 255, 255, 0.14)";

// Enter / exit envelope shared by every plate so motion is consistent.
const useEnvelope = (inFrames: number, outFrames: number) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const enter = spring({
    frame,
    fps,
    config: { damping: 200, stiffness: 140, mass: 0.9 },
    durationInFrames: inFrames,
  });
  const exit = interpolate(
    frame,
    [durationInFrames - outFrames, durationInFrames - 1],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) },
  );
  return { enter, exit, frame, fps };
};

export type TagPlateProps = { tag: string };

export const TagPlate: React.FC<TagPlateProps> = ({ tag }) => {
  const { enter, exit, frame, fps } = useEnvelope(18, 14);
  const opacity = enter * (1 - exit);
  const x = (1 - enter) * 90 + exit * 60;
  // Accent line draws in slightly after the plate lands.
  const line = interpolate(frame, [0.25 * fps, 0.75 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top: 130,
          right: 160,
          opacity,
          transform: `translateX(${x}px)`,
          display: "flex",
          alignItems: "center",
          gap: 44,
          padding: "44px 82px 46px 58px",
          borderRadius: 999,
          background: PLATE_BG,
          border: `3px solid ${PLATE_BORDER}`,
          boxShadow: "0 18px 50px rgba(0,0,0,0.28)",
          fontFamily,
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 16,
            background: ACCENT,
            boxShadow: `0 0 24px ${ACCENT}`,
          }}
        />
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div
            style={{
              color: "rgba(255,255,255,0.72)",
              fontSize: 50,
              fontWeight: 500,
              letterSpacing: 8,
              textTransform: "uppercase",
            }}
          >
            Find me on OnlyFans
          </div>
          <div style={{ color: "#FFFFFF", fontSize: 100, fontWeight: 700, letterSpacing: 0.5 }}>
            {tag}
          </div>
          <div
            style={{
              height: 7,
              width: `${line * 100}%`,
              background: ACCENT,
              borderRadius: 3,
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};

export type SectionPlateProps = { index: number; title: string; label?: string };

export const SectionPlate: React.FC<SectionPlateProps> = ({ index, title, label = "Part" }) => {
  const { enter, exit, frame, fps } = useEnvelope(18, 14);
  const opacity = enter * (1 - exit);
  const x = -(1 - enter) * 90 - exit * 60;
  const bar = interpolate(frame, [0.1 * fps, 0.6 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 150,
          bottom: 480,
          opacity,
          transform: `translateX(${x}px)`,
          display: "flex",
          alignItems: "stretch",
          gap: 48,
          padding: "44px 88px 50px 48px",
          borderRadius: 40,
          background: PLATE_BG,
          border: `3px solid ${PLATE_BORDER}`,
          boxShadow: "0 18px 50px rgba(0,0,0,0.28)",
          fontFamily,
        }}
      >
        <div
          style={{
            width: 14,
            borderRadius: 5,
            background: ACCENT,
            transform: `scaleY(${bar})`,
            transformOrigin: "top",
          }}
        />
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div
            style={{
              color: ACCENT,
              fontSize: 50,
              fontWeight: 600,
              letterSpacing: 8,
              textTransform: "uppercase",
            }}
          >
            {`${label} ${String(index).padStart(2, "0")}`}
          </div>
          <div style={{ color: "#FFFFFF", fontSize: 108, fontWeight: 700 }}>{title}</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const OftvRoot: React.FC = () => (
  <>
    {SHOW.map(([id, comp, defaults]) => (
      <Composition key={id} id={id} component={comp} width={3840} height={2160} fps={30} durationInFrames={90}
        defaultProps={defaults} calculateMetadata={byDur} />
    ))}
    <Composition
      id="CoverDuo"
      component={CoverDuo}
      width={3840}
      height={2160}
      fps={30}
      durationInFrames={1}
      defaultProps={{ left: "oftv/vitya_lily.jpg", right: "oftv/vitya_eva.jpg", eyebrow: "Eva x Lily", lines: ["Halloween", "Dinner"],
        sub: "Raspberry pie & spooky mini pizzas", leftName: "Lily", rightName: "Eva" }}
    />
    <Composition
      id="CoverDaisy"
      component={CoverDaisy}
      width={3840}
      height={2160}
      fps={30}
      durationInFrames={1}
      defaultProps={{ variant: "split" as const, before: "oftv/daisy_before.jpg", after: "oftv/daisy_after.jpg" }}
    />
    <Composition
      id="CoverVillain"
      component={CoverVillain}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1}
      defaultProps={{ bg: "oftv/cover_src.jpg", cutout: "oftv/cover_src.jpg", kicker: "k", line1: "L1", line2: "L2", banner: "B" }}
    />
    <Composition
      id="CoverShop"
      component={CoverShop}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1}
      defaultProps={{ bg: "oftv/cover_src.jpg", cutout: "oftv/cover_src.jpg", kicker: "k", line1: "L1", line2: "L2", banner: "B" }}
    />
    <Composition
      id="CoverDreamy"
      component={CoverDreamy}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1}
      defaultProps={{ bg: "oftv/cover_src.jpg", cutout: "oftv/cover_src.jpg", kicker: "k", line1: "L1", line2: "L2", banner: "B" }}
    />
    <Composition
      id="CoverDoodle"
      component={CoverDoodle}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1}
      defaultProps={{ src: "oftv/cover_src.jpg", kicker: "kicker", line1: "LINE ONE", line2: "LINE TWO", banner: "BANNER" }}
    />
    <Composition
      id="CoverSplit"
      component={CoverSplit}
      width={3840}
      height={2160}
      fps={30}
      durationInFrames={1}
      defaultProps={{ src: "oftv/cover_src.jpg", eyebrow: "EYEBROW", headline: "HEADLINE", script: "script", sub: "Subline" }}
    />
    <Composition
      id="CoverTitle"
      component={CoverTitle}
      width={3840}
      height={2160}
      fps={30}
      durationInFrames={1}
      defaultProps={{ src: "oftv/cover_src.jpg", eyebrow: "EYEBROW", headline: "HEADLINE", script: "script", sub: "Subline" }}
    />
    <Composition
      id="Cover"
      component={Cover}
      width={3840}
      height={2160}
      fps={30}
      durationInFrames={1}
      defaultProps={{ variant: "a" as const }}
    />
    <Composition
      id="TagPlate"
      component={TagPlate}
      width={3840}
      height={2160}
      fps={30}
      durationInFrames={165}
      defaultProps={{ tag: "@username" }}
    />
    <Composition
      id="SectionPlate"
      component={SectionPlate}
      width={3840}
      height={2160}
      fps={30}
      durationInFrames={144}
      defaultProps={{ index: 1, title: "Section Title" }}
    />
  </>
);



