"""Timeline for Miya Moore's 'healthy lifestyle rules' karate talk (@miya_moore).

One 5:45 talking-head take (мм1.MOV, upside-down iPhone, ffmpeg auto-rotates) full of
retakes. KEEP lists the clean source ranges (from the phrase-by-phrase large-v3 pass,
assets/analysis/phrases.json, plus a context re-check of doubtful spans). Pauses longer
than MAX_PAUSE inside a range are squeezed; every cut alternates a 1.08 punch-in so jump
cuts read as cuts. Subtitles come from the per-phrase words with WORD_EDITS applied,
one line <= 32 chars, cut per item so a cue never straddles a splice.
"""
import json
import re
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
SRC = "C:/Users/fosfe/Downloads/Новая папка (18)/мм1.MOV"
MUSIC = ["C:/Users/fosfe/Downloads/Новая папка (18)/It'll Be Alright - R.LUM.R.mp3",
         "C:/Users/fosfe/Downloads/Новая папка (18)/Never Play - Jeremy Blake.mp3"]
MAX_PAUSE, KEEP_PAUSE = 0.8, 0.45
MAX_CHARS = 32
SIL = 12  # dB over the noise floor = speech

# (group, source in, source out, note) — removed stretches are listed in REMOVED below
KEEP = [
    ("intro", 14.25, 43.20, "greeting, black belt, healthy is not about perfect"),
    ("intro", 44.30, 56.06, "Today I want to share a few simple rules"),
    ("main", 56.10, 71.42, "rule 1: consistency > perfection ... 'but honestly that's'"),
    ("main", 74.26, 94.12, "'unrealistic for most people' ... 'progress comes from repetition,'"),
    ("main", 123.38, 131.72, "clean take: 'Small efforts, repeated hours... short bursts of motivation'"),
    ("main", 133.30, 169.10, "rule 2: keep moving"),
    ("main", 169.38, 186.00, "rule 3: recovery ... 'as important as training'"),
    ("main", 207.90, 223.88, "clean take 'Good sleep helps your body repair itself' + listen to my body"),
    ("main", 223.88, 252.55, "rule 4: discipline > motivation ... 'difficult days'"),
    ("main", 266.40, 276.98, "clean take 'I think many positive changes ... don't feel like it'"),
    ("outro", 276.98, 304.45, "recap of the rules ... 'these habits can'"),
    ("outro", 304.82, 312.55, "'make a big difference over time. Thank you for spending this time with me'"),
    ("outro", 313.15, 319.45, "I hope sharing my experience was interesting and helpful"),
    ("outro", 319.88, 341.05, "subscribe to my OnlyFans ... bye-bye"),
]
REMOVED = [
    (0.0, 14.25, "camera set-up close-up, mic noise"),
    (43.20, 44.30, "pause"),
    (71.42, 74.26, "'a... I don't know'"),
    (94.12, 123.38, "two broken takes of 'small effort, repeated...', 'Понятно?', 'mm-hmm', 'blah blah blah', "
                    "'I'm in a hurry'"),
    (186.00, 207.90, "broken 'Good sleep helps your body repair', walks to the camera (close-up), 'just a second'"),
    (252.55, 266.40, "broken first take 'I think many positive changes... keep going do', close-up at 4:20"),
    (304.45, 304.82, "doubled 'can'"),
    (341.05, 344.64, "'thank you' mumble while reaching for the camera"),
]
SECTIONS = [  # (source time, title)
    (56.21, "Consistency First"),
    (133.45, "Keep Moving"),
    (169.52, "Recovery Matters"),
    (223.95, "Discipline Wins"),
    (277.08, "Final Thoughts"),
]
ONLYFANS_AT = 330.99

WORD_EDITS = {  # source start of a word -> replacement ("" drops it)
    16.15: "Miya", 21.81: "sports", 37.97: "habits", 38.75: "make", 39.95: "strong,", 42.45: "happy.",
    67.29: "routine", 93.21: "repetition.", 234.35: "Motivation", 251.87: "days.", 280.55: "consistent,",
    312.23: "me.", 329.01: "you", 326.89: "content,", 340.31: "Bye-bye.", 340.63: "",
    44.67: "Today", 45.45: "I want to", 45.67: "", 45.85: "", 46.01: "",
    49.19: "help",
    129.67: "bursts of",
    135.53: "simple:", 136.33: "Keep",
    155.73: "",  # "and I always I feel better" -> one "I"
    177.59: "harder", 178.23: "always", 179.37: "the",
    220.57: "instead", 220.87: "", 221.35: "",
    226.15: "karate",
    271.57: "doing", 276.65: "it.", 276.93: "So", 278.13: "my", 279.73: "rules:", 281.61: "moving,",
    287.37: "rely on", 287.75: "",  # Whisper: "really want" (doubtful — flagged)
    306.65: "over", 307.73: "time.",
    310.21: "", 310.89: "spending",
    324.83: "karate",
    318.75: "helpful.",
}
INSERT_WORDS = [  # Whisper returned an empty phrase here
    {"word": " prioritize", "start": 284.46, "end": 285.94},
]

