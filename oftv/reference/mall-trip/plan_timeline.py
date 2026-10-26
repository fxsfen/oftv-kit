"""Timeline for 'Meet my Siamese cat Pookie' (@mia_bluebird).

English speech throughout: on-camera intro (IMG_9933, the 4K take; joi.mp4 is a
1080p duplicate) + eight voice notes laid over cat b-roll. Subtitles are the
spoken words with Whisper slips fixed ("relax nervy" -> "relax nearby"),
one line <= 32 chars. B-roll ranges avoid camera speech (Silero VAD) and
shots where Mia's face is on camera (face-crop sheets).
Writes artifacts/timeline.json and assets/analysis/subs_en.json.
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\fosfe\Downloads\Новая папка (16)")
BROLL = Path(r"C:\Users\fosfe\Downloads\тц")
GAP = 0.4
PIECE_GAP = 0.08
TOPIC_TAIL = 0.6
TALK_IN, TALK_OUT = 0.3, 0.45
MAX_CHARS = 32


def note(stamp):
    return f"audio_2026-10-19_12-{stamp}"


# Whisper mishears her accent a lot; subtitle text is what she actually says.
LINES = [  # (topic, voice note, [(a, b)], subtitle text)
    ("browse", "21-57", [(0.30, 29.20)],
     "When I'm shopping, I usually like to take my time and look through different sections before choosing "
     "anything. I don't always have a very specific idea of what I want. Sometimes I just walk around, look at "
     "the clothes and styles, and wait for something to catch my attention."),
    ("jeans", "22-21", [(0.25, 26.30)],  # take 2 (cleaner than 22-02)
     "The first thing I started looking at was jeans. I always think it's useful to have a few different styles, "
     "because jeans are so easy to wear with almost everything. I found a few pairs that I liked, so I decided "
     "to take them with me and see how they look on."),
    ("skirts", "22-26", [(0.25, 24.15)],
     "Then I moved on to skirts. I like skirts because they can completely change the feel of an outfit. "
     "A simple top can look totally different when you pair it with a cute skirt. So I always like seeing "
     "different shapes and styles."),
    ("tops", "22-30", [(0.55, 31.15)],
     "After that, I looked for some simple tops and shorts. I usually like having basic pieces in my wardrobe "
     "because they are easy to combine with everything else. But if I see something with an interesting "
     "detail, a cool color or a fun design, I'll definitely give it a try."),
    ("sweaters", "22-39", [(0.20, 25.80)],  # take 2 (22-34 has slips and a trailing "thank you")
     "And of course, I couldn't leave without looking at sweaters. I love cozy pieces, especially when they "
     "have something special about them, like a pretty color, an interesting pattern or a nice texture. "
     "They are the kind of things that can make a simple outfit feel much more put together."),
    ("fitting", "22-43", [(0.40, 40.00)],
     "Once I have a few things, I always like to take them to the fitting room. For me, this is the most "
     "important part of shopping, because something can look amazing on the hanger but feel completely "
     "different once you actually put it on. I usually look at the fit first, then the shape, and finally how "
     "I feel wearing it. If I feel comfortable and like the way I look, that's usually a very good sign."),
]

# b-roll avoids Silero-VAD speech in the camera audio (broll_speech.json) and the two
# portrait clips (2996, 3001). Skirt try-ons were already used in the skirts video -> kept short.
TOPICS = [  # (topic, section title or None, group, b-roll)
    ("browse", None, "main", [("IMG_2992", 0, 8.8), ("IMG_2993", 0, 3.9), ("IMG_2995", 0, 4.6), ("IMG_2997", 0, 4.0),
                              ("IMG_2999", 0, 7.2), ("IMG_3002", 0, 3.6), ("IMG_3003", 0, 5.6), ("IMG_3030", 0, 9.7),
                              ("IMG_3029", 0, 17.0)]),
    ("jeans", "Jeans", "main", [("IMG_3037", 0, 6.7), ("IMG_3048", 0, 8.8), ("IMG_3054", 0, 18.2),
                                ("IMG_3055", 5.8, 10.2), ("IMG_3055", 14.0, 19.7), ("IMG_3056", 0, 21.2)]),
    ("skirts", "Skirts", "main", [("IMG_3115", 0, 8.8), ("IMG_3083", 2.0, 21.0), ("IMG_3084", 0, 19.6),
                                  ("IMG_3086", 0, 6.8), ("IMG_3087", 1.6, 13.4)]),
    ("tops", "Tops & Shorts", "main", [("IMG_3034", 0, 7.3), ("IMG_3040", 0, 11.9), ("IMG_3063", 3.6, 9.3),
                                       ("IMG_3064", 0, 3.3), ("IMG_3064", 5.0, 16.9), ("IMG_3065", 0, 17.1),
                                       ("IMG_3036", 0, 4.7)]),
    ("sweaters", "Sweaters", "main", [("IMG_3033", 0, 23.5), ("IMG_3120", 0, 4.9), ("IMG_3114", 0, 12.6),
                                      ("IMG_3076", 0, 20.0), ("IMG_3066", 3.6, 17.9)]),
    ("fitting", "The Fitting Room", "main", [("IMG_3041", 0, 2.4), ("IMG_3042", 0, 5.4), ("IMG_3057", 0, 6.85), ("IMG_3057", 7.2, 21.6),  # 6.9-7.13 red flash (hand over lens)
                                             ("IMG_3067", 0, 9.1), ("IMG_3085", 5.2, 20.0)]),
]

# On-camera hello / goodbye: the user's horizontal re-export ыв.mp4 (2560x1440). Long silent gaps
# (31.7-36.3, 103.0-106.5) are cut; the second part of each gets a 1.08 punch-in to read as a cut.
YV = "yv"
INTRO_PARTS = [
    (YV, 0.48, 32.05, None, [
        (0.78, 3.52, "Hi everyone, welcome back to my channel."),
        (3.94, 13.88, "Today I'm taking you shopping with me and showing you how I usually choose clothes "
                      "when I go to a store."),
        (14.42, 20.06, "I'm always curious to see what catches my eye first,"),
        (20.48, 31.70, "because sometimes I go in looking for one specific thing and end up finding "
                       "something completely different."),
    ]),
    (YV, 35.95, 71.75, 1.08, [
        (36.30, 45.70, "Today I'm going to look at different pieces: jeans, T-shirts, skirts, shorts and sweaters."),
        (46.18, 65.78, "I'll show you what I notice when I'm choosing clothes, what makes me want to try "
                       "something on, and how I decide whether I actually like it once I see it on myself."),
        (66.22, 71.24, "So let's go shopping together and see what I find."),
    ]),
]
GOODBYE = [
    (YV, 74.50, 103.40, None, [
        (75.14, 85.86, "Of course, I can't take everything home with me, so the hardest part is always choosing "
                       "which pieces are really worth getting."),
        (86.40, 102.98, "I usually try to think about what I already have in my wardrobe, how many different "
                        "outfits I can create with the pieces and, most importantly, whether I'll actually wear it."),
    ]),
    (YV, 106.15, 120.70, 1.08, [
        (106.54, 113.66, "Thank you so much for shopping with me today. I hope you enjoyed coming around"),
        (114.06, 120.18, "and seeing how I choose my clothes. I'll see you in my next video. Bye!"),
    ]),
]
GOODBYE_ONLYFANS = 115.2  # no OnlyFans line -> tag over the goodbye
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


def main():
    raw = json.load(open(PROJ / "assets/analysis/vo_words.json", encoding="utf-8"))
    tr = {note(k[-5:].replace("_", "-")): v for k, v in raw.items()}  # audio_2026_10_19_12_21_57 -> note("21-57")
    video, vo, sections, subs = [], [], [], {}
    for clip, a, b, zoom, sents in INTRO_PARTS:
        it = {"group": "intro", "src": clip, "in": a, "out": b, "speech": True}
        if zoom:
            it["zoom"] = zoom
        video.append(it)
        subs.setdefault(clip, []).extend(c for x, y, t in sents for c in timed_cues(t, [(x, y)]))
    video[-1]["pad_tail"] = 0.3
    n = 0
    for topic, title, group, clips in TOPICS:
        lines = [ln for ln in LINES if ln[0] == topic]
        plan = [pieces(SRC / f"{note(st)}.ogg", r) for _, st, r, _ in lines]
        lead = 0.7 if group == "outro" else 0.5
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
        for (_, st, _, text), p in zip(lines, plan):
            key = "vo_" + st
            for s, e in p:
                vo.append({"src": key, "in": s, "out": e, "item": first, "offset": round(t, 3)})
                t += (e - s) + PIECE_GAP
            t += GAP - PIECE_GAP
            subs.setdefault(key, []).extend(timed_cues(text, p, tr[note(st)]))
        if title:
            n += 1
            sections.append({"index": n, "label": "Part", "title": title, "item": first,
                             "offset": 0.6 if group == "outro" else 0.15})
    sections.append({"index": n + 1, "label": "Part", "title": "Final Thoughts", "item": len(video), "offset": 0.7})
    for clip, a, b, zoom, sents in GOODBYE:
        it = {"group": "outro", "src": clip, "in": a, "out": b, "speech": True}
        if zoom:
            it["zoom"] = zoom
        video.append(it)
        subs.setdefault(clip, []).extend(c for x, y, t in sents for c in timed_cues(t, [(x, y)]))
    last = len(video) - 1
    video[last]["pad_tail"] = 0.8
    rep = ([{"item": last, "offset": round(GOODBYE_ONLYFANS - video[last]["in"], 3)}] if GOODBYE_ONLYFANS
           else [{"item": last, "offset": max(0.0, round(video[last]["out"] - video[last]["in"] - 5.0, 3))}])

    srcs = {v["src"] for v in video}
    def find(c):
        if c == YV:
            return "C:/Users/fosfe/Downloads/ыв.mp4"
        for d in (SRC, BROLL):
            hit = list(d.glob(f"{c}.*"))
            if hit:
                return str(hit[0]).replace("\\", "/")
        raise FileNotFoundError(c)
    tl = {
        "tag": "@sandra_blake",
        "tag_at": 0.8,
        "tag_repeats": rep,
        "music": ["C:/Users/fosfe/Downloads/эмил/Lazy Walk - Cheel.mp3",
                  "C:/Users/fosfe/Downloads/юбка/Cooked - Dyalla (1) (1).mp3"],
        "sources": {**{c: find(c) for c in srcs},
                    **{"vo_" + st: str(SRC / f"{note(st)}.ogg").replace("\\", "/") for _, st, _, _ in LINES}},
        "transcript_keys": {**{c: c for c in srcs}, **{"vo_" + st: note(st) for _, st, _, _ in LINES}},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": {},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False),
                                                       encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    print(f"items={len(video)} vo_pieces={len(vo)} sections={[s['title'] for s in sections]} "
          f"~duration={tot:.1f}s longest_cue={len(longest[2])} '{longest[2]}'")


if __name__ == "__main__":
    main()



