"""Timeline for Masha's "what I do when I'm bored" vlog (@masha_masha_mashenkaa).

Intro: IMG_9627 (to camera). Main: 19 Telegram voice notes (one clean take each) grouped into 9 ideas, each
over 3-7 silent clips of that activity (all clips are landscape after their rotation flag; the phone-screen
clip IMG_9631 with Apple marketing text, the empty bed 9634 and the selfie/talking-looking 9641/9670 are
skipped). The two wrap-up notes (21-34-06/10) repeat what she says on camera in IMG_9682, so they are cut.
Outro: IMG_9682 + IMG_9683 (to camera, OnlyFans -> second tag plate).
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
SRC = "C:/Users/fosfe/Downloads/монтаж пн/masha_masha_mashenkaa"
MUSIC = ["C:/Users/fosfe/Downloads/монтаж пн/music/Lazy Walk - Cheel.mp3",
         "C:/Users/fosfe/Downloads/монтаж пн/music/Sound Of Freedom - Lo-Fi R&B Vibe.mp3.mp3"]
GAP, NOTE_GAP, TOPIC_TAIL, MAXC = 0.35, 0.5, 0.7, 32

WORDS = json.load(open(A / "transcripts.json", encoding="utf-8"))
TEXT_EDITS = [(r"\bIFTV\b", "OFTV")]
N = "audio_2026-10-20_21-"
TOPICS = [
    ("Put the Phone Down", ["32-45", "32-51"], ["9628", "9629", "9636", "9639"]),
    ("Music On", ["32-56", "33-00"], ["9637", "9635", "9632", "9633"]),
    ("A Little Break", ["33-05", "33-09"], ["9642", "9643", "9644", "9645", "9672"]),
    ("Self-Care", ["33-13", "33-17"], ["9646", "9647", "9648", "9673", "9649", "9650"]),
    ("Move a Little", ["33-22", "33-25"], ["9651", "9652", "9653", "9654", "9655", "9656", "9674"]),
    ("Get Creative", ["33-30", "33-34"], ["9657", "9658", "9659", "9660", "9661", "9675", "9678", "9680", "9681"]),
    ("Something New", ["33-39", "33-43", "33-47"], ["9662", "9663", "9664", "9665", "9676"]),
    ("Slow Down", ["33-51", "33-54"], ["9666", "9667", "9668", "9677", "9669"]),
    ("Go Outside", ["33-59", "34-03"], ["9684", "9685", "9687", "9688", "9689", "9690", "9691", "9692"]),
]
STOP = {"the", "a", "an", "to", "my", "and", "of", "your", "for", "in", "on", "with", "but", "so", "that", "i'm",
        "how", "it's", "if", "is", "are", "i", "can", "you", "this", "these", "make", "just", "little", "few", "which",
        "when", "what", "be", "very", "such", "it", "some", "something"}


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True).stdout)


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


def main():
    video, vo, sections, subs = [], [], [], {}
    durs = {}

    def talk(key, group, pad_tail=0.0, zoom=1.0):
        ws = WORDS[key]
        a = quietest(key, max(0.0, ws[0][0] - 0.3), -0.1, 0.1)
        b = quietest(key, ws[-1][1] + 0.35, -0.15, 0.15)
        it = {"group": group, "src": key, "in": a, "out": b, "speech": True}
        if pad_tail:
            it["pad_tail"] = pad_tail
        if zoom != 1.0:
            it["zoom"] = zoom
        video.append(it)
        subs[key] = cues(ws)

    talk("IMG_9627", "intro", pad_tail=0.6)
    for n, (title, notes, clips) in enumerate(TOPICS, 1):
        keys = [N + x for x in notes]
        pieces = [(quietest(k, max(0, WORDS[k][0][0] - 0.12), -0.1, 0.05), quietest(k, WORDS[k][-1][1] + 0.1, -0.05, 0.2))
                  for k in keys]
        need = 0.5 + sum(e - s for s, e in pieces) + NOTE_GAP * (len(pieces) - 1) + TOPIC_TAIL
        names = [f"IMG_{c}" for c in clips]
        for c in names:
            durs[c] = durs.get(c) or dur(f"{SRC}/{c}.MOV")
        lens = [durs[c] - 0.3 for c in names]
        k = need / sum(lens)
        print(f"{title}: vo {need:.1f}s of {sum(lens):.1f}s b-roll (k={k:.2f})")
        assert k <= 1, title
        first = len(video)
        for c, L in zip(names, lens):
            use = L * k
            mid = 0.15 + L / 2
            video.append({"group": "main", "src": c, "in": round(mid - use / 2, 3), "out": round(mid + use / 2, 3)})
        t = 0.5
        for key, (s, e) in zip(keys, pieces):
            vo.append({"src": key, "in": s, "out": e, "item": first, "offset": round(t, 3)})
            subs[key] = cues([w for w in WORDS[key] if s - 0.05 <= w[0] < e])
            t += (e - s) + NOTE_GAP
        sections.append({"index": n, "label": "Idea", "title": title, "item": first, "offset": 0.15})
    talk("IMG_9682", "outro")
    talk("IMG_9683", "outro", zoom=1.08)
    of = [w for w in WORDS["IMG_9683"] if re.search(r"only|fans", w[2], re.I)]
    of_at = of[0][0] - video[-1]["in"]

    (A / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    srcs = {k: f"{SRC}/{k}.MOV" for k in {v["src"] for v in video}}
    srcs.update({k: f"{SRC}/{k}.ogg" for k in {v["src"] for v in vo}})
    tl = {
        "tag": "@masha_masha_mashenkaa",
        "tag_at": 0.8,
        "tag_repeats": [{"item": len(video) - 1, "offset": round(of_at, 2), "note": "see you on my OnlyFans"}],
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
