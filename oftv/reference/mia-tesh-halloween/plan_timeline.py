"""mia-tesh-halloween (@mia_tesh), 'домонтаж': Halloween makeup tutorial — glam base + red lips + a spiderweb under the eye.
IMG_6754 = on-camera hello, IMG_6761 = on-camera goodbye (says OnlyFans). The middle is 13 min of silent makeup
(IMG_6757 skin -> brows/eyes, IMG_6758 mascara -> lips -> eyeliner -> spiderweb) + close-ups filmed after the web
(IMG_6759 posing, IMG_6762 brush/highlighter). Her six voice notes (vo1..vo6, recorded from our script) play over it.
Order follows the footage: the close-ups already show the web, so 'Glow' (vo3) comes after 'The Spooky Part'.
vo6 starts after she read the stage direction aloud ('Final look over the close-up shots before your goodbye')."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import build  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"
TR = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))


def span(key, after=None):
    """Whole voice note, first to last word; `after` = start at the first word after this one."""
    ws = TR[key]
    if after:
        k = max(i for i, w in enumerate(ws) if w["word"].strip(" ,.").lower() == after)
        ws = ws[k + 1:]
    return [(round(ws[0]["start"], 2), round(ws[-1]["end"], 2))]


V7, V8 = "IMG_6757-001", "IMG_6758-002"
CFG = {
    "tag": "@mia_tesh",
    "music": [str(LOFI / "HoliznaCC0 - Lucid(Lofi, Dreamy, Chill).mp3").replace("\\", "/"),
              str(LOFI / "HoliznaCC0 - Moon Unit(Lofi, Reflection, Dreamy).mp3").replace("\\", "/")],
    "intro": None,   # filled in main() from the word timestamps
    "scenes": [
        ("Skin Prep", "vo1", span("vo1"),
         "Okay, let's start with the skin. I always prep first, so the makeup stays smooth all night. "
         "I warm the product between my fingers and gently tap it in the skin. "
         "Next, a light base. Even for Halloween, I want my skin to look fresh and natural. "
         "Then a little powder, just in the center of my face, so nothing gets shiny. "
         "Now some contour and bronzer, under the cheekbones and along the jawline. Blend, blend, blend!",
         [(V7, 3, 58), (V7, 62, 98), (V7, 102, 148), (V7, 152, 200)], 3),
        ("Brows & Eyes", "vo2", span("vo2"),
         "Brows next. I brush them up and fill in the gaps with small, light strokes. "
         "For the eyes, I start with a soft warm shadow all over the lid. "
         "Then I make the outer corner a bit darker, to give the look more depth. "
         "Now eyeliner, a small wing. Take your time here, it's the trickiest part! "
         "And of course, mascara. Lots of mascara.",
         [(V7, 205, 245), (V7, 248, 298), (V7, 300, 338), (V7, 342, 388), (V8, 30, 56)], 3),
        ("Red Lips", "vo4", span("vo4"),
         "Now my favorite part: red lips! First, I outline my lips with a liner, so the lipstick stays sharp. "
         "Then I fill everything with a classic bold red. This red is pure old Hollywood.",
         [(V8, 60, 98), (V8, 100, 184)], 3),
        ("The Spooky Part", "vo5", span("vo5"),
         "And now, the Halloween part. With a black liner, I draw dark tears running down from my eye. "
         "Go slowly, and make the lines uneven. It looks creepier that way. "
         "Pretty on one side, and a little bit scary on the other. That's exactly the vibe I wanted.",
         [(V8, 331, 384)], 3),
        ("Glow", "vo3", span("vo3"),
         "A little blush on the apples of my cheeks, for a healthy glow, "
         "and highlighter on the top of the cheekbones. I love when it catches the light.",
         [("IMG_6762", 1, 58)], 4),
        ("The Final Look", "vo6", span("vo6", after="goodbye"),
         "And here's a full look. Glam! Red lips, with a spooky twist.",
         [(V8, 386, 400.4), ("IMG_6759", 1, 38)], 6),
    ],
    "outro": None,
    "onlyfans_at": None,
}


def talk_span(key):
    ws = TR[key]
    return ws[0]["start"], ws[-1]["end"]


if __name__ == "__main__":
    a, b = talk_span("IMG_6754")
    CFG["intro"] = ("IMG_6754", a, b,
                    "Hello everyone, and welcome to my Halloween makeup special! My name is Mia, and today "
                    "I'm going to show you how I create my makeup look, step by step. So get comfortable, "
                    "grab your makeup, and let's create something spooky together!")
    a, b = talk_span("IMG_6761")
    CFG["outro"] = ("IMG_6761", a, min(b + 2.5, 18.1),   # keep her wave after "see you soon"
                    "And that's the final look! I hope you enjoyed my Halloween makeup tutorial. "
                    "And of course, if you'd like to see more exclusive content, you can always find me "
                    "on my OnlyFans page. So take care, guys, and see you soon!")
    CFG["onlyfans_at"] = next(w["start"] for w in TR["IMG_6761"] if "only" in w["word"].lower())
    build(PROJ, CFG)
