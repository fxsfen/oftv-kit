"""Timeline for 'Halloween mulled wine' (@daisyyyli), Downloads/монтаж пнд/daisyyyli (IMG_3173..3227).

She says one line per step on camera (lav mic), the steps themselves are silent b-roll. Her voice memo
'Глинтвейн.m4a' (NFD file name) holds extra lines; the ones she also says on camera (slicing the apple,
honey) are skipped, the rest play over the b-roll of the same step. Titles = DaisyTitle + sparkle (her look,
daisyyyli-outfit), tag = usual TagPlate. Outro clips 3220/3222/3223 contain false starts: spans come from the
phrase pass (phrases.json). Writes artifacts/timeline.json and assets/analysis/subs_en.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from subs_util import timed_cues_xl  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
AN = PROJ / "assets/analysis"
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"

# (clip, group, title lines or None, in, out, speech text or None for silent b-roll)
ITEMS = [
    ("IMG_3173", "intro", None, 0.0, 14.45,
     "Hi everyone! I'm Daisy, an OnlyFans model, and I create content for OnlyFans TV. "
     "And today we are making a classic mulled wine, but with a little Halloween twist."),
    ("IMG_3174", "intro", None, 0.0, 8.3,
     "We'll need a red wine, an apple, a lemon, an orange and some classic spices."),
    ("IMG_3175", "main", ["Slicing", "the Fruit"], 0.0, 2.65, "First, I'm slicing the apple."),
    ("IMG_3176", "main", None, 2.0, 10.0, None),
    ("IMG_3177", "main", None, 26.0, 32.0, None),
    ("IMG_3178", "main", None, 0.0, 5.85, "We should also squeeze the fresh juice from the orange and lemon."),
    ("IMG_3179", "main", None, 5.0, 9.5, None),
    ("IMG_3179", "main", None, 40.0, 44.0, None),
    ("IMG_3180", "main", None, 0.0, 2.65, "Add all the fruit to the pot."),
    ("IMG_3181", "main", None, 1.0, 8.5, None),
    ("IMG_3181", "main", None, 21.0, 26.0, None),
    ("IMG_3182", "main", ["Wine", "& Spices"], 0.2, 3.75, "Now for the most important part."),
    ("IMG_3182", "main", None, 8.0, 14.0, None),
    ("IMG_3183", "main", None, 0.5, 6.5, None),
    ("IMG_3184", "main", None, 1.0, 5.0, None),
    ("IMG_3185", "main", None, 1.0, 12.0, None),
    ("IMG_3186", "main", None, 0.0, 6.0, None),
    ("IMG_3187", "main", None, 0.0, 4.0, None),
    ("IMG_3188", "main", ["A Touch", "of Honey"], 0.0, 3.7, "To balance the flavors, I am adding a little honey."),
    ("IMG_3189", "main", None, 0.5, 9.0, None),
    ("IMG_3190", "main", ["Low", "& Slow"], 0.5, 10.0, None),
    ("IMG_3191", "main", None, 3.0, 13.0, None),
    ("IMG_3192", "main", ["The Spooky", "Twist"], 1.95, 8.1,  # first "and to make your" was a false start
     "And to make your classic mulled wine a little more spooky, you can add a bloody rim."),
    ("IMG_3193", "main", None, 2.0, 8.0, None),
    ("IMG_3194", "main", None, 20.0, 26.0, None),
    ("IMG_3194", "main", None, 60.0, 66.0, None),
    ("IMG_3195", "main", None, 0.0, 5.6, "Wow, it looks a little creepy, but that's actually what we are going for."),
    ("IMG_3196", "main", None, 0.0, 5.15, "Okay, now I'm pouring the warm mulled wine into our spooky glass."),
    ("IMG_3196", "main", None, 7.0, 14.0, None),
    ("IMG_3197", "main", None, 50.0, 63.5, None),
    ("IMG_3220", "outro", ["Final", "Thoughts"], 1.55, 8.95,  # drop the false start "End of video"
     "And just like that, our classic mulled wine has become the perfect Halloween drink."),
    ("IMG_3220", "outro", None, 9.0, 12.1, None),  # first sip, before her "thank you" aside
    ("IMG_3222", "outro", None, 1.9, 10.75,  # drop the first "I love that"
     "I love that it's still a classic mulled wine, but it looks so much more interesting."),
    ("IMG_3223", "outro", None, 3.9, 14.75,  # drop "Thank you for spending"
     "Thank you for making this Halloween mulled wine with me. "
     "It's such a simple recipe, but it's perfect for a cozy autumn evening."),
    ("IMG_3227", "outro", None, 1.8, 23.0,  # ends after her wave
     "I'm Daisy, an OnlyFans model and OnlyFans TV creator. If you'd like to see more of my recipes, lifestyle "
     "and exclusive moments from my life, check out my OnlyFans. See you in the next video and Happy Halloween!"),
]
ONLYFANS = ("IMG_3227", 14.64)
VO = [  # (anchor item: src + its in, offset, memo in, memo out, text)
    (("IMG_3176", 2.0), 0.3, 6.96, 13.95,
     "I like to keep the skin on because it looks prettier in the finished drink."),
    (("IMG_3177", 26.0), 0.4, 14.4, 18.6, "Next, I'm slicing the orange and lemon."),
    (("IMG_3181", 1.0), 0.4, 21.56, 27.45, "Now I'm adding all of our fruit and fresh juice."),
    (("IMG_3183", 0.5), 0.3, 27.56, 32.85, "And I'm adding the red wine to the saucepan."),
    (("IMG_3185", 1.0), 0.3, 34.13, 42.1, "And now for the spices: cinnamon, star anise and a few cloves."),
    (("IMG_3186", 0.0), 0.4, 43.25, 48.05, "The whole kitchen already smells absolutely amazing."),
    (("IMG_3189", 0.5), 0.3, 54.78, 62.6, "You can add more or less, depending on how sweet you like your mulled wine."),
    (("IMG_3190", 0.5), 0.4, 64.76, 73.35, "Now I'm gently heating the mulled wine. The important thing is not to let it boil."),
    (("IMG_3191", 3.0), 0.3, 74.06, 83.05,
     "We just want the wine to warm up while the fruit and spices release all their beautiful flavors."),
    (("IMG_3197", 50.0), 0.5, 84.16, 93.4,
     "For the garnish, I'm adding an orange slice, a cinnamon stick and some star anise."),
]
MUSIC = [LOFI / "HoliznaCC0 - One Night In France(Lofi, Nostalgic, Chill).mp3",
         LOFI / "HoliznaCC0 - Tokyo Sunset(Lofi, Peaceful, Soft).mp3"]


def main():
    S = json.load(open(AN / "sources.json", encoding="utf-8"))
    tr = json.load(open(AN / "transcripts.json", encoding="utf-8"))
    vo_key = next(k for k in S["sources"] if S["sources"][k].lower().endswith(".m4a"))
    video, sections, subs = [], [], {}
    for clip, group, title, a, b, text in ITEMS:
        it = {"group": group, "src": clip, "in": a, "out": round(min(b, S["dur"][clip] - 0.05), 3),
              "speech": text is not None}
        if title:
            sections.append({"index": len(sections) + 1, "lines": title, "title": " ".join(title),
                             "item": len(video), "offset": 0.3})
        video.append(it)
        if text:
            ws = [w for w in tr[clip] if a - 0.3 <= w["start"] < b]
            subs.setdefault(clip, []).extend(timed_cues_xl(text, ws))
    for i in range(len(video) - 1):
        if video[i]["group"] != video[i + 1]["group"]:
            video[i]["pad_tail"] = 0.4
    video[-1]["pad_tail"] = 0.5
    of_item = next(i for i, v in enumerate(video) if v["src"] == ONLYFANS[0])
    vo = []
    for (src, t_in), off, a, b, text in VO:
        k = next(i for i, v in enumerate(video) if v["src"] == src and abs(v["in"] - t_in) < 0.01)
        assert not video[k]["speech"] and off + b - a <= video[k]["out"] - video[k]["in"] + 0.05, (src, t_in)
        vo.append({"src": vo_key, "in": a, "out": b, "item": k, "offset": off})
        subs.setdefault(vo_key, []).extend(timed_cues_xl(text, [w for w in tr[vo_key] if a - 0.05 <= w["start"] < b]))
    tl = {
        "tag": "@daisyyyli",
        "tag_at": 0.8,
        "tag_repeats": [{"item": of_item, "offset": round(ONLYFANS[1] - video[of_item]["in"], 3),
                         "note": "'check out my OnlyFans'"}],
        "title_style": "daisy",
        "music": [m.as_posix() for m in MUSIC],
        "sources": {k: S["sources"][k] for k in {v["src"] for v in video} | {vo_key}},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": {},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (AN / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"items={len(video)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s")
    for k, cs in subs.items():
        for c in cs:
            print(k[-4:], c)


if __name__ == "__main__":
    main()
