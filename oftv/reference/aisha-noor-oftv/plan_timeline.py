"""Build artifacts/timeline.json for 'What's in my bag' (@aisha_noor).

Spanish on-camera talking clips are trimmed to their speech (+ breath room); the
audio-only clips (IMG_92xx, black picture) are voice-over laid over the bag
unpacking b-roll (IMG_8017 / IMG_8021), fitted to the narration.
Subtitles are English translations (assets/analysis/subs_en.json), not Whisper text.
"""
import json
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
SRC = "C:/Users/fosfe/Downloads/аиш"
GAP = 0.45
TOPIC_TAIL = 0.6
PAD_IN, PAD_OUT = 0.08, 0.18
TALK_IN, TALK_OUT = 0.3, 0.45
HEAD_PAD = 0.5  # = whip length

bounds = json.load(open(PROJ / "assets/analysis/speech_bounds.json"))
TRIM = json.loads((PROJ / "assets/analysis/trim.json").read_text(encoding="utf-8"))


def talk(group, clip, out_extra=0.0):
    b = bounds[clip]
    t = TRIM.get(clip, {})
    s_in = t.get("in", b["speech_in"])
    s_out = t.get("out", b["speech_out"])
    return {"group": group, "src": clip, "in": round(max(0.0, s_in - TALK_IN), 3),
            "out": round(min(b["dur"], s_out + TALK_OUT + out_extra), 3), "speech": True}


def vo_len(clip):
    b = bounds[clip]
    t = TRIM.get(clip, {})
    return max(0.0, t.get("in", b["speech_in"]) - PAD_IN), min(b["dur"], t.get("out", b["speech_out"]) + PAD_OUT)


def fill(group, vos, clips, video, vo, lead=0.0):
    lines = [vo_len(s) for s in vos]
    need = lead + sum(e - s for s, e in lines) + GAP * (len(lines) - 1) + TOPIC_TAIL
    avail = sum(o - i for _, i, o in clips)
    assert avail >= need, (vos, avail, need)
    k = need / avail
    first = len(video)
    for clip, i, o in clips:
        length = (o - i) * k
        mid = i + (o - i) / 2
        a = max(i, mid - length / 2)
        video.append({"group": group, "src": clip, "in": round(a, 3), "out": round(a + length, 3)})
    t = lead
    for st, (s, e) in zip(vos, lines):
        vo.append({"src": st, "in": round(s, 3), "out": round(e, 3), "item": first, "offset": round(t, 3)})
        t += (e - s) + GAP
    return first


# (title, talking clips) in story order
ON_CAMERA = [
    ("The Bag", ["IMG_8004", "IMG_8005"]),
    ("Phone & Keys", ["IMG_8030", "IMG_8031", "IMG_8006"]),
    ("Quick Touch-Ups", ["IMG_8008", "IMG_8009", "IMG_8010", "IMG_8011", "IMG_8012"]),
    ("Tech Essentials", ["IMG_8013", "IMG_8014", "IMG_8015"]),
]
LITTLE_THINGS = (["IMG_9279", "IMG_9282", "IMG_9285", "IMG_9287"],
                 [("IMG_8021", 0.5, 8.5), ("IMG_8017", 0.0, 6.0), ("IMG_8017", 23.0, 29.0),
                  ("IMG_8017", 9.0, 14.0), ("IMG_8017", 14.0, 22.0), ("IMG_8021", 10.0, 17.0)])
FAVORITE = ["IMG_8018", "IMG_8019", "IMG_8020"]
OUTRO = ["IMG_8022", "IMG_8024", "IMG_8025", "IMG_8026"]


def main():
    video, vo, sections = [], [], []
    video.append(talk("intro", "IMG_8001"))
    video.append(talk("intro", "IMG_8002"))
    video.append(talk("intro", "IMG_8003", out_extra=0.5))  # breath tail carries the whip
    n = 0
    for k, (title, clips) in enumerate(ON_CAMERA):
        first = len(video)
        for c in clips:
            video.append(talk("main", c))
        if k == 0:  # frozen first frame of the same shot: the whip lands in silence, not over her first word
            video[first]["pad_head"] = HEAD_PAD
        n += 1
        sections.append({"index": n, "label": "Part", "title": title, "item": first, "offset": 0.15})
    first = fill("main", *LITTLE_THINGS, video, vo, lead=0.5)
    n += 1
    sections.append({"index": n, "label": "Part", "title": "The Little Things", "item": first, "offset": 0.15})
    first = len(video)
    for c in FAVORITE:
        video.append(talk("main", c))
    video[-1]["out"] = round(min(bounds[FAVORITE[-1]]["dur"], video[-1]["out"] + 0.5), 3)
    n += 1
    sections.append({"index": n, "label": "Part", "title": "My Favorite", "item": first, "offset": 0.15})
    first = len(video)
    for c in OUTRO:
        video.append(talk("outro", c, out_extra=0.8 if c == OUTRO[-1] else 0.0))
    video[first]["pad_head"] = HEAD_PAD
    sections.append({"index": n + 1, "label": "Part", "title": "Final Thoughts", "item": first, "offset": 0.6})
    last = len(video) - 1

    srcs = {v["src"] for v in video} | {x["src"] for x in vo}
    tl = {
        "tag": "@aisha_noor",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": TAG_END_OFFSET - video[last]["in"],
                         "note": "'...suscribirse a mi OnlyFans'"}],
        "music": [f"{SRC}/Sound Of Freedom - Lo-Fi R&B Vibe.mp3.mp3",
                  f"{SRC}/Sound Of Freedom - Chil Hip-Hop Beat .mp3.mp3"],
        "sources": {c: f"{SRC}/{c}.MOV" for c in srcs},
        "transcript_keys": {c: c for c in srcs},
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} vo={len(vo)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s")


TAG_END_OFFSET = float(TRIM.get("_onlyfans_at", 0.0))  # source time of 'OnlyFans' in the last clip

if __name__ == "__main__":
    main()
