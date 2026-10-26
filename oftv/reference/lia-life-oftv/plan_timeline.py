"""Timeline for Lia's Halloween bunny makeup video (@lia_life).

Intro: IMG_9856 (talking to camera). Main: five phone voice notes (IMG_9892..9896, camera pointed at the
ceiling -> audio only), cut into sentences and laid over the silent makeup b-roll (IMG_9858..9865; Silero VAD
finds no speech in any of them, face-crop sheets every 3 s show no talking). Outro: the final-look voice note
over the costume footage, then IMG_9883 (goodbye, mentions OnlyFans -> second tag plate).
"""
import json
import re
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
SRC = "C:/Users/fosfe/Downloads/лия"
GAP = 0.4          # pause between VO sentences
TOPIC_TAIL = 0.7   # b-roll after the last sentence of a topic
MAXC = 32          # one-line subtitles



def norm_words(ws):
    """Strip spaces; glue "-like"/"-TV" onto the previous word and "only"+"fans" into one token."""
    out = []
    for s, e, w in ws:
        w = w.strip()
        if out and (w.startswith("-") or (out[-1][2].lower() == "only" and w.lower().startswith("fans"))):
            out[-1] = [out[-1][0], e, out[-1][2] + ("" if w.startswith("-") else " ") + w]
        else:
            out.append([s, e, w])
    return out


WORDS = {k: norm_words(v) for k, v in json.load(open(A / "transcripts.json", encoding="utf-8")).items()}
WORDS["IMG_9883"] = [[s, e, {"only fans": "OnlyFans.", "hope": "Hope", "bye": "bye!"}.get(w.lower(), w)]
                     for s, e, w in WORDS["IMG_9883"]]

# Whisper -> what she actually says / house spelling
TEXT_EDITS = [(r"\boff[- ]?TV\b", "OFTV"), (r"\bonly ?fans\b", "OnlyFans"), (r"\bLeah\b", "Lia"),
              (r"recreate it home", "recreate at home"), (r"\bthis few minutes", "these few minutes"),
              (r"\bI Hope\b", "I hope")]

TOPICS = [  # (voice note, section title, group, b-roll ranges (src, in, out))
    ("IMG_9892", "The Bunny Idea", "main",
     [("IMG_9858", 0.3, 3.6), ("IMG_9861", 0.3, 9.0), ("IMG_9860", 21.0, 27.5), ("IMG_9862", 19.0, 26.5)]),
    ("IMG_9893", "Feline Eyes", "main",
     [("IMG_9858", 4.0, 28.0), ("IMG_9859", 2.0, 21.0), ("IMG_9860", 0.5, 20.0), ("IMG_9861", 9.0, 30.0),
      ("IMG_9861", 33.0, 50.0), ("IMG_9862", 0.5, 18.0)]),
    ("IMG_9894", "Nose & Whiskers", "main", [("IMG_9863", 0.5, 56.0), ("IMG_9864", 0.5, 20.0)]),
    ("IMG_9895", "The Ears", "main", [("IMG_9865", 2.0, 30.0), ("IMG_9865", 38.0, 61.0), ("IMG_9865", 66.0, 100.0)]),
    ("IMG_9896", "The Final Look", "outro", [("IMG_9865", 89.0, 102.3), ("IMG_9865", 104.8, 110.5),
                                             ("IMG_9865", 114.0, 125.0)]),
]
INTRO, OUTRO = "IMG_9856", "IMG_9883"
STOP = {"the", "a", "an", "to", "my", "and", "of", "your", "for", "in", "on", "with", "but", "so", "that", "i'm",
        "how", "it's", "if", "is", "are", "i", "can", "you", "this", "these", "make", "just", "little", "few"}


