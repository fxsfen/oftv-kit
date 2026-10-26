"""Timeline for the Halloween witch (Arachne) makeup video (@amane_misa).

Intro / outro: best English takes from the talking clips (Russian chatter and retakes dropped),
jump cuts alternate a 1.08 punch-in. Main: the voice-over recording (Мій запис 42, retakes
removed: best take per line from the phrase-level large-v3 pass) over silent makeup b-roll.
Every b-roll range was checked on 5 s contact sheets: she is working in the mirror / posing,
not out of frame, not lying on the bed, no body close-ups.
"""
import json
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
SRC = "C:/Users/fosfe/Downloads/OFTV Halloween  - Google ไดรฟ์"
INTRO, P1, P2, OUTRO = "VID_20261019_020033", "VID_20261019_020658", "VID_20261019_024116", "VID_20261019_025536"
GAP, PIECE_GAP, TOPIC_TAIL = 0.4, 0.15, 0.6

# (topic, [(a, b), ...] in the VO file, [subtitle text per piece])
LINES = [
    ("skin", [(2.36, 4.76)], ["First, I'm preparing my skin."]),
    ("skin", [(5.3, 9.4)], ["I want everything to look smooth", "but I don't want the makeup", "to feel so heavy."]),
    ("skin", [(16.96, 18.94)], ["I'm going for pale mistress,"]),
    ("skin", [(21.06, 22.62)], ["slightly dramatic vibes."]),
    ("skin", [(26.6, 29.08)], ["Let's see if I can", "pull that off."]),
    ("eyes", [(30.8, 34.4)], ["Okay, now for my favorite part,", "the eyes."]),
    ("eyes", [(35.02, 40.02)], ["I'm using deep purple and black", "shadows to create that smoky,", "mysterious look."]),
    ("eyes", [(40.56, 45.75)], ["I'm definitely not", "a professional makeup artist,", "so we are just", "experimenting today."]),
    ("eyes", [(56.45, 63.16)], ["If an eye looks better", "than the other,", "we are calling it", "artistic freedom."]),
    ("drama", [(67.02, 70.84)], ["Now let's make this look", "a little more dramatic."]),
    ("drama", [(74.46, 79.94)], ["I'm adding some contour", "to sharpen my cheekbones", "and a touch of highlighter,"]),
    ("drama", [(80.38, 82.26)], ["and a deep black lipstick."]),
    ("drama", [(82.8, 86.88)], ["Honestly, the darker lips", "might be my favorite part."]),
    ("drama", [(88.36, 90.52)], ["It's giving mysterious", "Halloween witch,"]),
    ("drama", [(90.92, 92.58)], ["and I'm kind of loving it."]),
    ("finish", [(108.54, 110.08)], ["We are almost there!"]),
    ("finish", [(110.62, 112.74)], ["I'm adding a few", "finishing touches,"]),
    ("finish", [(113.3, 117.38)], ["a little extra definition", "around the eyes, some lashes."]),
    ("finish", [(124.62, 126.04), (127.0, 129.06)], [["I feel like the outfit"], ["and the makeup", "really need to match."]]),
    ("finish", [(129.6, 134.98)], ["Okay, I think our little witch", "transformation", "has finally happened."]),
    ("final", [(137.42, 152.92)], ["And here's the final look!", "Dark, dramatic,", "a little mysterious", "and definitely Halloween-ready.",
                                    "I actually love how", "the purple eyeshadow turned out,", "and the lipstick really",
                                    "brings everything together."]),
]

TOPICS = [  # (topic, section title or None, group, b-roll ranges)
    ("skin", "The Base", "main", [(P1, 8, 40), (P1, 62, 78), (P1, 84, 112)]),
    ("eyes", "Smoky Purple Eyes", "main",
     [(P1, 200, 222), (P1, 248, 270), (P1, 300, 325), (P1, 395, 420), (P1, 450, 475), (P1, 510, 548)]),
    ("drama", "Contour & Dark Lips", "main", [(P2, 52, 100), (P2, 150, 178), (P2, 182, 232)]),
    ("finish", "Finishing Touches", "main", [(P2, 270, 290), (P2, 296, 330), (P2, 356, 372)]),
    ("final", "The Final Look", "outro", [(P2, 376, 420), (P2, 440, 458), (P2, 476, 500)]),
]

