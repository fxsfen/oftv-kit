"""lia-life-1026 (@lia_life): Queen of Hearts makeup inspired by a playing card. Downloads/монтаж пнд/lia_life.
IMG_0114 = on-camera hello (holds the card), IMG_0133 + IMG_0135 = final look + goodbye (says OnlyFans).
IMG_0153..0166 are her voice notes recorded as (black, portrait) videos -> VO over the silent makeup b-roll
IMG_0116..0129 (no speech by VAD, mouths closed on the face-crop sheets)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import build  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"
TR = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))


def span(key):
    ws = TR[key]
    return [(round(ws[0]["start"], 2), round(ws[-1]["end"], 2))]


CFG = {
    "tag": "@lia_life",
    "music": [str(LOFI / "HoliznaCC0 - Orbs In A Photo(LoFi, Chill).mp3").replace("\\", "/"),
              str(LOFI / "HoliznaCC0 - Saturation(Lofi, Calm, Relaxed).mp3").replace("\\", "/")],
    "intro": ("IMG_0114", 0.28, 15.72,
              "Hey everyone! It's Lia, your OnlyFans model and OFTV creator. And today I'm going to do my makeup "
              "inspired by the Queen of Hearts. Let's see if I can turn this little playing card into a gorgeous, "
              "beautiful look."),
    "scenes": [
        ("Fresh Base", "IMG_0153", span("IMG_0153"),
         "First, I'm creating a smooth, fresh base. Since the Queen of Hearts is all about bold colors and a little "
         "drama, I want my skin to look soft and luminous. That way, the red shades will really stand out.",
         [("IMG_0116", 2, 48)], 3),
        ("Rosy Eyes", "IMG_0155", span("IMG_0155"),
         "Now for the eyes. I'm starting with a soft pink, then adding rich red and burgundy shades for a little "
         "Queen of Hearts drama. I want the colors to blend beautifully, like the shades on a playing card. "
         "And a touch of shimmer makes everything feel a little more magical.",
         [("IMG_0118", 8, 56), ("IMG_0119", 0, 24)], 3),
        ("Liner & Lashes", "IMG_0157", span("IMG_0157"),
         "To make the eyes pop, I'm adding a little eyeliner and mascara.",
         [("IMG_0120", 5, 110), ("IMG_0121", 5, 110), ("IMG_0124", 1, 20)], 9),
        ("Cherry Red Lips", "IMG_0161", span("IMG_0161"),
         "I want this look to feel bold, but still pretty and feminine. And now, the most iconic part of this "
         "look: the lips. I'm choosing a rich cherry red to match the heart symbol on my card.",
         [("IMG_0127", 8, 60)], 3),
        ("A Little Heart", "IMG_0164", span("IMG_0164"),
         "I also decided to draw a small heart on my cheek, and suddenly the whole look feels much more "
         "like the Queen of Hearts.",
         [("IMG_0128", 0, 22)], 3),
        ("Finishing Touches", "IMG_0166", span("IMG_0166"),
         "Time for the finishing touches, and here is my inspiration: the Queen of Hearts. I love how a single "
         "playing card can inspire an entire look, from the eyes to the lips.",
         [("IMG_0129", 0, 39), ("IMG_0126", 0, 9.4)], 4),
    ],
    "outro": [("IMG_0133", 0.0, 12.16,
               "And here's my final Queen of Hearts makeup look. We used rosy tones, dramatic reds and cherry "
               "red lips to bring the playing card to life."),
              ("IMG_0135", 0.0, 14.4,   # keeps the "bye" and her wave after it
               "I'm Lia, an OnlyFans model and OFTV creator, and if you'd like to see more of my exclusive moments, "
               "you can find me on my OnlyFans. Thank you for watching this video. I'll see you soon. Bye!")],
    "onlyfans_at": 9.04,
}

if __name__ == "__main__":
    build(PROJ, CFG)
