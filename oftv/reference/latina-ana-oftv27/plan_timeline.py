"""Timeline for @latinagirl_ana — OFTV 27: everyday home clothes -> alternative outfit.

English speech. On-camera intro (8373/74/76/77/75, mic + green light) -> VO (vo16, vo4, vo11) over the
silent try-on footage (8378-8385) -> on-camera outro (8389/86/88).
There is ~127 s of usable b-roll for ~180 s of narration, so the b-roll runs as ONE continuous stream in
story order, slowed uniformly (speed = footage / narration, >= 0.68); section plates sit on the first line
of each section. Close-ups of her face (8382, 8382_4) and moments where she looks/smiles into the lens
(ends of 8382_5, 8383, 8385_1, 8385_3, 8382_2) are left out.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_timeline_ana26 import pieces, timed_cues  # noqa: E402  (same helpers as OFTV 26)

PROJ = Path(__file__).resolve().parents[1]
AN = PROJ / "assets/analysis"
SRC = Path(r"C:\Users\fosfe\Downloads") / "ана2" / "OFTV 27-20261019T165215Z-1-001" / "OFTV 27"
SMAP = json.load(open(AN / "sources.json", encoding="utf-8"))
GAP = 0.35
PIECE_GAP = 0.3
LEAD = 0.5
TAIL = 0.6
MIN_SPEED = 0.68
import unicodedata
_NFC = {unicodedata.normalize("NFC", p.name): p for p in SRC.iterdir()}  # names on disk are NFD


def path(key):
    return str(_NFC[SMAP[key]]).replace("\\", "/")


LINES = [  # (section title or None, voice key, pieces, subtitle text)
    ("The Starting Point", "vo16", [(2.10, 7.61)], "First, let's look at what we are starting with."),
    (None, "vo16", [(9.32, 14.99)], "Just a regular t-shirt and my favorite comfy pants."),
    (None, "vo16", [(15.90, 37.21)],
     "Honestly, this is what I wear on a normal day at home, but I think alternative fashion is all about the "
     "details, so I'm going to keep the comfortable base and build the whole look around it."),
    ("Shape & Layers", "vo16", [(43.30, 47.69)], "The first thing I'm changing is the silhouette."),
    (None, "vo16", [(48.24, 61.69)],
     "I'm tucking in just the front of my t-shirt to give the outfit a little more shape, and now I'm adding "
     "another layer."),
    (None, "vo16", [(62.84, 73.01)], "A loose shirt or a mesh top instantly makes everything look more intentional."),
    (None, "vo16", [(73.16, 80.30), (81.32, 84.33)],
     "I love how layering adds texture and makes even the simplest looks feel a little more alternative."),
    ("Accessories", "vo4", [(0.68, 6.13)], "Now for my favorite part: accessories."),
    (None, "vo4", [(6.24, 14.61)], "I'm adding silver chains, a choker, a few rings and a belt with metal details."),
    (None, "vo4", [(15.56, 20.79)], "These little things can completely change the mood of an outfit."),
    (None, "vo4", [(21.36, 24.99), (25.30, 35.33)],
     "I don't want to overdo it, so the idea is to make the look feel effortless, a little edgy and still "
     "comfortable enough to wear every day."),
    ("Makeup & Boots", "vo4", [(39.82, 46.39)], "To finish the look, I'm keeping my makeup simple but a little darker."),
    (None, "vo4", [(47.34, 54.95), (55.70, 57.77)], "A bit of eyeliner, mascara and a lip color that match the outfit are all I need."),
    (None, "vo4", [(60.10, 60.61), (61.48, 64.60), (65.55, 67.85)], "I paired this with chunky boots and a small black bag."),
    (None, "vo4", [(68.22, 79.81)],
     "I think the secret is making the clothes, accessories and makeup work together without losing that "
     "relaxed everyday feeling."),
    ("The Final Look", "vo4", [(83.34, 87.37)], "And here's the final look."),
    (None, "vo4", [(88.40, 100.87), (101.74, 105.55)],
     "We started with clothes I'd normally wear at home, and now we've got an alternative outfit with layers, "
     "silver accessories and dark makeup."),
    ("Final Thoughts", "vo11", [(1.04, 2.10), (2.72, 6.97)], "I didn't need a whole new wardrobe or anything complicated."),
    (None, "vo11", [(7.52, 18.87)],
     "Sometimes all it takes is a little creativity and a few details to make your everyday clothes feel "
     "completely different."),
]

BROLL = [  # story order: base clothes -> tuck + mesh layer -> accessories -> makeup + boots -> final look
    ("IMG_8378", 0, 3.5), ("IMG_8378_1", 0, 5.1), ("IMG_8380_1", 0, 1.9), ("IMG_8380_3", 0, 4.8),
    ("IMG_8381", 0, 4.6), ("IMG_8381_1", 0, 2.1),
    ("IMG_8380_2", 0, 3.8), ("IMG_8379", 0, 1.2), ("IMG_8379_1", 0, 5.3), ("IMG_8380", 0, 4.4),
    ("IMG_8382_1", 0, 11.5), ("IMG_8382_5", 0, 7.0), ("IMG_8382_1", 11.5, 23.3),
    ("IMG_8383", 0, 18.5), ("IMG_8384", 3.0, 6.0), ("IMG_8382_2", 0, 1.8), ("IMG_8382_3", 0, 5.4),
    ("IMG_8385", 0, 4.1), ("IMG_8385_1", 0, 5.0), ("IMG_8385_2", 0, 6.2), ("IMG_8385_3", 0, 11.0),
    ("IMG_8385_4", 0, 4.5),
]

VAD = json.load(open(AN / "camera_speech.json"))
INTRO = [  # (clip, text)
    ("IMG_8373", "Hi everyone, I'm Ana. I'm an OnlyFans model and an OFTV blogger, and today I want to try something fun."),
    ("IMG_8374", "Turning the clothes I usually wear at home into an alternative outfit."),
    ("IMG_8376", "I've got a basic t-shirt and comfy pants."),
    ("IMG_8377", "So let's see how much personality we can add without changing the whole outfit."),
    ("IMG_8375", "Let's get started."),
]
OUTRO = [
    ("IMG_8389", "And that's how I turn my everyday home clothes into an alternative look."),
    ("IMG_8386", "I'm Ana, an OnlyFans model, and thank you for spending this time with me."),
    ("IMG_8388", "If you want to see more of my content and get to know me better, you can subscribe to my OnlyFans. "
                 "See you soon!"),
]
ONLYFANS_OFFSET = 5.4   # into IMG_8388 (from its in-point): "...subscribe to my OnlyFans"


def talking(clip, text, group, subs):
    import soundfile as sf
    s, e = VAD[clip][0][0], VAD[clip][-1][1]
    dur = sf.info(str(AN / "wav16" / f"{clip}.wav")).duration - 0.05   # never past the last frame
    a = round(max(0.0, s - 0.3), 2)
    b = round(min(e + 0.3, dur), 2)
    subs.setdefault(clip, []).extend(timed_cues(text, [(s, e)]))
    return {"group": group, "src": clip, "in": a, "out": b, "speech": True}


def main():
    tr = json.load(open(AN / "transcripts.json", encoding="utf-8"))
    video, vo, sections, subs = [], [], [], {}
    for clip, text in INTRO:
        video.append(talking(clip, text, "intro", subs))
    video[-1]["out"] = min(video[-1]["out"], 2.44)
    video[-1]["pad_tail"] = 0.5          # 8375 ends on her last word: freeze so the whip sits in silence

    first = len(video)
    t, n = LEAD, 0
    for title, key, rng, text in LINES:
        p = pieces(Path(path(key)), rng)
        if title:
            n += 1
            sections.append({"index": n, "label": "Part", "title": title, "item": first,
                             "offset": round(max(0.15, t - 0.35), 3)})
        for s, e in p:
            vo.append({"src": key, "in": s, "out": e, "item": first, "offset": round(t, 3)})
            t += (e - s) + PIECE_GAP
        t += GAP - PIECE_GAP
        subs.setdefault(key, []).extend(timed_cues(text, p, tr[key]))
    need = t - GAP + TAIL
    avail = sum(o - i for _, i, o in BROLL)
    speed = round(avail / need, 4)
    assert MIN_SPEED <= speed <= 1.0, (speed, need, avail)
    for src, i, o in BROLL:
        video.append({"group": "main", "src": src, "in": i, "out": o, "speed": speed})

    for clip, text in OUTRO:
        video.append(talking(clip, text, "outro", subs))
    video[len(video) - 3]["pad_head"] = 0.35   # 8389: speech starts right away, keep the whip in silence
    last = len(video) - 1
    video[last]["pad_tail"] = 0.8
    srcs = {v["src"] for v in video}
    tl = {
        "tag": "@latinagirl_ana",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": ONLYFANS_OFFSET, "note": "'you can subscribe to my OnlyFans'"}],
        "music": [path_m("Sound Of Freedom - Chil Hip-Hop Beat .mp3.mp3"),
                  path_m("Sound Of Freedom - Lo-Fi R&B Vibe.mp3.mp3")],
        "sources": {**{c: path(c) for c in srcs}, **{k: path(k) for k in ("vo16", "vo4", "vo11")}},
        "transcript_keys": {**{c: c for c in srcs}, **{k: k for k in ("vo16", "vo4", "vo11")}},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": {},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (AN / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum((v["out"] - v["in"]) / v.get("speed", 1) + v.get("pad_tail", 0) + v.get("pad_head", 0) for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    print(f"items={len(video)} vo_pieces={len(vo)} speed={speed} narration={need:.1f}s footage={avail:.1f}s "
          f"sections={[s['title'] for s in sections]} ~duration={tot:.1f}s longest_cue={len(longest[2])}")


def path_m(name):
    return str(SRC / name).replace("\\", "/")


if __name__ == "__main__":
    main()
