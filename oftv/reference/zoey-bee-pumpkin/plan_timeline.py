"""Timeline for Zoey's Halloween pumpkin carving video (@zoey_bee).

Intro: IMG_1802 (to camera) + IMG_1803 ("something for this magic trick" + cutting board).
Main: the voice-over ("Закадровая офтв тыква.m4a", note-to-self lines like "the third part" and retakes
dropped, phrase bounds from a per-phrase large-v3 pass) over the 15-min carving take IMG_1806:
  Part 1 lid  - marker circle (4.6-15), knife around the line (45-82), lid lifted off (133.6-138.8).
               IMG_1805 is the failed take ("it wasn't recording all this time") - not used. Inside 1806
               the lid is off at 104-122 and back on at 123-133 (re-staged); those ranges are skipped so the
               lid only comes off once, on screen, right on "okay, we have a pumpkin lid".
  Part 2 scooping, Part 3 drawing the face, Part 4 carving (+ music-only hold, it's the main event),
  then her on-camera reaction from the end of 1806, Part 5 lights on (IMG_1807).
Never under VO: 1806 ranges where Silero VAD finds her talking (35-45, 329-338, 424-426, 878+).
Outro: IMG_1808 (clean takes; the first "now my little pumpkin..." take is replaced by the second).
"""
import json
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
SRC = "C:/Users/fosfe/Downloads/монтаж пн/zoey_bee"
VO_FILE = [p for p in Path(SRC).iterdir() if p.suffix == ".m4a"][0]
MUSIC = [f"{SRC}/PulseBox - Cinematic Halloween.mp3", f"{SRC}/VibeDepot - Halloween.mp3",
         f"{SRC}/Soundore - Halloween Instagram.mp3"]
GAP, TOPIC_TAIL = 0.45, 0.8
M = "IMG_1806"

# (title, [(vo in, vo out, [cues])], b-roll [(in, out, fixed?)], music-only hold seconds)
TOPICS = [
    ("Cutting the Lid", [
        (5.2, 9.2, ["First, we need to cut off", "the top of the pumpkin."]),
        (10.44, 15.82, ["I'm going to make a circle first", "so I know exactly", "where I want to cut."]),
        (17.74, 22.56, ["And now comes the part", "where we need to be", "a little careful."]),
        (24.2, 28.48, ["I'm trying to follow the line", "all the way around."]),
        (30.38, 32.9, ["Okay, we have a pumpkin lid."]),
    ], [(4.6, 15.0, False), (45.0, 82.0, False), (133.6, 138.8, True)], 0.0),
    ("Scooping It Out", [
        (39.54, 42.3, ["Now we have to", "clean everything out."]),
        (43.24, 47.14, ["And wow, there are", "a lot of seeds in here."]),
        (51.04, 56.82, ["I'm using a spoon", "to remove the seeds and all", "the extra pumpkin flesh."]),
        (59.24, 63.5, ["The inside needs to be", "as empty as possible."]),
        (64.64, 66.86, ["This is definitely", "the messy part,"]),
        (67.58, 69.68, ["but honestly, it's kind of fun."]),
    ], [(141.0, 170.0, False), (175.0, 205.0, False), (207.0, 236.0, False)], 2.0),
    ("Drawing the Face", [
        (73.06, 76.74, ["Now comes my favorite part:", "creating the face."]),
        (82.58, 84.72, ["I'm not using a template."]),
        (85.5, 88.08, ["I want to draw", "everything myself."]),
        (90.72, 94.54, ["I think I want", "big triangle eyes,"]),
        (95.22, 99.2, ["a little nose", "and a really big spooky smile."]),
        (100.08, 102.56, ["And of course,", "we need some teeth."]),
        (104.34, 108.82, ["Okay, she already looks", "a little scary,"]),
        (110.0, 112.66, ["but I think we can", "make her even better."]),
    ], [(375.0, 393.0, False), (401.0, 423.0, False), (439.0, 443.3, False)], 2.0),  # only while she draws (user, 10-21)
    ("Carving", [
        (115.94, 120.76, ["Now it's time to turn", "this drawing into", "a real pumpkin face."]),
        (121.92, 123.02, ["And now the nose."]),
        (136.68, 140.72, ["The mouth is definitely going", "to take a little more time."]),
    ], [(498.0, 560.0, False), (575.0, 650.0, False), (665.0, 760.0, False), (770.0, 830.0, False)], 18.0),
    # "and we're done" lands on the finished mouth (user, 10-21); no section plate
    (None, [(141.68, 143.76, ["And we're done!"])], [(839.0, 842.5, True)], 0.0),
]

