"""Timeline for 'Basic outfit -> stylish look' (@daisyyyli), Downloads/OFTV outfit (IMG_3135..3159).

She says one short line per step on camera (handheld mic), then a silent try-on shot shows it.
Talk parts keep her voice; try-on parts get her voice-memo lines (VO) or music only. Talk clips that continue into the
try-on are split into a speech item + a silent item (seamless, same source).
Intro -> six steps (Daisy titles, top-left) -> Final Thoughts; whips only intro->main->outro.
Writes artifacts/timeline.json and assets/analysis/subs_en.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from subs_util import timed_cues_xl  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name.startswith("OFTV outfit")][0]

# (clip, group, title lines or None, in, out, speech text or None for a silent try-on shot)
ITEMS = [
    ("IMG_3135", "intro", None, 0.0, 17.45,
     "Hi everyone! I'm Daisy, an OnlyFans model and OnlyFans TV creator, and today I'm going to show you "
     "how to turn a simple basic outfit into a stylish look with just a few simple steps."),
    ("IMG_3136", "main", ["Simple", "Basics"], 0.0, 7.15,
     "Let's start with the simplest look possible: a T-shirt, jeans and sneakers."),
    ("IMG_3137", "main", None, 4.0, 8.0, None),
    ("IMG_3138", "main", None, 0.5, 4.5, None),
    ("IMG_3139", "main", ["Adding", "a Belt"], 0.45, 5.2, "The first little trick is adding a belt."),
    ("IMG_3139", "main", None, 5.2, 14.0, None),
    ("IMG_3140", "main", None, 4.0, 7.5, None),
    ("IMG_3141", "main", ["Jewelry", "Time"], 0.7, 4.12, "Now let's add some jewelry."),
    ("IMG_3142", "main", None, 0.5, 7.0, None),
    ("IMG_3142", "main", None, 22.0, 26.0, None),
    ("IMG_3144", "main", None, 7.0, 10.5, None),
    ("IMG_3145", "main", None, 1.5, 5.0, None),
    ("IMG_3146", "main", ["Layering", "Up"], 7.25, 11.45, "The next step is adding a layer."),
    ("IMG_3146", "main", None, 11.45, 22.6, None),
    ("IMG_3147", "main", None, 2.0, 6.0, None),
    ("IMG_3148", "main", ["Statement", "Glasses"], 0.6, 6.05, "Now let's add one statement accessory."),
    ("IMG_3148", "main", None, 6.05, 15.85, None),
    ("IMG_3149", "main", ["The Right", "Bag"], 0.0, 3.3, "The next step is the bag."),
    ("IMG_3150", "main", None, 5.0, 9.0, None),
    ("IMG_3151", "main", None, 1.0, 4.95, "Today I'm choosing a bigger bag."),
    ("IMG_3151", "main", None, 4.95, 9.5, None),
    ("IMG_3152", "main", None, 8.0, 13.0, None),
    ("IMG_3153", "outro", ["Final", "Thoughts"], 0.0, 5.9,
     "And just like that, the same basic outfit looks completely different."),
    ("IMG_3155", "outro", None, 0.0, 12.45,
     "I love that you don't need to buy a whole new wardrobe, you just need to style what you already "
     "have in a different way."),
    ("IMG_3156", "outro", None, 2.1, 10.64,  # 1st "My," was a false start
     "My biggest tip is to start with a simple outfit and then add your details one by one."),
    ("IMG_3158", "outro", None, 1.35, 14.3,  # drop the "Uh"
     "Thank you for spending this time with me today. I hope this gives you some easy ideas for turning "
     "your basic pieces into stylish outfits."),
    ("IMG_3159", "outro", None, 4.05, 25.6,  # retake of "I'm Daisy"; ends after the kiss + pose
     "I'm Daisy, an OnlyFans model creating exclusive content, and if you'd like to see more of my outfits, "
     "lifestyle and behind-the-scenes moments, I'd love to see you on my OnlyFans. See you in the next video!"),
]
ONLYFANS = ("IMG_3159", 18.3)
# Her voice memo in the folder ("Campetto di rovascio.m4a" = iPhone location name) holds extra
# lines for the steps. Lines she also says on camera (belt / layer / bag) are skipped; the rest
# go over the silent try-on shot of the same step, anchored to that item.
VO_FILE = "Campetto di rovascio.m4a"
VO = [  # (anchor item: src + its in, offset, vo in, vo out, text)
    (("IMG_3139", 5.2), 0.35, 8.85, 17.2,
     "It instantly makes the outfit look more put-together and defines the silhouette."),
    (("IMG_3142", 0.5), 0.35, 18.55, 24.5, "Even a few minimal details can make a big difference."),
    (("IMG_3146", 11.45), 0.3, 29.28, 40.0,
     "A blazer or an oversized shirt instantly makes a basic outfit more interesting and adds dimension."),
    (("IMG_3148", 6.05), 0.3, 40.35, 49.05,
     "For me, it's sunglasses. The key is not to add too many accessories at once."),
]
MUSIC = Path(r"C:\Users\fosfe\Downloads\ее\Sound Of Freedom - Jazzy Rhodes Deep House.mp3.mp3")


def main():
    tr = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
    bounds = json.load(open(PROJ / "assets/analysis/speech_bounds.json", encoding="utf-8"))
    video, sections, subs = [], [], {}
    for clip, group, title, a, b, text in ITEMS:
        it = {"group": group, "src": clip, "in": a, "out": round(min(b, bounds[clip]["dur"] - 0.02), 3),
              "speech": text is not None}
        if title:
            sections.append({"index": len(sections) + 1, "lines": title, "title": " ".join(title),
                             "item": len(video), "offset": 0.3})
        video.append(it)
        if text:
            # 3146 has two takes of the same line: time cues from the kept (second) take only.
            ws = [w for w in tr[clip] if a - 0.3 <= w["start"] < b]
            subs.setdefault(clip, []).extend(timed_cues_xl(text, ws))
    for i in range(len(video) - 1):
        if video[i]["group"] != video[i + 1]["group"]:
            video[i]["pad_tail"] = 0.4
    video[-1]["pad_tail"] = 0.5
    of_item = next(i for i, v in enumerate(video) if v["src"] == ONLYFANS[0])
    vo_words = json.load(open(PROJ / "assets/analysis/transcript_vo.json", encoding="utf-8"))["VO"]
    vo = []
    for (src, t_in), off, a, b, text in VO:
        k = next(i for i, v in enumerate(video) if v["src"] == src and abs(v["in"] - t_in) < 0.01)
        assert not video[k]["speech"] and off + b - a <= video[k]["out"] - video[k]["in"], (src, t_in)
        vo.append({"src": "VO", "in": a, "out": b, "item": k, "offset": off})
        cues = timed_cues_xl(text, [w for w in vo_words if a - 0.3 <= w["start"] < b])
        cues[0][0] = a + 0.1  # Whisper puts the first word of a memo line late; the cut point is the onset
        subs.setdefault("VO", []).extend(cues)
    music_src = MUSIC.as_posix()
    tl = {
        "tag": "@daisyyyli",
        "tag_at": 0.8,
        "tag_repeats": [{"item": of_item, "offset": round(ONLYFANS[1] - video[of_item]["in"], 3),
                         "note": "'I'd love to see you on my OnlyFans'"}],
        "music": [music_src] * 2,  # 3:10 jazzy track, chained twice (6 s crossfade) under the whole video
        "sources": {**{v["src"]: str(SRC / f"{v['src']}.MOV").replace("\\", "/") for v in video},
                    "VO": (SRC / VO_FILE).as_posix()},
        "video": video,
        "vo": vo,
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False),
                                                       encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"items={len(video)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s")
    for k, cs in subs.items():
        for c in cs:
            print(k, c)


if __name__ == "__main__":
    main()
