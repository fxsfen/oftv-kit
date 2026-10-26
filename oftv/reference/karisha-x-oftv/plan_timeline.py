"""Timeline for Karisha's fall lookbook (@karisha.x).

Intro: MVI_2042 + MVI_2046 (to camera). Main: three outfits, each = the best sentences of its voice note
(vo5/6/7 = "Pekara Branković 5/6/7.m4a") over the silent try-on clips of that outfit. The voice notes are
~4:15 against ~2:25 of b-roll, so (1) the b-roll runs at 0.833x (stretch 1.2: every 25 fps source frame
lands on one 30 fps frame, no duplicated frames) and (2) only the key sentences are kept (cut: detachable
collar, "best part", shirt under the sweater, coffee date, conclusions, shoes we never see).
Outro: MVI_2084 (to camera, mentions OnlyFans -> second tag plate).
"""
import json
import re
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
SRC = "C:/Users/fosfe/Downloads/монтаж пн/karisha.x"
MUSIC = ["C:/Users/fosfe/Downloads/монтаж пн/music/Cooked - Dyalla (1) (1).mp3",  # 3:20 < 4:00 video ->
         "C:/Users/fosfe/Downloads/монтаж пн/music/SyncLab Music - Independence Day.mp3"]  # chained (6 s xfade)
GAP, TOPIC_TAIL, STRETCH, MAXC = 0.4, 0.7, 1.2, 32



def norm_words(ws):
    """'sub up' -> 'subscribe', 'only'+'fans' -> 'OnlyFans' (one token, so a cue never splits it)."""
    out = []
    for s, e, w in ws:
        w = w.strip()
        prev = out[-1][2].lower() if out else ""
        if prev == "sub" and w.lower() == "up":
            out[-1] = [out[-1][0], e, "subscribe"]
        elif prev == "only" and w.lower().startswith("fans"):
            out[-1] = [out[-1][0], e, "OnlyFans" + w[4:]]
        else:
            out.append([s, e, w])
    return out


WORDS = {k: norm_words(v) for k, v in json.load(open(A / "transcripts.json", encoding="utf-8")).items()}
TEXT_EDITS = [(r"\bOPTV\b", "OFTV"), (r"\bcups\b", "cuffs"), (r"\bsub up to my only fans\b", "subscribe to my OnlyFans"),
              (r"\bonly fans\b", "OnlyFans"), (r"\bi\b", "I"), (r"\bi'm\b", "I'm"), (r"\bi'd\b", "I'd"),
              (r"\bgiving a little bit of the Wednesday vibes\b", "giving a little bit of Wednesday vibes"),
              (r"\bwhat i will be able\b", "that I will be able"), (r"\bfor you three outfits\b", "three outfits for you")]

# (title, voice note, VO pieces (approx source in/out, snapped to the quietest 20 ms), b-roll clips in order)
TOPICS = [
    ("The Black Dress", "vo5", [(0.4, 11.4), (11.5, 24.0), (24.05, 35.2), (50.0, 60.1), (60.4, 65.3)],
     ["MVI_2051", "MVI_2053", "MVI_2054", "MVI_2058", "MVI_2052", "MVI_2059", "MVI_2060", "MVI_2048"]),
    ("Red & White", "vo6", [(0.2, 11.4), (26.3, 38.95), (63.6, 74.7)],
     ["MVI_2061", "MVI_2068", "MVI_2067", "MVI_2069", "MVI_2062", "MVI_2070", "MVI_2066"]),
    ("Casual Denim", "vo7", [(0.0, 10.95), (11.0, 23.15), (23.2, 36.0), (36.6, 46.9), (74.6, 82.4)],
     ["MVI_2072", "MVI_2073", "MVI_2074", "MVI_2075", "MVI_2076", "MVI_2078", "MVI_2079", "MVI_2080", "MVI_2081"]),
]
STOP = {"the", "a", "an", "to", "my", "and", "of", "your", "for", "in", "on", "with", "but", "so", "that", "i'm",
        "how", "it's", "if", "is", "are", "i", "can", "you", "this", "these", "make", "just", "little", "few", "which",
        "when", "what", "be", "very", "such", "it"}


def dur(stem):
    w = wave.open(str(A / "wav16" / f"{stem}.wav"))
    return w.getnframes() / w.getframerate()


E = {}


def quietest(key, t, lo, hi):
    if key not in E:
        w = wave.open(str(A / "wav16" / f"{key}.wav"))
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        hop = int(w.getframerate() * 0.02)
        n = len(x) // hop
        E[key] = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    r = E[key]
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(r) - 1, int((t + hi) / 0.02))
    return round((i0 + int(np.argmin(r[i0:i1 + 1]))) * 0.02, 3)