# talking pieces: (src, in, out, zoom, [(cue, src start, src end)])
INTRO = [
    ("IMG_1802", 3.9, 45.2, 1.0, [("Hi OFTV!", 4.3, 5.6), ("I'm Zoey, an OnlyFans model", 6.1, 8.6),
                                   ("and OFTV creator,", 8.6, 10.6), ("and today we're getting", 10.7, 12.9),
                                   ("ready for Halloween.", 12.9, 14.6), ("Today I'm going to show you", 15.8, 18.2),
                                   ("how I carve my own", 18.2, 20.6), ("Halloween pumpkin.", 20.6, 22.4),
                                   ("I didn't want to make it", 23.0, 25.0), ("too complicated,", 25.0, 26.6),
                                   ("so I'm going to draw", 27.2, 29.9), ("the face myself", 29.9, 32.0),
                                   ("and see how it turns out.", 32.0, 34.6), ("Hopefully it will look cute", 37.7, 40.2),
                                   ("and spooky at the same time.", 40.2, 42.8), ("Okay, let's start!", 43.5, 45.1)]),
    ("IMG_1803", 1.5, 11.5, 1.0, [("Of course, I need something", 1.7, 4.2), ("for this magic trick.", 4.2, 8.3)]),
]
REACTION = [
    # in-frame takes only: the close-up "reading" take (895-898) and the lean to the lens (904-907) are cut
    (M, 898.0, 902.3, 1.0, [("Okay, actually,", 898.1, 899.4), ("I like how it turned out.", 899.4, 902.1)]),
    (M, 908.8, 913.6, 1.08, [("She's cute,", 909.0, 910.3), ("but also kind of creepy.", 910.4, 913.3)]),
    (M, 921.95, 925.3, 1.08, [("I think that's exactly", 922.2, 923.9), ("what I wanted.", 923.9, 925.2)]),
]
LIGHTS = [
    ("IMG_1807", 6.4, 11.4, 1.0, [("And now we need one last thing:", 6.7, 9.5), ("a light inside.", 9.5, 11.0)]),
    # off-camera line (21-32) cut, she repeats it in frame
    ("IMG_1807", 32.8, 37.0, 1.0, [("This thing,", 33.1, 34.6), ("a light inside.", 34.6, 36.8)]),
    # sitting into frame (80.0-80.5) and fixing the round lamp (85.5-96) cut
    ("IMG_1807", 80.7, 85.4, 1.0, [("And now let's see", 81.1, 83.4), ("how she looks.", 83.4, 85.3)]),
    ("IMG_1807", 137.2, 151.4, 1.08, [("Okay, now it really looks", 137.4, 139.6), ("like a Halloween pumpkin,", 139.6, 141.2),
                                      ("and I made it by myself.", 141.2, 143.6), ("I like it.", 143.6, 145.4),
                                      ("It was my first", 145.5, 146.8), ("Halloween pumpkin with you.", 146.8, 151.0)]),
]
OUTRO = [
    ("IMG_1808", 9.25, 23.35, 1.0, [("And that's it!", 9.5, 11.0), ("That's how I made", 11.4, 13.2),
                                    ("my own Halloween pumpkin.", 13.2, 15.0), ("It was a little messy,", 15.8, 17.7),
                                    ("yeah, a little scary,", 18.2, 20.0), ("but honestly, a lot of fun.", 20.0, 23.1)]),
    ("IMG_1808", 39.85, 63.3, 1.08, [("Now my little pumpkin", 40.0, 41.5), ("is ready for Halloween.", 41.5, 42.9),
                                     ("Thank you for spending", 43.4, 45.0), ("some Halloween time with me,", 45.0, 46.6),
                                     ("OFTV. I'm Zoey,", 46.6, 49.3), ("and I'll see you", 49.8, 51.0),
                                     ("in the next video!", 51.0, 52.5), ("Happy Halloween!", 53.3, 55.0),
                                     ("If you want to see more of me,", 55.4, 57.4),
                                     ("you can always find me", 57.4, 59.0), ("on my OnlyFans.", 59.0, 60.5),
                                     ("Bye-bye!", 60.6, 62.1)]),
]
OF_AT = 59.3  # "...find me on my OnlyFans" in IMG_1808


def energy(key, path):
    w = wave.open(str(path))
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(w.getframerate() * 0.02)
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


E = {}


def quietest(key, t, lo, hi):
    if key not in E:
        p = A / "wav16" / (f"{VO_FILE.stem}.wav" if key == "vo" else f"{key}.wav")
        E[key] = energy(key, p)
    r = E[key]
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(r) - 1, int((t + hi) / 0.02))
    return round((i0 + int(np.argmin(r[i0:i1 + 1]))) * 0.02, 3)


MOTION = json.load(open(A / "motion.json"))  # mean abs frame diff, 4 fps (64x36 gray)


