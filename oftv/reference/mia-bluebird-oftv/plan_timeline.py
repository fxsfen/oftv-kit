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
SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name.startswith("Лине")][0]
GAP = 0.4
PIECE_GAP = 0.08
TOPIC_TAIL = 0.6
TALK_IN, TALK_OUT = 0.3, 0.45
MAX_CHARS = 32


def note(stamp):
    return f"audio_2026-10-17_20-05-{stamp}"


LINES = [  # (topic, voice note, [(a, b), ...], subtitle text)
    # 9.88-10.20 is a quiet first "Pookie" (doubled once levelled up) and 16.32-16.60 a doubled "to"
    # ("hard to to ignore") — both spliced out
    ("meet", "21", [(0.50, 9.52), (10.40, 16.32), (16.60, 17.20)],
     "First of all, just look at those beautiful blue eyes. One of the things I love most about Siamese cats "
     "is their unique appearance. Pookie has such a pretty face, soft fur and those gorgeous blue eyes "
     "that are hard to ignore."),
    ("meet", "26", [(0.80, 13.50)],
     "But of course, she's much more than just a pretty face. Every cat has her own personality, and getting "
     "to know Pookie has been such a lovely experience. I'm always discovering something new about her."),
    ("ways", "30", [(0.00, 24.60)],
     "Pookie has her own little ways of getting my attention, and I love watching her reactions to different "
     "things. Sometimes she wants to play, sometimes she wants to explore, and sometimes she just wants to "
     "relax nearby. I think that's what makes getting to know a pet so special. You start to understand her "
     "little habits and preferences."),
    ("fav", "34", [(0.30, 15.50)],
     "So now let's talk about some of Pookie's favorite things. I think every cat has her own little world of "
     "things she enjoys, whether it's a particular toy or a cozy place to sleep, or simply spending time near "
     "someone she trusts."),
    ("fav", "37", [(0.00, 17.00)],
     "I like spending time playing with her because it gives us a chance to bond, and when she's ready to rest, "
     "I let her enjoy her quiet time. I think it's important to respect a cat's personality and let her decide "
     "when she wants attention."),
    ("simple", "42", [(0.00, 8.50)],
     "And honestly, sometimes the simplest moments are the best. Having her sit beside me while I relax at home "
     "is already enough to make me smile."),
    ("simple", "46", [(0.40, 17.65)],
     "Having Pookie around me makes my everyday life feel a little more special. Even when I'm busy with work or "
     "just relaxing at home, it's lovely to have a little companion nearby. She reminds me to slow down "
     "sometimes and enjoy the simple things."),
    ("care", "50", [(0.00, 7.46)],
     "And of course, having a pet also means being responsible. I always want her to feel safe, comfortable "
     "and loved."),
    # 7.6-8.1 is a whispered first "for" ("for... for me") that becomes audible once levelled — start at the clean one
    ("final", "50", [(8.12, 16.05)],
     "For me, the best part of having Pookie in my life is building that special bond and learning more about "
     "her every day."),
]

TOPICS = [  # (topic, section title, group, b-roll (clip, in, out))
    ("meet", "Meet Pookie", "main", [("IMG_9971", 0.0, 13.0), ("IMG_9972", 0.0, 28.0), ("IMG_9976", 5.0, 10.5),
                                    ("IMG_9965", 4.0, 20.0)]),
    ("ways", "Her Little Ways", "main", [("IMG_9963", 0.0, 11.0), ("IMG_9970", 4.2, 9.4), ("IMG_9983", 0.0, 11.6),
                                         ("IMG_9985", 0.0, 12.6), ("IMG_9986", 0.0, 14.0), ("IMG_9978", 0.0, 3.4)]),
    ("fav", "Favorite Things", "main", [("IMG_9964", 0.0, 54.0), ("IMG_9968", 0.0, 34.0), ("IMG_9973", 0.0, 15.0),
                                        ("IMG_9974", 0.0, 6.3), ("IMG_9977", 0.0, 9.6), ("IMG_9980", 0.0, 20.0)]),
    ("simple", "Simple Moments", "main", [("IMG_9982", 0.0, 39.0), ("IMG_9987", 0.0, 17.0), ("IMG_9987", 18.0, 35.0),
                                          ("IMG_9989", 94.5, 100.0)]),
    ("care", "Taking Care of Her", "main", [("IMG_9960", 0.0, 12.9), ("IMG_9961", 0.0, 17.8), ("IMG_9962", 0.0, 4.1),
                                            ("IMG_9966", 0.0, 26.7), ("IMG_9969", 0.0, 14.8)]),
    # outro: cat portraits only (no Mia face on camera under the voice)
    ("final", "Final Thoughts", "outro", [("IMG_9972", 28.0, 43.0), ("IMG_9975", 0.0, 5.1), ("IMG_9965", 20.0, 27.0)]),
]

