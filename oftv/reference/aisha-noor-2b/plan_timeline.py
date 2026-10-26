"""Timeline for 'Easy orange bread' (@aisha_noor), Downloads/ее IMG_8961..8996 + voice notes IMG_96xx.

Spanish on-camera intro / tasting / outro; the recipe steps are her voice notes (black-picture
IMG_96xx clips) laid over the silent cooking b-roll, fitted to the narration. Two of her photos
with the finished bread (slow push-in clips in assets/video) cover "look how pretty it is".
Spanish voice kept, English subtitles = hand translation, English plates.
Analysis files (transcripts, speech bounds) are shared with ../aisha-noor-2a.
Writes artifacts/timeline.json and assets/analysis/subs_en.json.
"""
import json
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
A = PROJ.parent / "aisha-noor-2a"
sys.path.insert(0, str(A / "scripts"))
from subs_util import timed_cues_xl  # noqa: E402

SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "ее"][0]
TALK_IN, TALK_OUT = 0.3, 0.35
GAP, LEAD, TOPIC_TAIL = 0.45, 0.5, 0.6
VO_IN, VO_OUT = 0.15, 0.2
ZOOM = 1.08

TEXT = {
    "IMG_8961": "Hi everyone, welcome back to my OFTV channel! I'm Aisha, an OnlyFans model and a content creator. "
                "Today we're doing something a little different: we're making a delicious orange bread.",
    "IMG_8962": "It's a really simple recipe, with just a few ingredients and an amazing orange flavor, "
                "so let's get started.",
    "IMG_9653": "For this recipe we'll use two oranges: one whole orange, and just the juice of the other one.",
    "IMG_9654": "This gives the bread a much more intense orange flavor and aroma.",
    "IMG_9656": "I love when such a simple recipe can taste so fresh.",
    "IMG_9657": "Now we'll put all the ingredients except the flour into the blender.",
    "IMG_9658": "We add the oil, the egg, the sugar, one whole orange and the juice of one orange.",
    "IMG_9659": "And now we simply blend everything until we get a smooth mixture.",
    "IMG_9660": "Done! The mixture has a beautiful color and it smells so much like orange.",
    "IMG_9661": "Now I'll pour the mixture into a bowl.",
    "IMG_9662": "Next we'll add the 300 grams of flour, but first we'll sift it.",
    "IMG_9664": "This helps the batter turn out softer and more even.",
    "IMG_9665": "Now we just have to mix everything gently.",
    "IMG_9667": "No need to overmix, just until all the ingredients are well combined.",
    "IMG_9668": "The batter is ready, now I'll pour it into the pan.",
    "IMG_9669": "And now it can go into the oven.",
    "IMG_9670": "We'll bake it for about 15 to 20 minutes.",
    "IMG_9672": "It's a pretty quick recipe, so we won't have to wait too long.",
    "IMG_9673": "And that's it, our orange bread is ready.",
    "IMG_9674": "Look how pretty it is, and the orange smell is amazing.",
    "IMG_9675": "I'm going to let it cool a little before tasting it.",
    "IMG_9676": "I love how simple this recipe was to make.",
    "IMG_9677": "And we only need a few ingredients to make something so good.",
    "IMG_8991": "Okay, and now let's taste it.",
    "IMG_8992": "It's soft, sweet and it has a really intense orange flavor. It's so good.",
    "IMG_8993": "I think it's perfect with a coffee or a tea, especially in the morning or as an afternoon snack.",
    "IMG_8995": "Well, I hope you liked this recipe and enjoyed this little moment with me in the kitchen.",
    "IMG_8996": "And if you'd like to get to know me better and see a little more of my personal content, "
                "you can subscribe to my OnlyFans. See you, bye!",
}

# (section title, voice notes, b-roll [(clip, in, out)], scale b-roll to the narration?)
VO_PARTS = [
    ("Two Oranges", ["IMG_9653", "IMG_9654", "IMG_9656"],
     [("IMG_8963", 0.0, 4.1), ("IMG_8966", 0.0, 10.2), ("IMG_8967", 0.0, 6.0), ("IMG_8968", 0.0, 4.8),
      ("IMG_8970", 0.0, 4.7)], True),
    ("Into the Blender", ["IMG_9657", "IMG_9658", "IMG_9659", "IMG_9660"],
     [("IMG_8971", 1.5, 6.5), ("IMG_8971", 11.0, 16.0), ("IMG_8971", 24.0, 36.0), ("IMG_8972", 0.0, 4.5),
      ("IMG_9336", 0.0, 4.5), ("IMG_8973", 0.0, 13.6)], True),
    ("Flour & Mixing", ["IMG_9661", "IMG_9662", "IMG_9664", "IMG_9665", "IMG_9667"],
     [("IMG_8974", 0.0, 7.2), ("IMG_8976", 0.0, 6.1), ("IMG_8978", 0.0, 8.2), ("IMG_8979", 0.0, 7.2),
      ("IMG_8980", 0.0, 15.3)], True),
    ("Into the Oven", ["IMG_9668", "IMG_9669", "IMG_9670", "IMG_9672"],
     [("IMG_8981", 0.0, 10.2), ("IMG_8982", 0.0, 4.2), ("IMG_8990", 0.0, 3.0)], True),
    ("Fresh from the Oven", ["IMG_9673", "IMG_9674", "IMG_9675"],
     [("IMG_8990", 3.0, 6.3), ("PHOTO_9003", 0.0, 5.0), ("PHOTO_9023", 0.0, 5.0)], False),
    ("Taste Test", ["IMG_9676", "IMG_9677"],
     [("IMG_8991", 0.0, 10.6)], False),
]
ONLYFANS = ("IMG_8996", 5.5)
MUSIC = ["Lazy Walk - Cheel.mp3", "Flight Is Aight - Karneef.mp3"]