def clean(t):
    t = re.sub(r"\s+", " ", t).strip()
    for a, b in TEXT_EDITS:
        t = re.sub(a, b, t, flags=re.I)
    return t[:1].upper() + t[1:]


def cues(words):
    """One-line cues (<= MAXC chars) via DP: balanced lengths, prefer punctuation, never end on a stop word."""
    toks = [w[2].strip() for w in words]
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
            if re.search(r"[.!?] ", txt):
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


def words_in(key, a, b):
    return [w for w in WORDS[key] if w[0] >= a - 0.05 and w[0] < b]


def main():
    video, vo, sections, subs = [], [], [], {}

    def talk(key, group, pad_tail=0.0):
        ws = WORDS[key]
        a = quietest(key, max(0.0, ws[0][0] - 0.3), -0.1, 0.1)
        # Whisper ends the last word early ("outfits" ran to 14.0 s, scored 13.3): end = last loud 20 ms
        # frame within 1.5 s after the last word + 0.3 s (the whole clip for the goodbye)
        quietest(key, 0.0, 0.0, 0.0)  # loads the energy curve into E
        r = E[key]
        i0 = int(ws[-1][1] / 0.02)
        loud = [i for i in range(i0, min(len(r), i0 + 75)) if r[i] > -40]
        end = (loud[-1] * 0.02 if loud else ws[-1][1]) + 0.3
        b = round(min(end, dur(key) - 0.1) if group != "outro" else dur(key) - 0.1, 3)
        it = {"group": group, "src": key, "in": a, "out": b, "speech": True}
        if pad_tail:
            it["pad_tail"] = pad_tail
        video.append(it)
        subs[key] = cues(ws)

    talk("MVI_2042", "intro")
    talk("MVI_2046", "intro", pad_tail=0.6)
    for n, (title, key, pieces, clips) in enumerate(TOPICS, 1):
        pieces = [(quietest(key, a, -0.12, 0.08), quietest(key, b, -0.08, 0.15)) for a, b in pieces]
        need = 0.5 + sum(e - s for s, e in pieces) + GAP * (len(pieces) - 1) + TOPIC_TAIL
        lens = [dur(c) - 0.15 for c in clips]
        avail = sum(lens) * STRETCH
        k = need / avail
        print(f"{title}: vo {need:.1f}s of {avail:.1f}s slow b-roll (k={k:.2f})")
        assert k <= 1, title
        first = len(video)
        for c, L in zip(clips, lens):
            use = L * k
            mid = 0.05 + L / 2
            video.append({"group": "main", "src": c, "in": round(mid - use / 2, 3), "out": round(mid + use / 2, 3),
                          "stretch": STRETCH})
        t = 0.5
        subs[key] = []
        for s, e in pieces:
            vo.append({"src": key, "in": s, "out": e, "item": first, "offset": round(t, 3)})
            subs[key] += cues(words_in(key, s, e))
            t += (e - s) + GAP
        sections.append({"index": n, "label": "Look", "title": title, "item": first, "offset": 0.15})
    talk("MVI_2084", "outro")
    of = [w for w in WORDS["MVI_2084"] if re.search(r"only|fans", w[2], re.I)]
    of_at = of[0][0] - video[-1]["in"]

    (A / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tl = {
        "tag": "@karisha.x",
        "tag_at": 0.8,
        "tag_repeats": [{"item": len(video) - 1, "offset": round(of_at, 2), "note": "subscribe to my OnlyFans"}],
        "music": MUSIC,
        "sources": {**{f"MVI_{c[4:]}": f"{SRC}/{c}.MP4" for t in TOPICS for c in t[3]},
                    **{k: f"{SRC}/{k}.MP4" for k in ("MVI_2042", "MVI_2046", "MVI_2084")},
                    # original m4a voice notes (file names are NFD-normalised, so look them up by suffix)
                    **{f"vo{i}": [p.as_posix() for p in Path(SRC).iterdir() if p.suffix == ".m4a" and p.stem.endswith(f" {i}")][0]
                       for i in (5, 6, 7)}},
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum((v["out"] - v["in"]) * v.get("stretch", 1) + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} vo={len(vo)} ~duration={tot:.1f}s")
    for k, cs in subs.items():
        print(k, " | ".join(c[2] for c in cs))
    print("long cues:", [c[2] for v in subs.values() for c in v if len(c[2]) > MAXC])


if __name__ == "__main__":
    main()
