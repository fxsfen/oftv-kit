"""Timeline for the 'ки' cat-tree OFTV show edit (Lisa assembles a cat tree for Bublik and Zephyr).

English speech throughout. On-camera talking clips + four black-screen voice notes; two of
those (unboxing 6551, placement tips 6537) and the reflection 6546 are laid over silent
b-roll (Silero VAD = no speech; hands / cats / far shots, never her talking face).
Subtitles = hand-corrected text per sentence (Whisper mishears "Bublik" as "public",
"Zephyr" as "the fear"), timed from large-v3 word timestamps, one line <= 32 chars.
Show graphics (pop-ups, name tags, checklists, HUD, stamps, punches) are anchored to
source-clip times so they follow trims.
Writes artifacts/timeline.json and assets/analysis/subs_en.json.
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "ки"][0]
TALK_IN, TALK_OUT = 0.3, 0.45
MAX_CHARS = 32
TAG = None  # user: no OnlyFans pop-ups in this edit

L, R = 170, 3670  # sticker x for left / right anchors
TOP = 210


def L_(text, sub, icon, color, y=TOP):
    return {"text": text, "sub": sub, "icon": icon, "color": color, "x": L, "y": y, "anchor": "left", "tilt": -3}


def R_(text, sub, icon, color, y=TOP):
    return {"text": text, "sub": sub, "icon": icon, "color": color, "x": R, "y": y, "anchor": "right", "tilt": 3}


# Each segment: ("talk", clip, [ranges], [(a, b, text)], [graphics], zoom2nd)
#               ("vo", clip, (a, b), [(a, b, text)], [(vo_t, broll_clip, broll_in)], end_t, [graphics])
#               ("cut", clip, a, b, [graphics])                     silent cutaway
# graphics: (src_time, comp, props, dur[, sfx]) — src_time in the segment's audio clip
# (for cutaways: seconds from the cutaway start).
CHAPTERS = {}  # segment index -> (index, title, color)

SEGMENTS = [
    # ------------------------------------------------------------------ intro
    ("talk", "IMG_1955", [(0.0, 33.0)], [
        (0.00, 2.80, "Hi, I'm Lisa and you're watching my OnlyFans TV."),
        (3.06, 8.46, "Today is a special day. Not for me, for them, for Bublik and Zephyr, my cats."),
        (8.64, 12.42, "My little tyrants, whom I love more than reason allows."),
        (12.78, 19.12, "In this box: a cat tree with a house, two platforms and a scratching post."),
        (19.34, 24.18, "And today I'm assembling it with my own hands, in the garden, for them."),
        (24.18, 33.00, "They don't know about it yet. I know they'll adore it. Or they won't, because... cats. But we'll try."),
    ], [
        (3.2, "ShowTitle", {"eyebrow": "Today on the show", "lines": ["Cat Tower", "Challenge"],
                        "sub": "Built by hand. Judged by cats."}, 5.2, "whoosh"),
        (9.0, "PopSticker", R_("Bublik & Zephyr", "my little tyrants", "crown", "pink"), 3.6),
        (12.9, "Checklist", {"title": "In the box", "items": ["Cat house", "2 platforms", "Scratching post"],
                             "every": 1.6}, 6.0),
        (19.4, "PopSticker", L_("DIY in the garden", "built with my own hands", "wrench", "teal"), 4.4),
        (24.3, "PopSticker", R_("Shh... they don't know yet", "surprise inspection pending", "eyes", "violet"), 4.4),
        (31.1, "Punch", {"text": "BECAUSE CATS.", "color": "yellow", "x": 1200, "y": 560, "tilt": -6}, 1.9),
    ], None, "intro"),
    # ------------------------------------------------------------- 1 unboxing
    ("vo", "IMG_6551", (0.66, 45.30), [
        (0.66, 2.82, "We unpacked. I love this moment."),
        (3.06, 8.20, "Here is the base of the house, with an arch at the bottom for the cat."),
        (8.54, 15.88, "Dark and cozy inside, perfect for Bublik, who loves to hide and pretend he doesn't exist."),
        (16.40, 23.02, "Here is the jute post. This is a scratching post, a sacred object in the cat world."),
        (23.54, 28.32, "Here are the two platforms, they attach on top of the post."),
        (29.10, 31.32, "Plush covering, soft and warm."),
        (31.54, 33.60, "Why did I buy this at all?"),
        (33.78, 40.80, "Because Bublik scratches my sofa, and Zephyr jumps on the fridge and looks down at me like a queen."),
        (41.40, 45.30, "They need their own kingdom. Here it is."),
    ], [  # (vo source time where the shot starts, clip, clip in)
        (0.0, "IMG_2430", 20.5),
        (3.0, "IMG_2434", 0.4),
        (8.4, "IMG_2434", 5.9),
        (16.3, "IMG_2434", 21.0),
        (20.0, "IMG_2438", 7.0),
        (23.4, "IMG_2432", 29.5),
        (29.0, "IMG_6521", 30.5),
        (31.5, "IMG_6523", 0.3),
        (41.3, "IMG_2430", 40.0),
    ], 46.0, [
        (3.3, "PopSticker", R_("The house", "arched door, dark & cozy", "home", "orange"), 4.6),
        (9.4, "PopSticker", L_("Bublik's hideout", "pretends he doesn't exist", "eyes", "pink"), 5.2),
        (16.5, "PopSticker", R_("Jute post", "a sacred object in the cat world", "star", "yellow"), 5.6),
        (23.6, "PopSticker", L_("2 platforms", "plush, soft & warm", "spark", "teal"), 7.4),
        (33.9, "PopSticker", R_("Bublik", "professional sofa destroyer", "paw", "pink"), 3.4),
        (37.4, "PopSticker", L_("Zephyr", "queen of the fridge", "crown", "violet"), 3.6),
        (41.5, "Stamp", {"text": "THEIR KINGDOM", "sub": "EST. TODAY", "color": "orange", "x": 1920, "y": 760}, 3.4),
    ]),
    # ---------------------------------------------------------------- 2 build
    ("talk", "IMG_2448", [(0.0, 12.9), (14.34, 19.74)], [
        (0.00, 2.24, "We start with the base of the house."),
        (2.50, 7.78, "We assemble the walls, attach the floor and ceiling, everything with fasteners."),
        (8.02, 12.90, "Nothing complicated. The main thing is that the structure is sturdy."),
        (14.34, 19.74, "Because Bublik weighs 6 kg. That's not a cat, that's a small bear."),
    ], [
        (4.4, "StepHud", {"step": 1, "total": 4, "label": "Base of the house"}, 4.0),
        (14.6, "PopSticker", R_("Bublik: 6 kg", "not a cat, a small bear", "paw", "pink"), 5.0),
    ], 1.08),
    ("talk", "IMG_2462", [(0.0, 38.14)], [
        (0.00, 6.94, "A scratching post is the perfect option: strong, natural and pleasant for cat claws."),
        (7.22, 14.60, "The cat scratches it and doesn't scratch your furniture. In theory. In fact, Bublik scratches everything."),
        (15.06, 25.24, "The sofa, the carpet, my sweater, while I'm wearing it. But with a scratching post, less. A little less often."),
        (25.24, 38.14, "Attach the post to the base, check if it wobbles. It doesn't. Good, because if it falls on Bublik while he's sleeping, he'll be offended for a week."),
    ], [
        (0.4, "StepHud", {"step": 2, "total": 4, "label": "Scratching post"}, 4.0),
        (7.3, "PopSticker", R_("Saves your furniture*", "*in theory", "star", "yellow"), 4.6),
        (13.9, "Punch", {"text": "EVERYTHING!", "color": "pink", "x": 1250, "y": 620, "tilt": -5}, 1.7),
        (15.2, "Checklist", {"title": "Bublik's victims", "items": ["Sofa", "Carpet", "My sweater"], "every": 1.3}, 6.6),
        (30.5, "Stamp", {"text": "STURDY", "sub": "WOBBLE TEST PASSED", "color": "teal", "x": 2750, "y": 620}, 2.8),
        (34.4, "PopSticker", L_("Offended for a week", "if it ever falls on him", "clock", "violet"), 3.8),
    ], None),
    ("talk", "IMG_2521", [(0.0, 12.82)], [
        (0.00, 2.32, "The post is the most important part for a cat."),
        (2.46, 8.54, "Scratching is instinct. That's how they mark territory, relieve stress and file their claws."),
        (9.46, 12.82, "You can't stop it, but you can redirect it."),
    ], [
        (3.2, "Checklist", {"title": "Why cats scratch", "items": ["Mark territory", "Relieve stress", "File claws"],
                            "every": 1.35, "side": "right"}, 6.0),
        (9.5, "PopSticker", R_("Can't stop it?", "redirect it!", "spark", "teal"), 3.6),
    ], None),
    ("talk", "IMG_2522", [(0.0, 19.46)], [
        (0.00, 3.40, "Bublik is three years old. Fluffy, lazy..."),
        (3.44, 7.90, "His favorite activity is sleep. Then waking up. Then sleeping again."),
        (7.98, 13.80, "But there's one weakness: he can't see a box or a bag without climbing inside."),
        (13.90, 19.46, "Any box is his property. So he'll happily climb into this little house."),
    ], [
        (0.3, "NameTag", {"name": "Bublik", "role": "3 y.o.  ·  fluffy  ·  lazy", "color": "pink", "label": "Meet the boss"}, 5.6),
        (11.0, "PopSticker", R_("Any box = his property", "bags too", "box", "orange"), 4.4),
    ], None),
    ("cut", "IMG_6523", 10.2, 16.0, [
        (0.4, "PopSticker", L_("Inspection in progress", "chief tester on duty", "eyes", "pink"), 4.0),
    ]),
    # ------------------------------------------------------- 3 zephyr's level
    ("talk", "IMG_6529", [(0.0, 13.68)], [
        (0.00, 3.28, "First platform, middle level. This one is for Zephyr."),
        (3.34, 13.68, "She likes height, but not too much, to control the situation and still be close for petting. Because despite all her superiority, she's a terrible little cuddle monster."),
    ], [
        (1.0, "StepHud", {"step": 3, "total": 4, "label": "Middle platform"}, 3.8),
        (10.0, "PopSticker", R_("Cuddle monster", "despite all her superiority", "heart", "pink"), 3.8),
    ], None),
    ("talk", "IMG_6532", [(0.0, 13.04)], [
        (0.00, 3.36, "Zephyr is two years old. Beautiful, and she knows it."),
        (3.54, 13.04, "She walks around the apartment like a model on a runway, looks down at Bublik from above. And not only because she's slimmer."),
    ], [
        (0.2, "NameTag", {"name": "Zephyr", "role": "2 y.o.  ·  runway model", "color": "violet", "label": "Meet the queen"}, 5.6),
        (8.4, "PopSticker", R_("Looks down on Bublik", "literally", "crown", "violet"), 4.0),
    ], None),
    ("talk", "IMG_6534", [(2.02, 23.86)], [
        (2.02, 5.86, "Her favorite habit is to sit exactly in the middle of everything."),
        (6.12, 9.52, "I'm reading a book? She's on the book."),
        (9.70, 13.04, "I'm working on the laptop? She's on the keyboard."),
        (13.38, 19.08, "I'm trying to assemble a cat tree? She comes and sits on the parts."),
        (19.28, 23.86, "I'm waiting. Platform installed. I check the stability: it holds well."),
    ], [
        (6.2, "PopSticker", L_("Reading?", "she's on the book", "eyes", "violet"), 3.4),
        (9.8, "PopSticker", R_("Working?", "she's on the keyboard", "eyes", "violet"), 3.4),
        (13.5, "PopSticker", L_("Building?", "she's on the parts", "wrench", "violet"), 4.6),
        (20.6, "PopSticker", R_("Stability check", "holds well", "check", "teal"), 3.4),
    ], None),
    # ------------------------------------------------------ 4 the perfect spot
    ("vo", "IMG_6537", (0.0, 46.58), [
        (0.00, 2.64, "Top platform, for kings and queens."),
        (3.52, 6.48, "Now, where to put the cat tree at home?"),
        (6.86, 14.48, "First: near a window. Cats love watching the street. For them it's like Netflix, but free."),
        (15.04, 21.36, "Second: not in a draft. The plush covering holds warmth, but cats don't like wind."),
        (22.18, 32.30, "Third: in a quiet spot. Not where people constantly walk. Cats need their own corner where they're in charge."),
        (32.60, 46.58, "Fourth: stable and safe. Check that the cat tree doesn't wobble. Because if it falls, the cat will never go near it again. Ever. On principle."),
    ], [
        (0.0, "IMG_6536", 16.0),
        (3.4, "IMG_6542", 0.5),
        (6.8, "IMG_6544", 0.3),
        (15.0, "IMG_6536", 1.5),
        (22.1, "IMG_6536", 9.5),
        (28.0, "IMG_6544", 9.0),
        (32.5, "IMG_6543", 8.0),
        (41.0, "IMG_6544", 19.5),
    ], 47.4, [
        (0.3, "PopSticker", R_("Top floor", "for kings & queens", "crown", "yellow"), 3.0),
        (6.9, "PopSticker", L_("1 · Near a window", "Netflix for cats, but free", "eyes", "orange"), 7.6),
        (15.1, "PopSticker", R_("2 · No drafts", "warm plush, zero wind", "home", "teal"), 6.6),
        (22.3, "PopSticker", L_("3 · A quiet corner", "where they're in charge", "crown", "violet"), 10.0),
        (32.7, "PopSticker", R_("4 · Stable & safe", "no wobbles allowed", "check", "pink"), 8.0),
        (45.0, "Punch", {"text": "ON PRINCIPLE.", "color": "pink", "x": 1920, "y": 820, "tilt": -4}, 1.9),
    ]),
    # ------------------------------------------------------------ 5 the reveal
    ("talk", "IMG_6538", [(0.0, 20.02)], [
        (0.00, 1.00, "Done! Here it is."),
        (1.08, 6.10, "The house for Bublik and Zephyr: a house with an arch at the bottom,"),
        (6.16, 11.20, "first platform in the middle, second platform on top, a post between them."),
        (11.36, 16.30, "Everything plush, soft, beige... Beautiful. Beautiful."),
        (16.52, 20.02, "Now the main question: how will the cats react?"),
    ], [
        (0.1, "Punch", {"text": "DONE!", "color": "yellow", "x": 1150, "y": 560, "tilt": -6}, 1.6),
        (1.9, "StepHud", {"step": 4, "total": 4, "label": "Assembled!"}, 4.2),
        (14.6, "Punch", {"text": "BEAUTIFUL!", "color": "pink", "x": 1150, "y": 600, "tilt": 5}, 1.8),
        (16.6, "PopSticker", L_("The main question", "how will the cats react?", "eyes", "orange"), 3.8),
    ], None),
    ("talk", "IMG_6540", [(0.0, 16.82)], [
        (0.00, 9.08, "There are two options. Option one: they ignore it for a week, then one sniffs it, then the other, then both sleep there every day."),
        (9.24, 15.90, "Option two: one claims it immediately, and the other is offended that the first took the best spot."),
        (16.00, 16.82, "Cat drama begins."),
    ], [
        (0.9, "PopSticker", L_("Option 1", "ignore, sniff, then sleep there daily", "clock", "teal"), 8.2),
        (9.3, "PopSticker", R_("Option 2", "one claims it, the other is offended", "crown", "pink"), 6.6),
        (16.0, "Punch", {"text": "CAT DRAMA!", "color": "yellow", "x": 1300, "y": 620, "tilt": -5}, 1.7),
    ], None),
    ("talk", "IMG_6541", [(0.0, 4.98)], [
        (0.00, 2.68, "With Bublik and Zephyr, definitely option two."),
        (3.22, 4.98, "Stay tuned for the report!"),
    ], [
        (1.7, "Stamp", {"text": "OPTION 2", "sub": "GUARANTEED", "color": "pink", "x": 2950, "y": 600}, 3.0),
    ], None),
    # -------------------------------------------------------------- 6 cat test
    ("talk", "IMG_6548", [(0.0, 8.84)], [
        (0.00, 4.06, "That's what all this was for. For exactly this picture."),
        (4.28, 6.92, "Bublik and Zephyr, the house is ready."),
        (7.16, 8.84, "Welcome, little tyrants!"),
    ], [
        (7.1, "Punch", {"text": "WELCOME HOME!", "color": "orange", "x": 1700, "y": 520, "tilt": -4}, 1.9),
    ], None),
    ("cut", "IMG_6547", 6.5, 14.0, [
        (0.5, "PopSticker", R_("Zephyr", "top floor, obviously", "crown", "violet"), 4.4),
    ]),
    ("talk", "IMG_6549", [(0.0, 26.78)], [
        (0.00, 2.06, "I imagine the scene."),
        (2.28, 12.58, "Bublik comes, sniffs, climbs into the house, turns around a few times, gets comfortable, falls asleep."),
        (12.76, 20.38, "Zephyr comes, sees that Bublik took the house, jumps to the top platform, sits there and looks down at Bublik."),
        (20.38, 26.78, "Then I come, both are asleep, and I stand there smiling like an idiot."),
    ], [
        (2.4, "PopSticker", L_("Bublik", "sniff, climb in, spin, sleep", "paw", "pink"), 9.6),
        (12.9, "PopSticker", R_("Zephyr", "top platform, looking down", "crown", "violet"), 7.2),
        (20.5, "PopSticker", L_("Both asleep", "me: smiling like an idiot", "heart", "orange"), 6.0),
    ], None),
    ("cut", "IMG_6552", 4.5, 12.5, [
        (0.8, "Stamp", {"text": "CAT APPROVED", "sub": "OFFICIALLY", "color": "pink", "x": 2700, "y": 700}, 3.6),
    ]),
    # ---------------------------------------------------------- final thoughts
    ("vo", "IMG_6546", (0.52, 33.08), [
        (0.52, 4.36, "I stand and look at this little house and I think:"),
        (5.38, 12.64, "cats give us so much. They don't speak, they can't hug, they generally pretend they don't need us at all."),
        (13.04, 22.10, "But when you're feeling bad, they come and lie down next to you. Just like that. Without words, they feel it."),
        (22.98, 33.08, "Bublik always comes when I cry, Zephyr when I'm sick. They don't understand what's happening, but they're there, and that matters a lot."),
    ], [
        (0.0, "IMG_6547", 14.5),
        (9.0, "IMG_6552", 13.0),
        (29.0, "IMG_6544", 26.0),
    ], 34.0, [
        (23.0, "PopSticker", L_("Always there", "Bublik when I cry, Zephyr when I'm sick", "heart", "pink"), 6.4),
    ], "outro"),
    ("talk", "IMG_6594", [(0.0, 24.54), (27.74, 36.22)], [
        (0.00, 3.34, "And that's it, the cat tree is assembled."),
        (3.78, 8.72, "Made with love. The cats don't know yet, but they'll find out soon."),
        (8.94, 12.08, "If you have cats, do something special for them."),
        (12.26, 15.00, "You don't have to buy an expensive cat tree."),
        (15.24, 19.94, "Just give them your time. Play with them, pet them, cuddle them."),
        (20.36, 24.54, "They give us so much, give them a little more in return."),
        (27.74, 31.02, "Thank you for being here with me on my OnlyFans TV."),
        (31.28, 35.28, "More Bublik, Zephyr and my life on my OnlyFans."),
        (35.42, 36.22, "See you!"),
    ], [
        (15.1, "Checklist", {"title": "What cats need", "items": ["Your time", "Play", "Pets & cuddles"],
                             "every": 1.4, "side": "left"}, 5.4),
        (20.5, "PopSticker", L_("Give a little more", "they give us so much", "heart", "pink"), 4.0),
        (35.4, "Punch", {"text": "SEE YOU!", "color": "orange", "x": 1150, "y": 600, "tilt": -5}, 1.6),
    ], 1.08),
]
MUSIC = ["Sound Of Freedom - Lo-Fi R&B Vibe.mp3.mp3", "Sound Of Freedom - Chil Hip-Hop Beat .mp3.mp3",
         "On The Flip - The Grey Room _ Density & Time (2).mp3"]  # chained, 6 s crossfades
OUTRO_FROM = 18  # the Final Thoughts voice-over
TAG_REPEAT = ("IMG_6594", 34.5)  # "...on my OnlyFans"
CHAPTER_AT = {1: ("Unboxing", "orange"), 2: ("The Build", "teal"), 7: ("Zephyr's Level", "violet"),
              10: ("The Perfect Spot", "teal"), 11: ("The Reveal", "pink"), 14: ("Cat Test", "orange"),
              18: ("Final Thoughts", "pink")}

WEAK = {"a", "an", "the", "to", "of", "and", "or", "i", "i'm", "my", "with", "for", "in", "on", "is", "are", "be",
        "if", "so", "but", "that", "this", "your", "you", "can", "we", "it's", "some", "what", "at", "about", "just",
        "it", "me", "into", "from", "when", "do", "has", "have", "i'll", "how", "every", "more", "than", "her",
        "she", "she's", "those", "such", "let", "us", "our", "they", "they're", "he", "he's", "his", "their", "not"}


def split_cues(text):
    """Fewest balanced one-line cues (<= MAX_CHARS) via DP; breaks prefer punctuation and
    never leave a short function word dangling at the end of a cue."""
    words = text.split()
    n = len(words)
    ideal = len(text) / max(1, -(-len(text) // MAX_CHARS))

    def cost(i, j):
        s = " ".join(words[i:j])
        if len(s) > MAX_CHARS:
            return None
        c = (len(s) - ideal) ** 2 + 150
        last = words[j - 1]
        if j < n:
            if last.lower() in WEAK:  # "it." at a sentence end is fine
                c += 400
            if re.search(r"[,.!?:]$", last):
                c -= 120
        return c

    best = [0.0] + [None] * n
    back = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(j):
            c = cost(i, j)
            if c is None or best[i] is None:
                continue
            if best[j] is None or best[i] + c < best[j]:
                best[j], back[j] = best[i] + c, i
    parts, j = [], n
    while j > 0:
        parts.insert(0, " ".join(words[back[j]:j]))
        j = back[j]
    return parts


def timed_cues(text, a, b, words):
    """Cue timing from the real word timestamps (word-count alignment inside [a, b])."""
    cues = split_cues(text)
    ws = [w for w in words if a - 0.05 <= w["start"] < b]
    if not ws:
        ws = [{"start": a, "end": b}]
    n_txt = sum(len(c.split()) for c in cues)
    out, k = [], 0
    for c in cues:
        cnt = len(c.split())
        i = round(k * len(ws) / n_txt)
        j = max(i + 1, round((k + cnt) * len(ws) / n_txt))
        seg = ws[i:min(j, len(ws))] or ws[-1:]
        out.append([round(max(a, seg[0]["start"]), 3), round(min(b + 0.3, seg[-1]["end"]), 3), c])
        k += cnt
    return out


_R = {}


def energy(clip):
    if clip not in _R:
        import soundfile as sf
        x, sr = sf.read(str(PROJ / "assets/analysis/wav16" / f"{clip}.wav"), dtype="float32")
        hop = 320
        n = len(x) // hop
        _R[clip] = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    return _R[clip]


def quietest(clip, t, lo, hi):
    r = energy(clip)
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(r) - 1, int((t + hi) / 0.02))
    return (i0 + int(np.argmin(r[i0:i1 + 1]))) * 0.02


def dur(clip):
    p = next(SRC.glob(f"{clip}.*"))
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout)


def main():
    tr = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
    video, vo, sections, subs, graphics = [], [], [], {}, []
    group = "intro"
    srcs = set()
    for si, seg in enumerate(SEGMENTS):
        kind, clip = seg[0], seg[1]
        group = "intro" if si == 0 else "outro" if si >= OUTRO_FROM else "main"
        first = len(video)
        srcs.add(clip)
        if kind == "talk":
            _, _, ranges, sents, gfx, zoom2 = seg[:6]
            d = dur(clip)
            anchors = []
            for ri, (a, b) in enumerate(ranges):
                a2 = max(0.0, quietest(clip, a, -TALK_IN, -0.02) if a > 0.1 else a - TALK_IN)
                b2 = min(d - 0.05, quietest(clip, b, 0.02, TALK_OUT))
                it = {"group": group, "src": clip, "in": round(max(0.0, a2), 3), "out": round(b2, 3), "speech": True}
                if ri > 0 and zoom2:
                    it["zoom"] = zoom2
                video.append(it)
                anchors.append(len(video) - 1)
            subs.setdefault(clip, []).extend(c for a, b, t in sents for c in timed_cues(t, a, b, tr[clip]))
            for g in gfx:
                t = g[0]
                idx = next(i for i in anchors if video[i]["in"] - 0.5 <= t < video[i]["out"] + 0.5)
                graphics.append({"comp": g[1], "props": g[2], "dur": g[3], "sfx": g[4] if len(g) > 4 else "pop",
                                 "item": idx, "offset": round(max(0.0, t - video[idx]["in"]), 3)})
        elif kind == "vo":
            _, _, (a, b), sents, shots, end_t, gfx = seg[:7]
            lead = 0.5
            a2 = quietest(clip, a, -0.12, 0.0) if a > 0.1 else a
            b2 = quietest(clip, b, 0.0, 0.25)
            # shots: vo time -> output time = lead + (vo_t - a2)
            for k, (vt, bclip, bin_) in enumerate(shots):
                vt_next = shots[k + 1][0] if k + 1 < len(shots) else end_t
                t0 = 0.0 if k == 0 else lead + vt - a2
                t1 = lead + vt_next - a2
                length = t1 - t0
                assert bin_ + length <= dur(bclip) - 0.05, (bclip, bin_, length, dur(bclip))
                video.append({"group": group, "src": bclip, "in": round(bin_, 3), "out": round(bin_ + length, 3)})
                srcs.add(bclip)
            vo.append({"src": clip, "in": round(a2, 3), "out": round(b2, 3), "item": first, "offset": lead})
            subs.setdefault(clip, []).extend(c for x, y, t in sents for c in timed_cues(t, x, y, tr[clip]))
            for g in gfx:
                graphics.append({"comp": g[1], "props": g[2], "dur": g[3], "sfx": g[4] if len(g) > 4 else "pop",
                                 "item": first, "offset": round(lead + g[0] - a2, 3)})
        else:  # silent cutaway
            _, _, a, b, gfx = seg
            video.append({"group": group, "src": clip, "in": a, "out": b})
            for g in gfx:
                graphics.append({"comp": g[1], "props": g[2], "dur": g[3], "sfx": g[4] if len(g) > 4 else "pop",
                                 "item": first, "offset": g[0]})
        if si in CHAPTER_AT:
            title, color = CHAPTER_AT[si]
            sections.append({"index": len(sections) + 1, "title": title, "color": color, "item": first,
                             "offset": 0.6 if si == OUTRO_FROM else 0.15})
    # the same footage must never show twice
    for i, v in enumerate(video):
        for w in video[i + 1:]:
            if v["src"] == w["src"] and v["in"] < w["out"] - 0.05 and w["in"] < v["out"] - 0.05:
                raise SystemExit(f"repeated footage: {v['src']} {v['in']}-{v['out']} vs {w['in']}-{w['out']}")
    # whip boundaries need >= 0.5 s of non-speech
    video[0]["pad_tail"] = 0.4
    video[-1]["pad_tail"] = 1.2

    clip, t = TAG_REPEAT
    idx = max(i for i, v in enumerate(video) if v["src"] == clip and v["in"] <= t)
    tl = {
        "tag": TAG,
        "tag_at": 0.8,
        "tag_repeats": [],
        "music": [str(SRC / m).replace("\\", "/") for m in MUSIC],
        "sources": {c: str(next(SRC.glob(f"{c}.*"))).replace("\\", "/") for c in srcs},
        "video": video,
        "vo": vo,
        "sections": sections,
        "graphics": graphics,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    print(f"items={len(video)} vo={len(vo)} graphics={len(graphics)} sections={[s['title'] for s in sections]} "
          f"~duration={tot:.1f}s longest_cue={len(longest[2])} '{longest[2]}'")
    print("groups:", [(v["group"], v["src"]) for v in video])


if __name__ == "__main__":
    main()