def main():
    tr = json.load(open(A / "assets/analysis/transcripts.json", encoding="utf-8"))
    bounds = json.load(open(A / "assets/analysis/speech_bounds.json", encoding="utf-8"))
    video, vo, sections, subs = [], [], [], {}

    def talk(group, clip, a=None, b=None, title=None, zoom=False):
        bd, ws = bounds[clip], tr[clip]
        s_in = a if a is not None else max(0.0, bd["speech_in"] - TALK_IN)
        s_out = b if b is not None else min(bd["dur"], max(bd["speech_out"], ws[-1]["end"]) + TALK_OUT)
        it = {"group": group, "src": clip, "in": round(s_in, 3), "out": round(s_out, 3), "speech": True}
        if zoom:
            it["zoom"] = ZOOM
        if title:
            sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": len(video),
                             "offset": 0.15})
        video.append(it)
        subs[clip] = timed_cues_xl(TEXT[clip], ws)

    def vo_span(clip):
        bd = bounds[clip]
        return max(0.0, bd["speech_in"] - VO_IN), min(bd["dur"], bd["speech_out"] + VO_OUT)

    def fill(title, vos, clips, scale):
        lines = [vo_span(s) for s in vos]
        need = LEAD + sum(e - s for s, e in lines) + GAP * (len(lines) - 1) + TOPIC_TAIL
        avail = sum(o - i for _, i, o in clips)
        assert avail >= need - 0.3, (title, round(avail, 2), round(need, 2))
        k = min(1.0, need / avail) if scale else 1.0
        first = len(video)
        for clip, i, o in clips:
            length = (o - i) * k
            a = i + (o - i - length) / 2
            video.append({"group": "main", "src": clip, "in": round(a, 3), "out": round(a + length, 3)})
        t = LEAD
        for st, (s, e) in zip(vos, lines):
            vo.append({"src": st, "in": round(s, 3), "out": round(e, 3), "item": first, "offset": round(t, 3)})
            subs[st] = timed_cues_xl(TEXT[st], tr[st])
            t += (e - s) + GAP
        sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": first,
                         "offset": 0.15})

    talk("intro", "IMG_8961", a=0.0)
    talk("intro", "IMG_8962")
    video[-1]["pad_tail"] = 0.4
    for part in VO_PARTS:
        fill(*part)
    # straight on from the cutting shot: she shows the slice, "let's taste it", first bite
    talk("main", "IMG_8991", a=13.6, b=18.6, zoom=True)
    talk("main", "IMG_8992")
    talk("main", "IMG_8993", zoom=True)
    video[-1]["pad_tail"] = 0.4
    talk("outro", "IMG_8995", title="Final Thoughts")
    video[-1]["pad_head"] = 0.5
    talk("outro", "IMG_8996", zoom=True)
    video[-1]["pad_tail"] = 1.0

    of_item = len(video) - 1
    srcs = {v["src"] for v in video} | {x["src"] for x in vo}
    path = {c: (PROJ / "assets/video" / f"{c}.mp4") if c.startswith("PHOTO") else (SRC / f"{c}.MOV") for c in srcs}
    tl = {
        "tag": "@aisha_noor",
        "tag_at": 0.8,
        "tag_repeats": [{"item": of_item, "offset": round(ONLYFANS[1] - video[of_item]["in"], 3),
                         "note": "'pueden suscribirse a mi OnlyFans'"}],
        "music": [str(SRC / m).replace("\\", "/") for m in MUSIC],
        "sources": {c: str(p).replace("\\", "/") for c, p in path.items()},
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "assets/analysis").mkdir(parents=True, exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False),
                                                       encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) + v.get("pad_head", 0) for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"items={len(video)} vo={len(vo)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s "
          f"longest_cue={len(longest[2])} '{longest[2]}'")


if __name__ == "__main__":
    main()