# talking pieces: (src, in, out, zoom, subtitle cues as (text, start, end) in source time)
INTRO_ITEMS = [
    (INTRO, 41.3, 54.2, 1.0, [("Hey everyone, welcome back.", 41.4, 45.2), ("I'm Misa, an OnlyFans model", 45.3, 48.3),
                              ("and OFTV creator,", 48.3, 50.0), ("and today we are doing", 50.0, 52.4),
                              ("something a little different.", 52.4, 54.1)]),
    (INTRO, 60.6, 74.0, 1.08, [("Halloween is just", 60.7, 62.6), ("around the corner,", 62.6, 64.0),
                               ("so I thought it would be fun", 64.6, 68.6), ("to try a witchy makeup look.", 68.6, 73.6)]),
    (INTRO, 83.9, 89.3, 1.0, [("Maybe Arachne", 84.1, 86.2), ("from the anime Soul Eater.", 86.2, 89.1)]),
    (INTRO, 103.1, 113.0, 1.08, [("I have never really gone all out", 103.2, 106.4), ("with this style before,", 106.4, 108.2),
                                 ("so let's see how it turns out.", 108.4, 112.8)]),
]
OUTRO_ITEMS = [
    (OUTRO, 35.0, 48.3, 1.0, [("Well, that was so much fun.", 35.1, 37.4), ("I'm Misa, your OnlyFans model", 38.0, 40.9),
                              ("and OFTV creator,", 40.9, 42.2), ("and this was my little Halloween", 42.3, 44.4),
                              ("witch Arachne makeup experience.", 44.4, 48.0)]),
    (OUTRO, 49.5, 52.6, 1.08, [("It definitely turned out darker,", 49.6, 52.5)]),
    (OUTRO, 57.1, 60.9, 1.0, [("more dramatic than my", 57.2, 59.1), ("everyday makeup.", 59.1, 60.6)]),
    (OUTRO, 79.9, 83.2, 1.08, [("And I think that's exactly", 80.0, 81.7), ("what makes it special.", 81.7, 83.1)]),
    (OUTRO, 88.5, 101.6, 1.0, [("Thank you so much for spending", 88.6, 91.4), ("this time with me.", 91.4, 93.3),
                               ("If you'd like to see more", 94.3, 96.7), ("of my exclusive content,", 96.7, 98.2),
                               ("you can find me on OnlyFans.", 98.3, 101.5)]),
    (OUTRO, 108.3, 117.1, 1.08, [("Happy Halloween, everyone!", 108.4, 110.5), ("And I'll see you", 111.8, 114.2),
                                 ("in my next video. Bye!", 114.2, 117.0)]),
]


def energy(path):
    w = wave.open(str(path))
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(sr * 0.02)
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


E = {"vo": energy(A / "vo42.wav"), INTRO: energy(A / f"{INTRO}.wav"), OUTRO: energy(A / f"{OUTRO}.wav")}


def quietest(key, t, lo, hi):
    r = E[key]
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(r) - 1, int((t + hi) / 0.02))
    return round((i0 + int(np.argmin(r[i0:i1 + 1]))) * 0.02, 3)


def split_cues(texts, s, e):
    """One-line cues spread over [s, e] in proportion to their length."""
    tot = sum(len(t) for t in texts)
    out, t = [], s
    for tx in texts:
        d = (e - s) * len(tx) / tot
        out.append([round(t, 3), round(t + d, 3), tx])
        t += d
    return out


def main():
    video, vo, sections, subs = [], [], [], {"vo42": [], INTRO: [], OUTRO: []}

    def talk(items, group, last_pad):
        for k, (src, a, b, z, cues) in enumerate(items):
            a, b = quietest(src, a, -0.12, 0.12), quietest(src, b, -0.12, 0.15)
            it = {"group": group, "src": src, "in": a, "out": b, "speech": True}
            if z != 1.0:
                it["zoom"] = z
            if k == len(items) - 1 and last_pad:
                it["pad_tail"] = last_pad
            video.append(it)
            subs[src] += [[max(s, a), min(e, b), tx] for tx, s, e in cues]

    talk(INTRO_ITEMS, "intro", 0.6)
    n = 0
    tag_item = None
    for topic, title, group, clips in TOPICS:
        lines = [ln for ln in LINES if ln[0] == topic]
        plan = [[(quietest("vo", a, -0.15, 0.06), quietest("vo", b, -0.06, 0.2)) for a, b in r] for _, r, _ in lines]
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
            video.append({"group": group, "src": src, "in": round(mid - length / 2, 3), "out": round(mid + length / 2, 3)})
        t = lead
        for (_, _, texts), p in zip(lines, plan):
            if isinstance(texts[0], list):  # cues given per piece
                per = texts
            elif len(p) == len(texts):  # one cue per piece
                per = [[x] for x in texts]
            else:  # one piece, several cues
                per = [texts]
            for (s, e), tx in zip(p, per):
                vo.append({"src": "vo42", "in": s, "out": e, "item": first, "offset": round(t, 3)})
                subs["vo42"] += split_cues(tx, s, e)
                t += (e - s) + PIECE_GAP
            t += GAP - PIECE_GAP
        if title:
            n += 1
            sections.append({"index": n, "label": "Part", "title": title, "item": first, "offset": 0.15})
    talk(OUTRO_ITEMS, "outro", 0.8)
    tag_item = len(video) - 2  # "...you can find me on OnlyFans"
    of_at = 100.75 - video[tag_item]["in"]

    (A / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tl = {
        "tag": "@amane_misa",
        "tag_at": 0.8,
        "tag_repeats": [{"item": tag_item, "offset": round(of_at, 2), "note": "'you can find me on OnlyFans'"}],
        "music": [f"{SRC}/Soundore - Halloween.mp3", f"{SRC}/HoliznaPATREON - halloween.mp3"],
        "sources": {INTRO: f"{SRC}/{INTRO}.mp4", P1: f"{SRC}/{P1}.mp4", P2: f"{SRC}/{P2}.mp4",
                    OUTRO: f"{SRC}/{OUTRO}.mp4", "vo42": f"{SRC}/Мій запис 42.mp3"},
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} vo_pieces={len(vo)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s")
    print("long cues:", [c[2] for v in subs.values() for c in v if len(c[2]) > 32])


if __name__ == "__main__":
    main()
