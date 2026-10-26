"""Timeline for the '5 random products makeup challenge' (@amane_misa).

One long voice-over recording full of retakes: LINES lists, for every line we
keep, the source ranges of the best take (from the phrase-by-phrase large-v3
pass in assets/analysis/vo_phrases.json) plus the clean subtitle text. Edges are
snapped to the nearest quiet frame and long pauses inside a take are squeezed.
B-roll comes from the 17-min process video and the reveal video; their (mostly
Russian) camera audio is muted. Only the English on-camera lines are used.
"""
import json
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
SRC = "C:/Users/fosfe/Downloads/OFTV 16.10 - Google ไดรฟ์"
INTRO, PROCESS, REVEAL = "VID_20261015_192239", "VID_20261015_192821", "VID_20261015_195657"
GAP = 0.4            # between VO lines
PIECE_GAP = 0.12     # between pieces of one line (retake splices / squeezed pauses)
TOPIC_TAIL = 0.6
MAX_PAUSE, KEEP_PAUSE = 0.6, 0.3

LINES = [  # (topic, [(a, b), ...] in the VO file, subtitle text)
    ("pick", [(0.0, 3.85)], "Okay, eyes closed."),
    ("pick", [(4.6, 6.05)], "I'm not allowed to peek."),
    ("pick", [(15.7, 20.25)], "Let's see what fate has planned for me today."),
    ("pick", [(20.75, 23.5)], "Product number one. Oh, interesting."),
    ("pick", [(23.85, 25.9)], "That's not what I expected."),
    ("pick", [(32.9, 33.75), (36.6, 38.8)], "Number two. Please be something useful."),
    ("pick", [(39.4, 40.55), (41.05, 43.35), (49.14, 50.7)],
     "Number three. Okay, this could either be amazing or a complete disaster."),
    ("pick", [(51.6, 53.2), (62.8, 64.5)], "Number four. I'm getting nervous now."),
    ("pick", [(64.75, 67.1), (67.8, 68.75), (69.1, 70.35), (70.75, 72.25)],
     "And finally, number five. Yes, that's it. No more choices. I have to make this work."),
    ("reveal", [(80.0, 81.5)], "Let's see what we have got."),
    ("reveal", [(84.9, 85.8), (86.15, 88.2)], "Five products. Zero planning and a lot of hope."),
    ("base", [(104.0, 107.3)], "I need to figure out how to use everything together."),
    ("base", [(107.55, 109.42), (118.2, 120.3)], "Some of these products might have to do double duty today."),
    ("base", [(121.1, 124.65)], "I'm not going to give up before I even start."),
    ("base", [(130.3, 134.25), (134.65, 135.75)], "There is always a way to make makeup work."),
    ("base", [(137.6, 139.45)], "Time to start."),
    ("base", [(144.3, 146.26), (148.36, 151.04), (151.64, 154.18)],
     "I'm going to use products in whatever way makes the most sense. This is all about being creative."),
    ("base", [(155.85, 157.6), (158.1, 160.25), (165.55, 168.0)],
     "I'm starting with the base, if my random selection allows it. If not, we will just have to improvise."),
    ("base", [(168.7, 173.7)], "Honestly, this is already making me think outside the box."),
    ("base", [(181.1, 183.6)], "I never usually do my makeup this way."),
    ("base", [(184.25, 189.3)], "Okay, not perfect, but we are making progress."),
    ("color", [(193.88, 196.5)], "Now for the fun part, adding some color."),
    ("color", [(196.9, 201.1)], "Let's see how creative I can get with these five products."),
    ("color", [(201.8, 204.4), (204.75, 207.1)], "If I have something for the eyes, that's where it's going."),
    ("color", [(214.0, 218.4)], "Maybe one of the other products can help me out."),
    ("color", [(227.7, 230.1)], "I'm trying to make everything look intentional."),
    ("lips", [(238.5, 245.65)], "The lips are always important, so let's see what I can do with whatever I picked."),
    ("lips", [(251.1, 253.9)], "Wait. I think this may actually work."),
    ("lips", [(259.9, 263.55)], "I'm starting to see the look come together."),
    ("lips", [(264.3, 265.8)], "We're almost there."),
    ("lips", [(281.6, 285.45)], "I'm genuinely curious to see the final result."),
    ("final", [(287.5, 289.0)], "And we are done!"),
    ("final", [(292.6, 297.9)], "I can't believe I actually made a full look out of five random products."),
    ("final", [(300.2, 302.1), (302.7, 309.85)],
     "Some choices were definitely unexpected, some choices were definitely expected, "
     "but I think the important thing is that I made it work."),
    ("final", [(313.8, 315.45)], "Let's take one last look."),
    ("final", [(320.5, 325.8)], "The question is, would I actually wear this makeup outside?"),
    ("final", [(327.15, 330.0), (332.7, 337.1)],
     "I'm not sure yet, but I have to admit, this was a lot more fun than I expected."),
]

