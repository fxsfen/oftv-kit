"""Guion 29 (@bela_cruz): random-pieces fashion challenge. See plan_common.py.
B-roll excluded: e2t2 0-1.8 and e3t1 0-2.5 / 6.2+ (she talks to camera), e5t4 2.5+ (leaves the frame),
e6t2 (lips close-up). Other VAD speech in the takes is the off-camera director while she poses/turns away."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import build  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
MUS = "C:/Users/fosfe/Downloads/ана2/OFTV 27-20261019T165215Z-1-001/OFTV 27/Sound Of Freedom - "

CFG = {
    "tag": "@bela_cruz",
    "music": [MUS + "Chil Hip-Hop Beat .mp3.mp3", MUS + "Lo-Fi R&B Vibe.mp3.mp3"],
    "intro": ("e1", 1.5, 17.2,
              "Hi everyone! I'm Bela, I'm an OnlyFans model and I have my own blog on OFTV. "
              "Today I decided to do a little fashion challenge. "
              "I'm going to create a look with pieces I'll pick completely at random. "
              "Let's see if something really stylish comes out of this."),
    "scenes": [
        ("The First Pieces", "vo2", [(0.80, 21.49)],
         "Let's start with the first piece. On purpose, I don't try to picture the look in advance, "
         "I just grab whatever I have at hand. The first piece will set the direction for the whole look. "
         "Now the second one, and this is where it gets more interesting, "
         "because the pieces might not match each other at all.",
         [("e2t1", 0, 7.9), ("e2t2", 1.8, 4.5), ("e2t3", 0, 8.4), ("e2t4", 0, 7.36), ("e2t5", 0, 5.3)]),
        ("Colors & Proportions", "vo3", [(1.20, 24.71)],
         "The third piece can completely change the result. I don't just look at the colors, "
         "but also at the proportions: what goes on top, what goes on the bottom, "
         "and which piece will be the main element. If a combination looks strange at first, "
         "I don't rush to rule it out. Sometimes it's the unexpected combinations "
         "that turn out to be the most interesting.",
         [("e3t1", 2.5, 6.2), ("e3t2", 0, 6.67), ("e3t2_3", 0, 4.17), ("e3t3_1", 0, 6.12),
          ("e3t3_2", 0, 8.68), ("e3t4", 0, 8.4)]),
        ("The Details", "vo4", [(1.06, 19.53)],
         "Now comes the most interesting part: the details. Shoes can make the look more relaxed "
         "or, on the contrary, give it a more structured feel. With accessories, I try not to overdo it. "
         "Sometimes one statement piece of jewelry is enough to make the whole outfit look complete.",
         [("e4t1", 0, 3.4), ("e4t2", 0, 3.17), ("e4t3", 0, 10.0), ("e4t4", 0, 4.33)]),
        ("The First Result", "vo5", [(0.48, 18.05)],
         "Well, we have our first result. Honestly, I wasn't sure these pieces could go together, "
         "but once I put them on, the look started to feel much more cohesive. "
         "Sometimes it's only when you try it on that you know if a combination works or not.",
         [("e5t1", 2.0, 9.53), ("e5t2", 0, 5.82), ("e5t3", 0, 6.46), ("e5t4", 0, 2.5)]),
        ("My Final Choice", "vo6", [(0.76, 19.21)],
         "In the end, I'm going with this option. I like that the look doesn't feel too planned, "
         "it has a certain spontaneity, and that's probably the main advantage of this kind of experiment. "
         "Sometimes it's good to step outside your usual combinations.",
         [("e6t1", 0, 14.64), ("e6t3", 0, 9.0)]),
    ],
    "outro": ("e7", 3.0, 32.4,
              "This is the look I managed to create with pieces picked completely at random, "
              "and honestly, I'm pretty happy with the result. I think sometimes these little experiments "
              "help us look at our own closet in a completely different way. "
              "Thank you for spending this time with me. I'm Bela, this was my blog on OFTV. "
              "If you want to see more of me and my content, you can subscribe to my OnlyFans. See you next time!"),
    "onlyfans_at": 29.6,
}

if __name__ == "__main__":
    build(PROJ, CFG)
