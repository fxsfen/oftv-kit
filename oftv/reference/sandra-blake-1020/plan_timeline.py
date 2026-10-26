"""Timeline for Sandra's microwave potato recipe (@sandra_blake).

Her talking clips were vertical (720x1280); the user re-made them as one 2560x1440 file with her cut out on a
background (Downloads/fix.mp4): intro 0-19 s, "such an easy recipe" with the dish 22-42 s, OnlyFans line 42.5-56.5.
Main: the Telegram voice notes (English) over the landscape cooking clips. Dropped: note 21-28-13 (a stage
direction read aloud: "Sandra waits in the kitchen..."), 21-29-18 (first take of 21-29-22), clip 5122 (oil bottle
label close-up) and the first seconds of 5112 (seasoning pack held to camera) - product placement.
"""
import json
import re
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
SRC = "C:/Users/fosfe/Downloads/монтаж пн/sandra_blake"
FIX = "C:/Users/fosfe/Downloads/fix.mp4"
MUSIC = ["C:/Users/fosfe/Downloads/монтаж пн/music/Sound Of Freedom - Chil Hip-Hop Beat .mp3.mp3",
         "C:/Users/fosfe/Downloads/монтаж пн/music/Sound Of Freedom - Lo-Fi R&B Vibe.mp3.mp3"]
NOTE_GAP, TOPIC_TAIL, MAXC = 0.5, 0.7, 32
N = "audio_2026-10-20_21-"

WORDS = json.load(open(A / "transcripts.json", encoding="utf-8"))
TEXT_EDITS = [(r"\bthe the\b", "the")]
# (title, voice notes, b-roll [(clip, in, out)])
TOPICS = [
    ("Prep the Potatoes", ["27-52"], [("IMG_5112", 6.0, 14.6), ("IMG_5113", 2.0, 78.0), ("IMG_5114", 1.0, 25.0),
                                      ("IMG_5115", 2.0, 62.0)]),
    ("Season & Oil", ["27-59"], [("IMG_5119", 2.0, 74.0)]),
    ("Microwave Time", ["28-06"], [("IMG_5123", 1.0, 11.5), ("IMG_5124", 0.5, 9.5)]),
    ("Fresh Dill", ["28-53", "28-57", "29-03"], [("IMG_5127", 1.0, 29.5), ("IMG_5150", 0.5, 9.5),
                                                ("IMG_5151", 1.0, 14.2), ("IMG_5152", 0.0, 2.0), ("IMG_5153", 0.0, 7.2)]),
    ("Cheesy Finish", ["29-09", "29-13", "29-22"], [("IMG_5150", 10.0, 24.4), ("IMG_5154", 1.0, 24.0),
                                                    ("IMG_5155", 0.3, 8.2)]),
]
STOP = {"the", "a", "an", "to", "my", "and", "of", "your", "for", "in", "on", "with", "but", "so", "that", "i'm",
        "how", "it's", "if", "is", "are", "i", "can", "you", "this", "these", "make", "just", "little", "few", "which",
        "when", "what", "be", "very", "such", "it", "some", "i'll", "let's"}

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
        t = re.sub(a, b, t)
    return t


def cues(words):
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
            if j < n and (last in STOP or last.isdigit()):
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


def main():
    video, vo, sections, subs = [], [], [], {"fix": []}

    def fix_item(group, a, b, zoom=1.0, pad_tail=0.0, snap_out=True):
        a = quietest("fix", a, -0.1, 0.1)
        b = quietest("fix", b, -0.1, 0.12) if snap_out else b
        it = {"group": group, "src": "fix", "in": a, "out": b, "speech": True}
        if zoom != 1.0:
            it["zoom"] = zoom
        if pad_tail:
            it["pad_tail"] = pad_tail
        video.append(it)
        subs["fix"] += cues([w for w in WORDS["fix"] if a - 0.05 <= w[0] < b - 0.05])

    fix_item("intro", 0.0, 18.9, pad_tail=0.6, snap_out=False)  # stray "pan" sound at 18.9-19.2 left out
    for n, (title, notes, clips) in enumerate(TOPICS, 1):
        keys = [N + x for x in notes]
        pieces = [(quietest(k, max(0, WORDS[k][0][0] - 0.12), -0.1, 0.05), quietest(k, WORDS[k][-1][1] + 0.1, -0.05, 0.2))
                  for k in keys]
        need = 0.5 + sum(e - s for s, e in pieces) + NOTE_GAP * (len(pieces) - 1) + TOPIC_TAIL
        avail = sum(o - i for _, i, o in clips)
        k = need / avail
        print(f"{title}: vo {need:.1f}s of {avail:.1f}s b-roll (k={k:.2f})")
        assert k <= 1, title
        first = len(video)
        for c, i, o in clips:
            use = (o - i) * k
            mid = i + (o - i) / 2
            video.append({"group": "main", "src": c, "in": round(mid - use / 2, 3), "out": round(mid + use / 2, 3)})
        t = 0.5
        for key, (s, e) in zip(keys, pieces):
            vo.append({"src": key, "in": s, "out": e, "item": first, "offset": round(t, 3)})
            subs[key] = cues([w for w in WORDS[key] if s - 0.05 <= w[0] < e])
            t += (e - s) + NOTE_GAP
        sections.append({"index": n, "label": "Step", "title": title, "item": first, "offset": 0.15})
    # taste test + OnlyFans line from fix.mp4; the doubled "life life" (45.96-46.16) is cut with a punch-in
    sections.append({"index": len(TOPICS) + 1, "label": "Step", "title": "Taste Test", "item": len(video),
                     "offset": 0.4})
    fix_item("outro", 22.0, 41.6)
    fix_item("outro", 42.2, 45.96)
    fix_item("outro", 46.16, 56.4, zoom=1.08)
    of = [w for w in WORDS["fix"] if "OnlyFans" in w[2] and w[0] > 40]
    of_at = of[0][0] - video[-1]["in"]

    (A / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    srcs = {k: f"{SRC}/{k}.MOV" for k in {v["src"] for v in video} if k != "fix"}
    srcs["fix"] = FIX
    srcs.update({k: f"{SRC}/{k}.ogg" for k in {v["src"] for v in vo}})
    tl = {
        "tag": "@sandra_blake",
        "tag_at": 0.8,
        "tag_repeats": [{"item": len(video) - 1, "offset": round(of_at, 2), "note": "subscribe to my OnlyFans"}],
        "music": MUSIC,
        "sources": srcs,
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} vo={len(vo)} ~duration={tot:.1f}s")
    for k, cs in subs.items():
        print(k[-5:], " | ".join(c[2] for c in cs))
    print("long cues:", [c[2] for v in subs.values() for c in v if len(c[2]) > MAXC])


if __name__ == "__main__":
    main()
