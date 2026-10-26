"""lia_life (@lia_life), 'монтаж вт': pink-from-head-to-toe challenge. Intro IMG_9938, makeup + outfit b-roll
(9939-9949, all silent) under five voice notes 'Jarvis St*', final look IMG_9954 + goodbye IMG_9955 on camera.
English speech. See plan_common.py (long b-roll shots are split into several evenly spaced pieces)."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import build  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\fosfe\Downloads") / "монтаж вт" / "lia_life"
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"


def write_sources():
    S = {"sources": {}, "dur": {}}
    for p in sorted(SRC.iterdir()):
        if p.suffix.lower() in (".mov", ".m4a"):
            S["sources"][p.stem] = str(p).replace("\\", "/")
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                               capture_output=True, text=True)
            S["dur"][p.stem] = round(float(r.stdout), 3)
    (PROJ / "assets/analysis/sources.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")


CFG = {
    "tag": "@lia_life",
    "music": [str(LOFI / "HoliznaCC0 - Bubbles(Lofi, Bright, Relaxed).mp3").replace("\\", "/"),
              str(LOFI / "HoliznaCC0 - Projector Screen(LoFi, Happy).mp3").replace("\\", "/")],
    "intro": ("IMG_9938", 0.0, 30.2,
              "Hi everyone! I'm Lia, an OnlyFans model and OFTV creator. Welcome back to my little beauty corner. "
              "And today I'm taking on a little fun challenge. I'm going to create the whole look using just one "
              "color: pink. Everything's gonna be pink. My makeup, my outfit, even accessories. "
              "So let's see where it takes us."),
    "scenes": [
        ("Fresh Base", "Jarvis St", [(2.68, 15.49)],
         "First, I'm preparing my skin. I want everything to look fresh, smooth and glowy. "
         "Pink is going to be the star of this look, so I'm keeping my base soft and natural.",
         [("IMG_9939", 0, 51.9)]),
        ("Pink Eyes", "Jarvis St 2", [(2.48, 18.17)],
         "Now for the eyes. I'm going with soft pink shades and a little extra shimmer. "
         "I love how pink can look sweet, playful and glamorous all at once. "
         "A little mascara and we're getting somewhere.",
         [("IMG_9941", 0, 34.0), ("IMG_9942", 0, 35.3), ("IMG_9943", 0, 24.7)]),
        ("Blush & Gloss", "Jarvis St 3", [(1.46, 15.05)],
         "Of course, we need some pink blush. I'm adding a rosy glow to my cheeks and finishing with a glossy "
         "pink lip. I want this makeup to feel fresh, feminine and just a little flirty.",
         [("IMG_9944", 0, 46.6), ("IMG_9945", 0, 46.4)]),
        ("The Pink Outfit", "Jarvis St 4", [(1.84, 17.27)],
         "Makeup is done, so it's time for the outfit. I'm choosing pink from head to toe. "
         "I want the pieces to complement each other without making the look feel too busy. "
         "Same color, different textures, that's the secret.",
         [("IMG_9946", 0, 18.4), ("IMG_9947", 0, 48.5)]),
        ("Finishing Touches", "Jarvis St 5", [(1.52, 17.15)],
         "And now the finishing touches. A matching bag, pink shoes to tie everything together. "
         "I love how the little details make the whole outfit feel intentional. "
         "Pink from head to toe, challenge accepted.",
         [("IMG_9948", 0, 35.0), ("IMG_9949", 0, 17.5)]),
    ],
    "outro": [
        ("IMG_9954", 0.0, 11.6,
         "And here's the final pink look. I went from the fresh makeup base to glossy lips, "
         "rosy eyes and a complete pink outfit."),
        ("IMG_9955", 0.0, 21.1,
         "I think we proved that only one color can create the whole look. Thank you so much for spending these "
         "few minutes with me. I'm Lia, your OnlyFans model and OFTV creator, and if you'd like to see more of my "
         "exclusive content, you can subscribe to my OnlyFans. Thank you so much, I'll see you, bye!"),
    ],
    "onlyfans_at": 16.58,
}

if __name__ == "__main__":
    write_sources()
    build(PROJ, CFG)