def active_window(src, i, o, length):
    """Start of the `length`-second window inside [i, o] with the most motion (hands working, not a still shot)."""
    d = MOTION[src]
    best, bs = -1.0, i
    t = i
    while t + length <= o + 1e-6:
        a, b = int(t * 4), max(int((t + length) * 4), int(t * 4) + 1)
        m = sum(d[a:b]) / (b - a)
        if m > best:
            best, bs = m, t
        t += 0.25
    return round(bs, 3)


def split_cues(texts, s, e):
    tot = sum(len(t) for t in texts)
    out, t = [], s
    for tx in texts:
        d = (e - s) * len(tx) / tot
        out.append([round(t, 3), round(t + d, 3), tx])
        t += d
    return out


def main():
    video, vo, sections, subs = [], [], [], {"vo": []}

    def talk(items, group, last_pad=0.0):
        for k, (src, a, b, z, cues) in enumerate(items):
            a, b = quietest(src, a, -0.1, 0.1), quietest(src, b, -0.12, 0.15)
            it = {"group": group, "src": src, "in": a, "out": b, "speech": True}
            if z != 1.0:
                it["zoom"] = z
            if k == len(items) - 1 and last_pad:
                it["pad_tail"] = last_pad
            video.append(it)
            subs.setdefault(src, []).extend([[max(s, a), min(e, b), tx] for tx, s, e in cues])

    talk(INTRO[:1], "intro")
    video.append({"group": "intro", "src": "IMG_1803", "in": 2.3, "out": 3.0})
    vo.append({"src": "IMG_1803", "in": 2.55, "out": 7.25, "item": len(video) - 1, "offset": 0.25})
    video.append({"group": "intro", "src": "IMG_1803", "in": 7.4, "out": 11.6, "pad_tail": 0.6})
    subs["IMG_1803"] = [[2.55, 4.6, "Of course, I need something"], [4.6, 7.2, "for this magic trick."]]
    for n, (title, lines, clips, hold) in enumerate(TOPICS, 1):
        pieces = [(quietest("vo", a, -0.12, 0.05), quietest("vo", b, -0.05, 0.15)) for a, b, _ in lines]
        need = 0.6 + sum(e - s for s, e in pieces) + GAP * (len(pieces) - 1) + TOPIC_TAIL + hold
        fixed = sum(o - i for i, o, f in clips if f)
        avail = sum(o - i for i, o, f in clips if not f)
        k = (need - fixed) / avail if avail else 1.0  # only fixed clips: shown whole
        print(f"{title}: vo+hold {need:.1f}s of {avail + fixed:.1f}s b-roll (k={k:.2f})")
        assert 0 < k <= 1, title
        first = len(video)
        for i, o, f in clips:
            length = (o - i) * (1.0 if f else k)
            st = i if f else active_window(M, i, o, length)
            video.append({"group": "main", "src": M, "in": st, "out": round(st + length, 3)})
        t = 0.6
        for (s, e), (_, _, tx) in zip(pieces, lines):
            vo.append({"src": "vo", "in": s, "out": e, "item": first, "offset": round(t, 3)})
            subs["vo"] += split_cues(tx, s + 0.05, e - 0.05)
            t += (e - s) + GAP
        if title:
            sections.append({"index": n, "label": "Part", "title": title, "item": first, "offset": 0.15})
    talk(REACTION, "main")
    sections.append({"index": 5, "label": "Part", "title": "Lights On", "item": len(video), "offset": 0.15})
    talk(LIGHTS[:3], "main")
    # lit pumpkin, then the zoomed close-up - both silent: her line there is Russian
    # ("Блин, какая она красивая", large-v3 check), she must only speak English (user, 10-21)
    video.append({"group": "main", "src": "IMG_1807", "in": 102.6, "out": 105.6})
    video.append({"group": "main", "src": "IMG_1807", "in": 107.0, "out": 110.6})
    talk(LIGHTS[3:], "main", 0.6)
    talk(OUTRO, "outro")
    of_at = OF_AT - video[-1]["in"]

    (A / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tl = {
        "tag": "@zoey_bee",
        "tag_at": 0.8,
        "tag_repeats": [{"item": len(video) - 1, "offset": round(of_at, 2), "note": "find me on my OnlyFans"}],
        "music": MUSIC,
        "sources": {**{k: f"{SRC}/{k}.MOV" for k in ("IMG_1802", "IMG_1803", M, "IMG_1807", "IMG_1808")},
                    "vo": VO_FILE.as_posix()},
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} vo={len(vo)} ~duration={tot:.1f}s")
    print("long cues:", [c[2] for v in subs.values() for c in v if len(c[2]) > 32])


if __name__ == "__main__":
    main()
