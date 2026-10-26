"""Timeline for @latinagirl_ana — Halloween villain makeup look 'Victoria Bane'.

English speech (the "Nueva grabación" voice notes are English, not Spanish). On-camera intro
(IMG_8301/03/04/07/06) -> VO over the makeup process -> reveal: VO over her silent posing in the
finished look (IMG_8331*) -> on-camera outro (8333/36/39/40/32). Long pauses inside the voice notes
are squeezed by splitting each note at its silent gaps (energy runs, assets/analysis/vo_runs.json).
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\fosfe\Downloads\OFTV 26-20261019T081449Z-1-001\OFTV 26")
GAP = 0.45
PIECE_GAP = 0.3   # natural breath where a long pause was squeezed
TOPIC_TAIL = 0.4
MAX_CHARS = 32
import unicodedata
_NFC = {}
VOPATH = {}


LINES = [  # (topic, voice key, pieces, subtitle text — her words, Whisper slips fixed)
    ("base", "vo3", [(0.0, 30.54)],
     "Every villain needs a flawless base. My character, Victoria Bane, is elegant, calculated, and always in "
     "control. She never needs to be loud to get what she wants, so I'm going for a smooth matte complexion that "
     "feels polished, almost like a mask hiding all her secrets."),
    ("base", "vo3", [(33.10, 43.24), (43.96, 53.44)],
     "Victoria has very defined features, so I'm sculpting my cheeks with a cool-toned contour. For blush, "
     "I'm choosing a muted cool shade and placing it high on the cheekbones."),
    ("base", "vo3", [(59.24, 74.46)],
     "I want her to look sophisticated and a little intimidating. Not sweet, not innocent, and definitely not "
     "someone you should underestimate."),
    ("brows", "vo9", [(1.58, 25.20)],
     "The brows are what give this character her attitude. I'm creating a more defined arch with a slightly "
     "lifted tail. This shape makes the eyes look sharper and gives the face a confident, almost challenging "
     "expression."),
    ("brows", "vo9", [(26.04, 34.74)],
     "Victoria doesn't ask for permission. She already knows what she wants."),
    ("brows", "vo9", [(36.58, 41.72), (42.74, 55.92)],
     "Now for the most important part, the eyeliner. I'm creating a long, sharp wing that lifts toward the end "
     "of my brow. The shape is clean, dramatic and slightly intimidating."),
    ("brows", "vo9", [(56.98, 73.10)],
     "I want Victoria's eyes to look like she can read everyone in the room without saying a single word. "
     "And remember, the sharper the wing, the more dramatic the attitude."),
    ("lips", "vo1", [(0.32, 5.22), (5.72, 11.40)],
     "For the lips, I'm choosing a deep wine shade. It feels elegant, powerful and just a little dangerous."),
    ("lips", "vo1", [(12.06, 33.84)],
     "I'm defining the shape with a lip liner first, then filling everything in with lipstick. This is "
     "Victoria's signature, the kind of look that makes a statement before she even says a word."),
    ("details", "vo1", [(35.42, 54.20)],
     "Now it's all about the little details. I'm checking the eyeliner, adding a final coat of mascara and "
     "making sure everything looks balanced."),
    ("reveal", "vo1", [(57.42, 60.70), (61.96, 71.70), (72.26, 76.60)],
     "But the makeup alone is not enough. The real transformation is in the expression: calm, confident and "
     "just a little mysterious. Victoria never has to explain herself."),
]

# b-roll: only shots where she is working on the makeup (no direct-to-camera talking/gesturing:
# 8309(1), 8316, 8321, the wave at the end of 8330 are left out). Reveal = silent posing in the final look.
TOPICS = [  # (topic, section title or None, group, b-roll (clip, in, out))
    ("base", "The Base", "main", [("IMG_8308", 0, 2.1), ("IMG_8309", 0, 5.3), ("IMG_8310(1)", 0, 1.9),
                                  ("IMG_8310(2)", 0, 2.8), ("IMG_8310", 0, 6.8), ("IMG_8311", 0, 6.7),
                                  ("IMG_8312", 0, 8.7), ("IMG_8316(1)", 0, 16.4), ("IMG_8316(2)", 0, 4.4),
                                  ("IMG_8318", 0, 7.6), ("IMG_8317(1)", 0, 14.5)]),
    ("brows", "Brows & Eyeliner", "main", [("IMG_8313", 0, 6.7), ("IMG_8314", 0, 6.9), ("IMG_8315", 0, 6.7),
                                           ("IMG_8317", 0, 3.1), ("IMG_8319(1)", 0, 11.2), ("IMG_8320", 0, 26.1),
                                           ("IMG_8323", 0, 7.4), ("IMG_8324", 0, 45.0), ("IMG_8324(1)", 0, 8.8),
                                           ("IMG_8325", 0, 5.9), ("IMG_8325(1)", 0, 6.2)]),
    ("lips", "Lips & Details", "main", [("IMG_8327", 0, 12.1), ("IMG_8326(1)", 0, 19.1), ("IMG_8326", 0, 2.1), ("IMG_8330", 0, 3.0)]),
    ("details", None, "main", [("IMG_8322", 0, 16.6), ("IMG_8322(1)", 0, 2.9), ("IMG_8328(1)", 0, 17.7),
                               ("IMG_8328", 0, 17.6)]),
    ("reveal", "Meet Victoria Bane", "outro", [("IMG_8331(1)", 0, 9.1), ("IMG_8331(2)", 0, 4.4),
                                              ("IMG_8331(3)", 0, 4.3), ("IMG_8331", 0, 1.7)]),
]

INTRO_PARTS = [  # (clip, in, out, [(a, b, text)])
    ("IMG_8301", 0.00, 6.70, [(0.0, 6.4, "Hi everyone, I'm Ana, an OnlyFans model, and welcome back to my OFTV channel.")]),
    ("IMG_8303", 1.40, 6.00, [(1.7, 5.7, "Today I'm creating a makeup look inspired by a villain.")]),
    ("IMG_8304", 0.00, 3.40, [(0.0, 3.2, "Thin, sharp eyeliner, bold brows,")]),
    ("IMG_8307", 0.00, 3.50, [(0.0, 3.3, "sculpted cheeks and dark, dramatic lips.")]),
    ("IMG_8306", 0.00, 3.75, [(0.0, 3.5, "Let's see how powerful we can make this look.")]),
]
GOODBYE = [
    ("IMG_8333", 0.00, 3.00, [(0.0, 2.8, "And here she is, Victoria Bane.")]),
    ("IMG_8336", 0.00, 6.80, [(0.0, 6.5, "Sharp wings, sculpted cheeks, bold brows and dark lips.")]),
    ("IMG_8339", 0.00, 7.60, [(0.0, 7.3, "I love how makeup choices can completely change the way a character feels.")]),
    ("IMG_8340", 0.00, 3.60, [(0.0, 3.3, "Thank you for spending this time with me on OFTV.")]),
    ("IMG_8332", 0.00, 9.90, [(0.0, 7.5, "I'm Ana, an OnlyFans model, and if you want to see more of my personal content, "
                                         "you can subscribe to my OnlyFans."), (8.3, 9.5, "See you soon!")]),
]
ONLYFANS_OFFSET = 4.8   # into IMG_8332: "...you can subscribe to my OnlyFans"
WEAK = {"a", "an", "the", "to", "of", "and", "or", "i", "i'm", "my", "with", "for", "in", "on", "is", "are", "be",
        "if", "so", "but", "that", "this", "your", "you", "can", "we", "it's", "some", "what", "at", "about", "just",
        "it", "me", "into", "from", "when", "do", "has", "have", "i'll", "how", "every", "more", "than", "her",
        "she", "she's", "those", "such", "let", "us", "our"}


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
            if last.lower().strip(",.!?:") in WEAK:
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


def timed_cues(text, spans, words=None):
    """Time cues from the real word timestamps when given (word count alignment),
    else spread proportionally; a cue never straddles two spans (splices)."""
    cues = split_cues(text)
    if words:
        ws = [w for w in words if any(s - 0.05 <= w["start"] < e for s, e in spans)]
        n_txt = sum(len(c.split()) for c in cues)
        out, k = [], 0
        for c in cues:
            cnt = len(c.split())
            a = round(k * len(ws) / n_txt)
            b = max(a + 1, round((k + cnt) * len(ws) / n_txt))
            seg = ws[a:min(b, len(ws))] or ws[-1:]
            out.append([round(seg[0]["start"], 3), round(seg[-1]["end"], 3), c])
            k += cnt
        return out
    total = sum(e - s for s, e in spans)
    out, acc = [], 0.0
    for c in cues:
        d = total * len(c) / sum(len(x) for x in cues)
        a, b = acc, acc + d
        mid, t = (a + b) / 2, 0.0
        for s, e in spans:
            if mid <= t + (e - s) + 1e-6:
                out.append([round(s + max(0.0, a - t), 3), round(s + min(e - s, b - t), 3), c])
                break
            t += e - s
        acc = b
    return out


_R = {}


def energy(path):
    if path not in _R:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        hop = 320
        n = len(x) // hop
        _R[path] = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    return _R[path]


def quietest(path, t, lo, hi):
    r = energy(path)
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(r) - 1, int((t + hi) / 0.02))
    return (i0 + int(np.argmin(r[i0:i1 + 1]))) * 0.02


def pieces(path, ranges):
    out = []
    for a, b in ranges:
        a2 = quietest(path, a, -0.12, 0.04) if a > 0.05 else a
        b2 = quietest(path, b, -0.04, 0.12)
        out.append((round(a2, 3), round(b2, 3)))
    return out



def _old_main():
    tr = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
    video, vo, sections, subs = [], [], [], {}
    for clip, a, b, sents in INTRO_PARTS:
        video.append({"group": "intro", "src": clip, "in": a, "out": b, "speech": True})
        subs.setdefault(clip, []).extend(c for x, y, t in sents for c in timed_cues(t, [(x, y)], tr.get(clip)))
    video[-1]["pad_tail"] = 0.3
    n = 0
    for topic, title, group, clips in TOPICS:
        lines = [ln for ln in LINES if ln[0] == topic]
        plan = [pieces(VOPATH[key], r) for _, key, r, _ in lines]
        lead = 0.5
        need = lead + sum(sum(e - s for s, e in p) + PIECE_GAP * (len(p) - 1) for p in plan) \
            + GAP * (len(plan) - 1) + TOPIC_TAIL
        avail = sum(o - i for _, i, o in clips)
        k = need / avail
        assert k <= 1, (topic, need, avail)
        first = len(video)
        for src, i, o in clips:
            length = (o - i) * k
            mid = i + (o - i) / 2
            video.append({"group": group, "src": src, "in": round(mid - length / 2, 3),
                          "out": round(mid + length / 2, 3)})
        t = lead
        for (_, key, _, text), p in zip(lines, plan):
            for s, e in p:
                vo.append({"src": key, "in": s, "out": e, "item": first, "offset": round(t, 3)})
                t += (e - s) + PIECE_GAP
            t += GAP - PIECE_GAP
            subs.setdefault(key, []).extend(timed_cues(text, p, tr[key]))
        if title:
            n += 1
            sections.append({"index": n, "label": "Part", "title": title, "item": first,
                             "offset": 0.6 if group == "outro" else 0.15})
    for clip, a, b, sents in GOODBYE:
        video.append({"group": "outro", "src": clip, "in": a, "out": b, "speech": True})
        subs.setdefault(clip, []).extend(c for x, y, t in sents for c in timed_cues(t, [(x, y)], tr.get(clip)))
    last = len(video) - 1
    video[last]["pad_tail"] = 0.8
    srcs = {v["src"] for v in video}
    tl = {
        "tag": "@latinagirl_ana",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": ONLYFANS_OFFSET, "note": "'you can subscribe to my OnlyFans'"}],
        "music": [str(SRC / "HoliznaPATREON - halloween.mp3").replace("\\", "/"),
                  str(SRC / "Denys Kyshchuk - Halloween.mp3").replace("\\", "/"),
                  str(SRC / "Soundore - Halloween.mp3").replace("\\", "/")],
        "sources": {**{c: str(next(p for p in SRC.iterdir() if p.stem == c)).replace("\\", "/") for c in srcs},
                    **{k: str(p).replace("\\", "/") for k, p in VOPATH.items()}},
        "transcript_keys": {**{c: c for c in srcs}, **{k: k for k in VOPATH}},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": {},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    print(f"items={len(video)} vo_pieces={len(vo)} sections={[s['title'] for s in sections]} "
          f"~duration={tot:.1f}s longest_cue={len(longest[2])}")


if False:
    main()





