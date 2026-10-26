"""Timeline for Hessa's "5 small details" outfit video (@hessakhalifa). Spanish voice kept, English subtitles
(hand translation), English plates.

Source: one pre-assembled 1080p file (IMG_5941) with no music: intro to camera (0-21 s), five tips as
voice-over over getting-ready footage with long silent gaps, summary/goodbye to camera (211.7 s on).
Two pillarboxed VERTICAL inserts (133.9-184.7 and 200.7-211.7, found by black-border scan) would get
the video rejected, so the middle is rebuilt: every VO sentence is laid over horizontal footage only
(22-133.5 and 185-200.4; frames checked every 2 s, she never talks to camera there) and the dead air
is squeezed out. Sentence bounds = large-v3 word times, confirmed by an energy scan.
"""
import json
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
SRC = "C:/Users/fosfe/Downloads/монтаж пн/hessakhalifa/IMG_5941.MOV"
MUSIC = ["C:/Users/fosfe/Downloads/монтаж пн/music/Sound Of Freedom - Jazzy Rhodes Deep House.mp3.mp3"]
K = "IMG_5941"
GAP, TOPIC_TAIL = 0.4, 0.7

# intro / outro talking pieces: (in, out, [english cues]) ; cues spread over the piece by length
INTRO = [
    (0.0, 1.95, ["Hi guys, I'm Hessa,"]),
    (2.0, 5.5, ["an OnlyFans model", "and content creator for OFTV."]),
    (5.9, 10.85, ["Today I want to show you", "5 things that make", "my look so much better."]),
    (12.3, 15.6, ["Sometimes you don't need", "to change your whole outfit,"]),
    (15.65, 18.55, ["a few small details", "can make it look much better."]),
    (18.85, 21.1, ["So let's start", "with the first one."]),
]
OUTRO = [
    (210.85, 213.7, ["So these are", "my 5 little tricks:"]),
    (214.5, 220.1, ["jewelry, sunglasses,", "a bag,"]),
    (220.8, 224.2, ["the right shoes,", "the perfect shoes"]),
    (225.3, 228.0, ["and my perfume."]),
    (228.8, 232.0, ["No need for a whole new wardrobe", "for a perfect look."]),
    (232.1, 235.5, ["Sometimes the little details", "are what make the difference."]),
    (236.4, 241.95, ["So if you want to get to know me", "or see more of my content,", "you can find me on OnlyFans."]),
    (241.95, 245.0, ["Thank you so much,", "see you next time!"]),
]
OF_AT = 241.3  # "...pueden encontrarme en OnlyFans" -> second tag plate

# (title, VO sentences [(in, out, [cues])], b-roll ranges)
TOPICS = [
    ("Jewelry", [
        (21.6, 23.35, ["The first one is jewelry."]),
        (23.4, 31.0, ["I think a necklace, earrings", "or even a few rings", "can make a simple outfit",
                      "look so much more special."]),
        (32.05, 37.0, ["I especially love adding", "something delicate", "when my outfit is pretty simple."]),
    ], [(22.2, 44.0)]),
    ("Sunglasses", [
        (70.45, 73.0, ["Number two: sunglasses."]),
        (74.0, 78.55, ["They're probably one of", "the easiest ways", "to give a look personality."]),
        (79.2, 84.55, ["Even if I'm wearing", "something really basic,", "good sunglasses make it all",
                      "look more put together."]),
        (84.6, 87.4, ["Plus, they're really practical."]),
    ], [(70.0, 99.3)]),
    ("The Right Bag", [
        (100.2, 103.05, ["Number three: the right bag."]),
        (103.1, 109.4, ["For me, the bag is", "an important part of the outfit", "because it can completely change",
                        "the feel of the look."]),
        (110.1, 113.4, ["For a casual look,", "I'd choose something simple."]),
        (113.45, 117.6, ["And for something more elegant,", "I like a bag", "that stands out a bit more."]),
    ], [(99.3, 122.0)]),
    ("Shoes", [
        (134.6, 136.8, ["Number four: shoes."]),
        (137.6, 141.45, ["Never underestimate", "how much shoes", "can change an outfit."]),
        (142.0, 147.5, ["The same dress can look", "completely different", "with sneakers, boots or heels."]),
        (150.25, 156.65, ["So when I feel", "my look needs something more,", "I often just change my shoes."]),
    ], [(50.0, 62.4), (122.0, 133.5)]),
    ("Perfume", [
        (185.35, 188.1, ["And number five: perfume."]),
        (188.15, 191.1, ["It may not be something", "people can see,"]),
        (191.15, 193.4, ["but for me", "it's part of the look."]),
        (193.4, 199.4, ["When I wear a perfume I love,", "I automatically feel", "more put together and confident."]),
        (199.85, 205.5, ["I think the best outfit", "isn't just one that looks good,", "but also makes you feel good."]),
    ], [(185.0, 200.4), (44.0, 50.0), (62.5, 70.0)]),
]