TOPICS = [  # (topic keys, section title or None, group, b-roll ranges)
    # Every range was checked on face-crop sheets: she is silently working, not talking,
    # turning to someone, out of frame or in a camera close-up (user flagged 1:55 / 2:41).
    (["pick"], "Blind Pick", "main", [(PROCESS, 44, 64), (PROCESS, 64, 80), (PROCESS, 96, 124)]),
    (["reveal"], None, "main", [(PROCESS, 148, 172)]),
    (["base"], "The Base", "main", [(PROCESS, 176, 224), (PROCESS, 320, 386), (PROCESS, 392, 436)]),
    (["color"], "Adding Color", "main",
     [(PROCESS, 440, 470), (PROCESS, 500, 521), (PROCESS, 640, 677), (PROCESS, 708, 756)]),
    (["lips"], "Lips & Final Touches", "main",
     [(PROCESS, 768, 808), (PROCESS, 840, 853), (PROCESS, 862, 880), (PROCESS, 888, 944)]),
    # reveal video: only stretches with no camera speech (Silero VAD) and no close-ups
    (["final"], "The Final Look", "outro",
     [(PROCESS, 1006, 1029), (REVEAL, 27.5, 46.4), (REVEAL, 50.8, 66.8), (REVEAL, 108.0, 115.4)]),]


def energy():
    w = wave.open(str(PROJ / "assets/audio/vo_main_q.wav"))
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(sr * 0.02)
    n = len(x) // hop
    r = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    return r, float(np.percentile(r, 10)) + 10


R, THR = energy()


def quietest(t, lo, hi):
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(R) - 1, int((t + hi) / 0.02))
    return (i0 + int(np.argmin(R[i0:i1 + 1]))) * 0.02


def squeeze(a, b):
    """Split [a, b] at long internal pauses, keeping KEEP_PAUSE of each."""
    out, cur = [], a
    i0, i1 = int(a / 0.02), int(b / 0.02)
    st = None
    for i in range(i0, i1):
        if R[i] < THR:
            if st is None:
                st = i
        else:
            if st is not None and (i - st) * 0.02 > MAX_PAUSE and st > i0 + 5:
                out.append((cur, st * 0.02 + KEEP_PAUSE / 2))
                cur = i * 0.02 - KEEP_PAUSE / 2
            st = None
    out.append((cur, b))
    return out


def pieces(ranges):
    res = []
    for a, b in ranges:
        a = quietest(a, -0.15, 0.08)
        b = quietest(b, -0.08, 0.2)
        res += squeeze(a, b)
    return [(round(s, 3), round(e, 3)) for s, e in res if e - s > 0.12]


def main():
    video, vo, sections, words = [], [], [], []
    video.append({"group": "intro", "src": INTRO, "in": 17.75, "out": round(quietest(24.95, -0.1, 0.1), 3),
                  "speech": True, "pad_tail": 0.6})
    n = 0
    for keys, title, group, clips in TOPICS:
        lines = [ln for ln in LINES if ln[0] in keys]
        plan = [pieces(r) for _, r, _ in lines]
        lead = 0.7 if group == "outro" else 0.5
        need = lead + sum(sum(e - s for s, e in p) + PIECE_GAP * (len(p) - 1) for p in plan) \
            + GAP * (len(plan) - 1) + TOPIC_TAIL
        avail = sum(o - i for _, i, o in clips)
        k = need / avail
        assert k <= 1, (keys, need, avail)
        first = len(video)
        for src, i, o in clips:
            length = (o - i) * k
            mid = i + (o - i) / 2
            video.append({"group": group, "src": src, "in": round(mid - length / 2, 3),
                          "out": round(mid + length / 2, 3)})
        t = lead
        for (_, _, text), p in zip(lines, plan):
            total = sum(e - s for s, e in p)
            toks = text.split()
            acc = 0.0
            for s, e in p:
                vo.append({"src": "vo_main", "in": s, "out": e, "item": first, "offset": round(t, 3)})
                # subtitle words spread evenly over the spoken pieces
                share = toks[round(len(toks) * acc / total): round(len(toks) * (acc + e - s) / total)]
                step = (e - s) / max(1, len(share))
                for j, tk in enumerate(share):
                    words.append({"word": " " + tk, "start": round(s + j * step, 3), "end": round(s + (j + 1) * step, 3)})
                acc += e - s
                t += (e - s) + PIECE_GAP
            t += GAP - PIECE_GAP
        if title:
            n += 1
            sections.append({"index": n, "label": "Part", "title": title, "item": first, "offset": 0.15})
    # on-camera goodbye: drop the "if you... if you like... bye-bye" stumble (196.7-201.4);
    # the second half gets a slight punch-in so the jump cut reads as a cut, not a glitch
    video.append({"group": "outro", "src": REVEAL, "in": 185.75, "out": 194.6, "speech": True})
    last = len(video)
    out_end = round(quietest(211.3, -0.15, 0.03), 3)
    video.append({"group": "outro", "src": REVEAL, "in": 201.35, "out": out_end, "speech": True, "pad_tail": 0.8,
                  "zoom": 1.08})

    talk = json.load(open(PROJ / "assets/analysis/talk_transcripts.json", encoding="utf-8"))
    json.dump({**talk, "vo_main": words}, open(PROJ / "assets/analysis/transcripts.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    tl = {
        "tag": "@amane_misa",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": 1.9, "note": "'you can subscribe to my OnlyFans'"}],
        "music": [f"{SRC}/Cooked - Dyalla (1) (1).mp3", f"{SRC}/On The Flip - The Grey Room _ Density & Time (2).mp3"],
        "sources": {INTRO: f"{SRC}/{INTRO}.mp4", PROCESS: f"{SRC}/{PROCESS}.mp4", REVEAL: f"{SRC}/{REVEAL}.mp4",
                    "vo_main": f"{SRC}/Мій запис 41.mp3"},
        "transcript_keys": {INTRO: INTRO, REVEAL: REVEAL, "vo_main": "vo_main"},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": {},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} vo_pieces={len(vo)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s")


if __name__ == "__main__":
    main()





