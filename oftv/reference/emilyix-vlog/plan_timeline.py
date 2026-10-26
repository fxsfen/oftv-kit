"""Build artifacts/timeline.json for the 'rainy day with me' vlog (@emilyix).

On-camera talking clips are trimmed to their speech (+ breath room); voice-over
topics are laid over b-roll whose length is fitted to the narration.
"""
import json
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
SRC = "C:/Users/fosfe/Downloads/эмил"
GAP = 0.45
TOPIC_TAIL = 0.6
PAD_IN, PAD_OUT = 0.08, 0.18
TALK_IN, TALK_OUT = 0.3, 0.45

bounds = json.load(open(PROJ / "assets/analysis/speech_bounds.json"))


def vo_key(stamp):
    return f"audio_2026_10_16_{stamp}"


def talk(group, clip, out_extra=0.0):
    b = bounds[clip]
    return {"group": group, "src": clip, "in": round(max(0.0, b["speech_in"] - TALK_IN), 3),
            "out": round(min(b["dur"], b["speech_out"] + TALK_OUT + out_extra), 3), "speech": True}


def vo_len(stamp):
    b = bounds[vo_key(stamp)]
    return max(0.0, b["speech_in"] - PAD_IN), min(b["dur"], b["speech_out"] + PAD_OUT)


def fill(group, stamps, clips, video, vo, lead=0.0):
    lines = [vo_len(s) for s in stamps]
    need = lead + sum(e - s for s, e in lines) + GAP * (len(lines) - 1) + TOPIC_TAIL
    avail = sum(o - i for _, i, o in clips)
    assert avail >= need, (stamps, avail, need)
    k = need / avail
    first = len(video)
    for clip, i, o in clips:
        length = (o - i) * k
        mid = i + (o - i) / 2
        a = max(i, mid - length / 2)
        video.append({"group": group, "src": clip, "in": round(a, 3), "out": round(a + length, 3)})
    t = lead
    for st, (s, e) in zip(stamps, lines):
        vo.append({"src": "vo_" + st, "in": round(s, 3), "out": round(e, 3), "item": first, "offset": round(t, 3)})
        t += (e - s) + GAP
    return first


VO_TOPICS = [
    ("Cozy Vibes", ["10_27_44", "10_27_50", "10_27_55"],
     [("IMG_7373", 0.0, 5.0), ("IMG_7377", 1.0, 15.0), ("IMG_7379", 2.0, 15.0), ("IMG_7383", 0.0, 7.3),
      ("IMG_7385", 0.0, 2.7)]),
    ("Reading Time", ["10_27_58", "10_28_02", "10_28_06"],
     [("IMG_7392", 0.0, 8.8), ("IMG_7395", 0.0, 5.9), ("IMG_7397", 0.0, 15.4)]),
    ("A Little Work", ["10_28_11", "10_28_15", "10_29_09", "10_29_13"],
     [("IMG_7398", 0.0, 6.1), ("IMG_7400", 0.0, 10.5), ("IMG_7401", 0.0, 5.2), ("IMG_7404", 0.0, 8.0),
      ("IMG_7405", 2.0, 16.0), ("IMG_7407", 0.0, 8.3), ("IMG_7418", 0.0, 8.9)]),
    ("Self-Care", ["10_29_17", "10_29_21"],
     [("IMG_7436", 0.0, 19.5), ("IMG_7437", 4.0, 40.0), ("IMG_7438", 0.0, 10.3)]),
]


def main():
    video, vo, sections = [], [], []
    # intro: greeting, rain outside, why she stays home
    video.append(talk("intro", "IMG_7316"))
    video.append({"group": "intro", "src": "IMG_7302", "in": 0.5, "out": 4.3})
    video.append(talk("intro", "IMG_7309"))
    video.append(talk("intro", "IMG_7310", out_extra=0.5))  # rain-only tail carries the whip
    n = 0
    # Part 1 is on camera: coffee while it rains
    first = len(video)
    video.append(talk("main", "IMG_7359"))
    video.append({"group": "main", "src": "IMG_7360", "in": 2.0, "out": 6.5})
    video.append(talk("main", "IMG_7369"))
    t71 = talk("main", "IMG_7371")
    t71["in"] = 3.0  # silent sipping before "Honestly..." — keep ~2.5 s of it for mood
    video.append(t71)
    n += 1
    sections.append({"index": n, "label": "Part", "title": "Coffee & Rain", "item": first, "offset": 0.15})
    for label, stamps, clips in VO_TOPICS:
        first = fill("main", stamps, clips, video, vo, lead=0.5)
        n += 1
        sections.append({"index": n, "label": "Part", "title": label, "item": first, "offset": 0.15})
    # outro: reflective line over the window, then on-camera goodbye
    first = fill("outro", ["10_29_26"], [("IMG_7299", 0.0, 6.2), ("IMG_7381", 0.0, 5.0)], video, vo, lead=0.7)
    sections.append({"index": n + 1, "label": "Part", "title": "Final Thoughts", "item": first, "offset": 0.6})
    for c in ["IMG_7422", "IMG_7423", "IMG_7432"]:
        video.append(talk("outro", c))
    last = len(video)
    video.append(talk("outro", "IMG_7435", out_extra=0.8))

    sources = {c: f"{SRC}/{c}.MOV" for c in {v["src"] for v in video}}
    for st in {x["src"][3:] for x in vo}:
        sources["vo_" + st] = f"{SRC}/audio_2026-10-16_{st.replace('_', '-')}.ogg"
    tl = {
        "tag": "@emilyix",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": TAG_END_OFFSET, "note": "'...you can find me on my OnlyFans'"}],
        "music": ["C:/Users/fosfe/Downloads/эмил/Lazy Walk - Cheel.mp3",
                  "C:/Users/fosfe/Downloads/эмил/Down The Rabbit Hole - The Grey Room _ Density & Time.mp3"],
        "sources": sources,
        "transcript_keys": {**{v["src"]: v["src"] for v in video if v.get("speech")},
                            **{"vo_" + st: vo_key(st) for st in {x["src"][3:] for x in vo}}},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": WORD_EDITS,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} vo={len(vo)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s")


TAG_END_OFFSET = 4.3   # "you can find me on my OnlyFans" starts 4.4 s into IMG_7435
WORD_EDITS = {"vo_10_27_50@1.44": "lighting,", "vo_10_29_17@0.86": "working"}

if __name__ == "__main__":
    main()