def energy():
    w = wave.open(str(A / "wav16" / f"{K}.wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(w.getframerate() * 0.02)
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


E = energy()


def quietest(t, lo, hi):
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(E) - 1, int((t + hi) / 0.02))
    return round((i0 + int(np.argmin(E[i0:i1 + 1]))) * 0.02, 3)


def split_cues(texts, s, e):
    tot = sum(len(t) for t in texts)
    out, t = [], s
    for tx in texts:
        d = (e - s) * len(tx) / tot
        out.append([round(t, 3), round(t + d, 3), tx])
        t += d
    return out


def main():
    video, vo, sections, cues = [], [], [], []
    # intro: one continuous talking item (source 0-21.1), tail freeze for the whip
    video.append({"group": "intro", "src": K, "in": 0.0, "out": quietest(21.1, -0.1, 0.25), "speech": True,
                  "pad_tail": 0.5})
    for a, b, tx in INTRO:
        cues += split_cues(tx, a + 0.05, b - 0.05)
    for n, (title, lines, clips) in enumerate(TOPICS, 1):
        pieces = [(quietest(a, -0.1, 0.05), quietest(b, -0.05, 0.15)) for a, b, _ in lines]
        need = 0.5 + sum(e - s for s, e in pieces) + GAP * (len(pieces) - 1) + TOPIC_TAIL
        avail = sum(o - i for i, o in clips)
        k = need / avail
        print(f"{title}: vo {need:.1f}s of {avail:.1f}s b-roll (k={k:.2f})")
        assert k <= 1, title
        first = len(video)
        for i, o in clips:
            length = (o - i) * k
            mid = i + (o - i) / 2
            video.append({"group": "main", "src": K, "in": round(mid - length / 2, 3), "out": round(mid + length / 2, 3)})
        t = 0.5
        for (s, e), (_, _, tx) in zip(pieces, lines):
            vo.append({"src": K, "in": s, "out": e, "item": first, "offset": round(t, 3)})
            cues += split_cues(tx, s + 0.05, e - 0.05)
            t += (e - s) + GAP
        sections.append({"index": n, "label": "Part", "title": title, "item": first, "offset": 0.15})
    # outro: video from the first horizontal frame (211.75); "Asi que" (210.85-211.75) plays over a
    # frozen first frame (pad_head) right after the whip.
    head = round(211.75 - 210.85, 3)
    video.append({"group": "outro", "src": K, "in": 211.75, "out": 245.3, "speech": True, "pad_head": head})
    vo.append({"src": K, "in": 210.85, "out": 211.75, "item": len(video) - 1, "offset": 0.0})
    for a, b, tx in OUTRO:
        cues += split_cues(tx, a + 0.05, b - 0.05)
    sections.append({"index": 6, "label": "Part", "title": "Final Thoughts", "item": len(video) - 1, "offset": 1.2,
                     "chapter": "Final Thoughts"})

    (A / "subs_en.json").write_text(json.dumps({K: cues}, indent=1, ensure_ascii=False), encoding="utf-8")
    tl = {
        "tag": "@hessakhalifa",
        "tag_at": 0.8,
        "tag_repeats": [{"item": len(video) - 1, "offset": round(head + OF_AT - 211.75, 2), "note": "OnlyFans line"}],
        "music": MUSIC,
        "sources": {K: SRC},
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) + v.get("pad_head", 0) for v in video) - 1.0
    print(f"items={len(video)} vo={len(vo)} ~duration={tot:.1f}s")
    print("long cues:", [c[2] for c in cues if len(c[2]) > 32])


if __name__ == "__main__":
    main()