def energy(key):
    w = wave.open(str(A / "wav16" / f"{key}.wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(w.getframerate() * 0.02)
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


E = {}


def quietest(key, t, lo, hi):
    if key not in E:
        E[key] = energy(key)
    r = E[key]
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(r) - 1, int((t + hi) / 0.02))
    return round((i0 + int(np.argmin(r[i0:i1 + 1]))) * 0.02, 3)


def clean(t):
    for a, b in TEXT_EDITS:
        t = re.sub(a, b, t, flags=re.I)
    return t


def sentences(key):
    """Word list -> sentences [(start, end, [words])], split at . ! ?"""
    out, cur = [], []
    for s, e, w in WORDS[key]:
        cur.append([s, e, w.strip()])
        if re.search(r"[.!?]$", w.strip()):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def cues(words):
    """One-line cues (<= MAXC chars) via DP: balanced lengths, prefer punctuation, never end on a stop word."""
    toks = [w[2] for w in words]
    n = len(toks)
    best = [(0.0, -1)] + [(1e9, -1)] * n
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            txt = clean(" ".join(toks[i:j]))
            if len(txt) > MAXC and j - i > 1:
                break
            last = toks[j - 1].lower().strip(",.!?")
            cost = (len(txt) - 24) ** 2 / 50 + 3
            if j < n and last in STOP:
                cost += 40
            if j < n and toks[j - 1][-1] in ",.!?":
                cost -= 4
            if re.search(r"[.!?] ", txt):  # never run two sentences into one cue
                cost += 25
            if len(txt) < 10 and n > 1:
                cost += 15
            if best[i][0] + cost < best[j][0]:
                best[j] = (best[i][0] + cost, i)
    seg, j = [], n
    while j > 0:
        i = best[j][1]
        seg.append((i, j))
        j = i
    return [[words[i][0], words[j - 1][1], clean(" ".join(toks[i:j]))] for i, j in reversed(seg)]


def talk_item(key, group, pad_tail=0.0, pad_head=0.0, stop_at=None):
    ws = [w for w in WORDS[key] if stop_at is None or w[0] < stop_at]
    a = quietest(key, max(0.0, ws[0][0] - 0.3), -0.1, 0.1)
    b = quietest(key, ws[-1][1] + 0.4, -0.15, 0.15)
    it = {"group": group, "src": key, "in": a, "out": b, "speech": True}
    if pad_tail:
        it["pad_tail"] = pad_tail
    if pad_head:
        it["pad_head"] = pad_head
    return it, cues(ws)


def main():
    video, vo, sections, subs = [], [], [], {}
    it, c = talk_item(INTRO, "intro", pad_tail=0.6)
    video.append(it)
    subs[INTRO] = c
    n = 0
    for key, title, group, clips in TOPICS:
        sents = sentences(key)
        pieces = [(quietest(key, s[0][0], -0.15, 0.04), quietest(key, s[-1][1], -0.04, 0.2)) for s in sents]
        lead = 0.7 if group == "outro" else 0.5
        need = lead + sum(e - s for s, e in pieces) + GAP * (len(pieces) - 1) + TOPIC_TAIL
        avail = sum(o - i for _, i, o in clips)
        k = need / avail
        assert k <= 1, (key, need, avail)
        first = len(video)
        for src, i, o in clips:
            length = (o - i) * k
            mid = i + (o - i) / 2
            video.append({"group": group, "src": src, "in": round(mid - length / 2, 3),
                          "out": round(mid + length / 2, 3)})
        t = lead
        subs[key] = []
        for (s, e), sent in zip(pieces, sents):
            vo.append({"src": key, "in": s, "out": e, "item": first, "offset": round(t, 3)})
            subs[key] += cues(sent)
            t += (e - s) + GAP
        n += 1
        sections.append({"index": n, "label": "Part", "title": title, "item": first, "offset": 0.15})
        print(f"{key} {title}: vo {need:.1f}s of {avail:.1f}s b-roll (k={k:.2f})")
    it, c = talk_item(OUTRO, "outro")
    video.append(it)
    subs[OUTRO] = c
    of = [w for w in WORDS[OUTRO] if re.search(r"only|fans", w[2], re.I)]
    of_at = of[-1][0] - it["in"]  # "find me on my OnlyFans", not the "your OnlyFans model" intro line

    (A / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tl = {
        "tag": "@lia_life",
        "tag_at": 0.8,
        "tag_repeats": [{"item": len(video) - 1, "offset": round(of_at, 2), "note": "'you can find me on my OnlyFans'"}],
        "music": [f"{SRC}/Soundore - Halloween.mp3", f"{SRC}/HoliznaPATREON - halloween.mp3"],
        "sources": {k: f"{SRC}/{k}.MOV" for k in
                    {INTRO, OUTRO, *[t[0] for t in TOPICS], *[c[0] for t in TOPICS for c in t[3]]}},
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) + v.get("pad_head", 0) for v in video) - 1.0
    print(f"items={len(video)} vo_pieces={len(vo)} ~duration={tot:.1f}s")
    for k, cs in subs.items():
        print(k, " | ".join(c[2] for c in cs))
    print("long cues:", [c[2] for v in subs.values() for c in v if len(c[2]) > MAXC])


if __name__ == "__main__":
    main()