# On-camera goodbye (joipoka.mp4, added later): the three clean takes; the false start (1.3-1.9),
# the broken OnlyFans takes (31.7-61.1) are dropped. Take 3 runs on into the cat kiss (silent) as the ending.
GOODBYE = [
    ("joipoka", 2.85, 19.60, None, [
        (3.15, 5.90, "And that's my little introduction to Pookie."),
        (6.54, 11.80, "She's not just my beautiful Siamese cat, she's a special part of my everyday life."),
        (12.00, 15.24, "From her gorgeous blue eyes to her curious personality,"),
        (15.76, 19.18, "there are so many little things about her that I love."),
    ]),
    ("joipoka", 21.10, 31.70, 1.08, [  # punch-in so the jump cut between takes reads as a cut
        (21.46, 24.52, "I hope you enjoyed getting to know us a little better."),
        (24.30, 28.00, "So I am so happy I could introduce you to Pookie"),
        (28.10, 31.70, "and share a few moments from our life together."),
    ]),
    ("joipoka", 62.75, 88.00, None, [
        (62.90, 69.80, "If you would like to see more of my personal life and get to know me better, "
                       "you can subscribe to my OnlyFans."),
        (70.64, 74.30, "So thank you for spending this time with us, take care,"),
        (74.40, 77.60, "and I will see you in my next OFTV video."),
        (77.98, 79.04, "Bye everyone!"),
    ]),
]
GOODBYE_ONLYFANS = 69.30

INTRO = ("IMG_9933", 0.18, 12.96, [
    (0.00, 2.78, "Hi everyone, welcome back to my OFTV blog."),
    (3.00, 7.50, "My name is Mia, I'm an OnlyFans model and OFTV creator."),
    (8.00, 12.96, "And today I have a little special introduction for you."),
])

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
    tr = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
    video, vo, sections, subs = [], [], [], {}
    clip, s_in, s_out, sents = INTRO
    video.append({"group": "intro", "src": clip, "in": round(max(0.0, s_in - TALK_IN), 3),
                  "out": round(s_out + TALK_OUT, 3), "speech": True, "pad_tail": 0.4})
    subs[clip] = [c for a, b, t in sents for c in timed_cues(t, [(a, b)], tr[clip])]
    for n, (topic, title, group, clips) in enumerate(TOPICS, 1):
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
        sections.append({"index": n, "label": "Part", "title": title, "item": first,
                         "offset": 0.6 if group == "outro" else 0.15})
    subs["joipoka"] = []
    for clip, a, b, zoom, sents in GOODBYE:
        it = {"group": "outro", "src": clip, "in": a, "out": b, "speech": True}
        if zoom:
            it["zoom"] = zoom
        video.append(it)
        subs[clip] += [c for x, y, t in sents for c in timed_cues(t, [(x, y)])]
    last = len(video) - 1
    video[last]["pad_tail"] = 0.8  # let the music breathe after the cat kiss

    srcs = {v["src"] for v in video}
    tl = {
        "tag": "@mia_bluebird",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": round(GOODBYE_ONLYFANS - video[last]["in"], 3),
                         "note": "'you can subscribe to my OnlyFans'"}],
        "music": [str(SRC / "Never Play - Jeremy Blake.mp3").replace("\\", "/"),
                  str(SRC / "Lawrence - TrackTribe.mp3").replace("\\", "/")],
        "sources": {**{c: str(next(SRC.glob(f"{c}.*"))).replace("\\", "/") for c in srcs},
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
