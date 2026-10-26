"""lana-bunny (@lana-bunny, tag = folder name), 'монтаж вт': DIY spa day — oat/honey/coffee face mask + sugar body scrub.
C0001 = her whole English script on camera, full of retakes and Russian crew chatter: the intro and goodbye stay on
camera, the recipe lines (last clean take of each) play as voice-over over the silent process footage, plus a few
seconds of music-only process per section so the video passes 2:00. She never says "OnlyFans" -> second tag plate
on the goodbye. Left out: product-label close-ups C0143/C0144 (product placement), crew-talk / laughing stretches
(C0156 0-52, C0148 15-40, C0165 around 148-155 and 170+)."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import build  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\fosfe\Downloads") / "монтаж вт" / "lana-bunny"
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"


def write_sources():
    S = {"sources": {}, "dur": {}}
    for p in sorted(SRC.rglob("*.MP4")):
        S["sources"][p.stem] = str(p).replace("\\", "/")
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True)
        S["dur"][p.stem] = round(float(r.stdout), 3)
    (PROJ / "assets/analysis/sources.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")


CFG = {
    "tag": "@lana-bunny",
    "music": [str(LOFI / "HoliznaCC0 - Calm Currents(Lofi, Relax, Calm).mp3").replace("\\", "/"),
              str(LOFI / "HoliznaCC0 - Ocean Breeze(LoFi, Ukulele, Peaceful).mp3").replace("\\", "/")],
    "intro": ("C0001", 13.1, 24.4,
              "Hi everyone on OFTV! Today we're having a spa day without leaving home, "
              "and everything we need is already in the kitchen."),
    "scenes": [
        ("The Face Mask", "C0001", [(25.3, 38.55), (52.6, 59.1), (60.3, 68.4)],
         "Let's start with a face mask. Honey moisturizes and has antibacterial properties. "
         "Oats gently clean and calm the skin. And coffee works as a light natural scrub that boosts circulation. "
         "Mix everything into a smooth paste and apply to your face with circular motions.",
         [("C0148", 43, 63), ("C0149", 0, 12.4), ("C0146", 16, 52), ("C0147", 0, 23.4), ("C0150", 30, 48), ("C0150", 95, 110),
          ("C0151", 0, 49), ("C0154", 0, 26)], 8),
        ("Apply & Relax", "C0001", [(142.0, 150.45)],
         "Leave it on for 10 to 15 minutes while we prepare the second part of our spa ritual.",
         [("C0155", 0, 13), ("C0156", 52, 170)], 14),
        ("The Body Scrub", "C0001", [(212.9, 228.8), (231.1, 241.7)],
         "Now for the body scrub. Sugar and oil are a classic combo that works better than many store-bought "
         "products. Sugar gently exfoliates dead skin while oil moisturizes and leaves skin smooth. "
         "The ratio is simple: two parts sugar to one part oil. Apply to damp skin with gentle massage motions.",
         [("C0158", 22, 50), ("C0159", 25, 60), ("C0160", 0, 70), ("C0161", 0, 80)], 8),
        ("Rinse & Glow", "C0001", [(291.2, 304.4)],
         "The best part is that these ingredients are natural, chemical-free and cost-efficient compared to a salon. "
         "And the results are just good.",
         [("C0163", 0, 66), ("C0165", 24, 66), ("C0165", 81, 145)], 10),
    ],
    "outro": [
        ("C0001", 305.2, 315.8,
         "Look, my skin already feels soft and glowing, all in just 5 minutes with zero extra spending."),
        ("C0001", 318.5, 330.4,   # through her goodbye wave (329.0-330.5); crew 'stop' starts at 330.52
         "Thanks for watching! If you love simple beauty hacks like this, subscribe to my channel. "
         "See you in the next video!"),
    ],
    "onlyfans_at": 319.0,   # she never says OnlyFans -> repeat the tag on "Thanks for watching"
}

if __name__ == "__main__":
    write_sources()
    build(PROJ, CFG)
