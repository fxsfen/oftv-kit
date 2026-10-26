"""Build artifacts/timeline.json for the travel packing vlog.

Each topic = voice-over lines (played back to back with short gaps) over a
list of b-roll clips. Clip ranges are trimmed proportionally so the pictures
last exactly as long as the narration of that topic.
"""
import json
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
SRC = "C:/Users/fosfe/Downloads/путише"
FPS = 30
GAP = 0.45          # silence between consecutive VO lines
TOPIC_TAIL = 0.6    # breathing room after the last line of a topic
PAD_IN, PAD_OUT = 0.08, 0.18

bounds = json.load(open(PROJ / "assets/analysis/speech_bounds.json"))


def vo_key(stamp):
    return f"audio_2026_10_16_{stamp}"


# (section label or None, [VO stamps], [(clip, in, out), ...])
TOPICS = [
    ("Documents", ["00_11_48", "00_11_54"],
     [("IMG_9404", 0.0, 5.4), ("IMG_9438", 0.0, 12.0), ("IMG_9439", 2.0, 18.0)]),
    ("Tech Essentials", ["00_11_58", "00_12_02"],
     [("IMG_9408", 0.0, 3.6), ("IMG_9410", 0.0, 12.1), ("IMG_9407", 0.0, 7.7)]),
    (None, ["00_12_06", "00_12_16"],  # headphones — still part of tech
     [("IMG_9412", 0.0, 13.3), ("IMG_9413", 0.0, 7.7), ("IMG_9414", 0.0, 10.5)]),
    ("Clothes & Comfort", ["00_12_21", "00_12_26"],
     [("IMG_9416", 0.0, 9.7), ("IMG_9415", 0.0, 19.1), ("IMG_9417", 4.0, 20.0)]),
    (None, ["00_12_31"],  # sleepwear
     [("IMG_9418", 0.0, 24.5)]),
    ("Beauty & Accessories", ["00_12_35", "00_12_40"],
     [("IMG_9411", 0.0, 12.0), ("IMG_9420", 0.0, 11.5), ("IMG_9422", 0.0, 2.8), ("IMG_9425", 0.0, 4.0),
      ("IMG_9421", 0.0, 6.7), ("IMG_9426", 0.0, 2.6)]),
    (None, ["00_12_45"],  # sunglasses
     [("IMG_9429", 0.0, 20.1)]),
    (None, ["00_12_48"],  # small accessories / jewellery
     [("IMG_9430", 0.0, 12.9)]),
    ("Just in Case", ["00_12_53", "00_12_57"],
     [("IMG_9432", 0.0, 4.6), ("IMG_9435", 0.0, 21.0), ("IMG_9436", 0.0, 7.5)]),
    (None, ["00_13_04", "00_13_08"],  # everyday bag
     [("IMG_9437", 0.0, 6.3), ("IMG_9447", 0.0, 19.4)]),
]
# Wrap-up lines go over the suitcase being closed, in the outro group.
SUMMARY = (["00_13_13", "00_13_16"],
           [("IMG_9441", 0.0, 5.8), ("IMG_9443", 0.0, 8.1), ("IMG_9444", 0.0, 4.3),
            ("IMG_9445", 0.0, 7.1), ("IMG_9446", 0.0, 13.4)])


def vo_len(stamp):
    b = bounds[vo_key(stamp)]
    s = max(0.0, b["speech_in"] - PAD_IN)
    e = min(b["dur"], b["speech_out"] + PAD_OUT)
    return s, e


def fill(group, stamps, clips, video, vo, lead=0.0):
    """Append clips for one topic; returns index of its first video item."""
    lines = [vo_len(s) for s in stamps]
    need = lead + sum(e - s for s, e in lines) + GAP * (len(lines) - 1) + TOPIC_TAIL
    avail = sum(o - i for _, i, o in clips)
    assert avail >= need, (stamps, avail, need)
    k = need / avail
    first = len(video)
    for clip, i, o in clips:
        length = (o - i) * k
        mid = i + (o - i) / 2  # keep the middle of each shot (action is rarely at the very edges)
        a = max(i, mid - length / 2)
        video.append({"group": group, "src": clip, "in": round(a, 3), "out": round(a + length, 3)})
    t = lead
    for st, (s, e) in zip(stamps, lines):
        vo.append({"src": "vo_" + st, "in": round(s, 3), "out": round(e, 3), "item": first, "offset": round(t, 3)})
        t += (e - s) + GAP
    return first


def main():
    video, vo, sections = [], [], []
    b = bounds["IMG_9394"]
    # intro: freeze the last frame 0.6 s so the whip lands after "...in my suitcase"
    video.append({"group": "intro", "src": "IMG_9394", "in": 0.0, "out": b["dur"], "speech": True, "pad_tail": 0.6})
    n = 0
    for label, stamps, clips in TOPICS:
        first = fill("main", stamps, clips, video, vo, lead=0.5 if label else 0.0)
        if label:
            n += 1
            sections.append({"index": n, "label": "Part", "title": label, "item": first, "offset": 0.15})
    first = fill("outro", SUMMARY[0], SUMMARY[1], video, vo, lead=0.7)
    sections.append({"index": n + 1, "label": "Part", "title": "Final Thoughts", "item": first, "offset": 0.6})
    video.append({"group": "outro", "src": "IMG_9401", "in": 0.0, "out": bounds["IMG_9401"]["dur"], "speech": True})
    out_item = len(video)
    video.append({"group": "outro", "src": "IMG_9402", "in": 0.3, "out": bounds["IMG_9402"]["dur"], "speech": True,
                  "pad_tail": 0.8})

    sources = {c: f"{SRC}/{c}.MOV" for c in {v["src"] for v in video}}
    for st in {x["src"][3:] for x in vo}:
        sources["vo_" + st] = f"{SRC}/audio_2026-10-16_{st.replace('_', '-')}.ogg".replace("audio_2026-10-16_00-", "audio_2026-10-16_00-")
    tl = {
        "tag": "@masha_masha_mashenkaa",
        "tag_at": 0.8,
        "tag_repeats": [{"item": out_item, "offset": 9.8, "note": "'...exclusive content ... on my OnlyFans'"}],
        "music": ["C:/Users/fosfe/Downloads/юбка/Cooked - Dyalla (1) (1).mp3",
                  "C:/Users/fosfe/Downloads/юбка/Moonlit - Dyalla.mp3"],
        "sources": sources,
        "transcript_keys": {**{k: k for k in ["IMG_9394", "IMG_9401", "IMG_9402"]},
                            **{"vo_" + st: vo_key(st) for st in {x["src"][3:] for x in vo}}},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": {"vo_00_12_21@0.72": "comes to", "vo_00_12_31@2.92": "sleep"},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} vo={len(vo)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s")


if __name__ == "__main__":
    main()