WEAK = {"a", "an", "the", "to", "of", "and", "or", "i", "i'm", "my", "with", "for", "in", "on", "is", "are", "be",
        "if", "so", "but", "that", "this", "your", "you", "can", "we", "it's", "some", "what", "at", "about", "just",
        "it", "me", "into", "from", "when", "do", "has", "have", "i'll", "how", "every", "more", "than", "her",
        "she", "those", "such", "let", "us", "our", "were", "was", "these", "as"}


def split_cues(words):
    """DP over word breaks: fewest balanced one-line cues <= MAX_CHARS, prefer punctuation,
    never end a cue on a weak function word."""
    toks = [w["word"] for w in words]
    n = len(toks)
    text = " ".join(toks)
    ideal = len(text) / max(1, -(-len(text) // MAX_CHARS))

    def cost(i, j):
        s = " ".join(toks[i:j])
        if len(s) > MAX_CHARS and j - i > 1:
            return None
        c = (len(s) - ideal) ** 2 + 150
        if j < n:
            if toks[j - 1].lower().strip(",.!?:") in WEAK:
                c += 400
            if re.search(r"[,.!?:]$", toks[j - 1]):
                c -= 120
        return c

    best, back = [0.0] + [None] * n, [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(j):
            c = cost(i, j)
            if c is not None and best[i] is not None and (best[j] is None or best[i] + c < best[j]):
                best[j], back[j] = best[i] + c, i
    out, j = [], n
    while j > 0:
        i = back[j]
        out.insert(0, [words[i]["start"], words[j - 1]["end"], " ".join(toks[i:j])])
        j = i
    return out


def main():
    ph = json.load(open(PROJ / "assets/analysis/phrases.json", encoding="utf-8"))["phrases"]
    words = [w for p in ph for w in p["words"]] + INSERT_WORDS
    words.sort(key=lambda w: w["start"])
    clean = []
    for w in words:
        t = WORD_EDITS.get(round(w["start"], 2), w["word"].strip())
        if t:
            clean.append({"word": t, "start": w["start"], "end": w["end"]})
    # capitalise sentence starts after the edits
    for i, w in enumerate(clean):
        if i == 0 or re.search(r"[.!?]$", clean[i - 1]["word"]):
            w["word"] = w["word"][:1].upper() + w["word"][1:]

    # Pauses are found from word timings (not energy: quiet word onsets like "You can..." read
    # as silence and got clipped). A gap > MAX_PAUSE between two words is cut down to KEEP_PAUSE.
    def squeeze(a, b):
        ws = [w for w in words if a - 0.05 <= w["start"] and w["end"] <= b + 0.15]
        out, cur = [], a
        for w0, w1 in zip(ws, ws[1:]):
            if w1["start"] - w0["end"] > MAX_PAUSE:
                out.append((cur, w0["end"] + KEEP_PAUSE / 2))
                cur = w1["start"] - KEEP_PAUSE / 2
        out.append((cur, b))
        return [(round(s, 3), round(e, 3)) for s, e in out if e - s > 0.3]

    video, subs, zoom = [], [], False
    prev_group = None
    for group, a, b, _ in KEEP:
        if group != prev_group:
            zoom = False  # a whip resets the framing
        for s, e in squeeze(a, b):
            it = {"group": group, "src": "mm1", "in": s, "out": e, "speech": True}
            if zoom:
                it["zoom"] = 1.08
            video.append(it)
            zoom = not zoom
            ws = [w for w in clean if s - 0.05 <= w["start"] and w["end"] <= e + 0.15]
            # sentences inside this item, then one-line cues
            sent = []
            for w in ws:
                sent.append(w)
                if re.search(r"[.!?:]$", w["word"]) or w is ws[-1]:
                    subs += split_cues(sent)
                    sent = []
        prev_group = group
    # whips (intro->main, main->outro) need >= 0.5 s of non-speech: freeze the edge frames
    for i in range(1, len(video)):
        if video[i]["group"] != video[i - 1]["group"]:
            video[i - 1]["pad_tail"] = 0.35
            video[i]["pad_head"] = 0.3
    video[-1]["pad_tail"] = 1.2

    def locate(t):
        for k, it in enumerate(video):
            if it["in"] - 0.3 <= t <= it["out"]:
                return k, round(max(0.0, t - it["in"]) + it.get("pad_head", 0.0), 3)
        raise ValueError(t)

    sections = []
    for n, (t, title) in enumerate(SECTIONS, 1):
        k, off = locate(t)
        sections.append({"index": n, "label": "Part", "title": title, "item": k, "offset": max(0.15, off)})
    k, off = locate(ONLYFANS_AT)
    tl = {
        "tag": "@miya_moore",
        "tag_at": 0.8,
        "tag_repeats": [{"item": k, "offset": off, "note": "'you can subscribe to my OnlyFans'"}],
        "music": MUSIC,
        "sources": {"mm1": SRC},
        "transcript_keys": {"mm1": "mm1"},
        "video": video,
        "vo": [],
        "sections": sections,
        "word_edits": {},
        "removed": REMOVED,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps({"mm1": subs}, indent=1, ensure_ascii=False),
                                                       encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) + v.get("pad_head", 0) for v in video) - 1.0
    print(f"items={len(video)} cues={len(subs)} longest={max(len(c[2]) for c in subs)} ~duration={tot:.1f}s")
    print(" / ".join(c[2] for c in subs))


if __name__ == "__main__":
    main()
