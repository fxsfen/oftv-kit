"""Timeline for 'What's in my makeup bag' (@aisha_noor), Downloads/ее IMG_8032..8067.

Single-sentence Spanish talking takes (same beige-wall setup). Spanish voice kept, English
subtitles = hand translation (one line <= 32 chars), English plates.
Intro -> six parts -> final thoughts; whips only intro->main and main->outro.
Jump cuts inside a part alternate a 1.08 punch-in.
Writes artifacts/timeline.json and assets/analysis/subs_en.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from subs_util import timed_cues_xl  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
SRC = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "ее"][0]
TALK_IN, TALK_OUT = 0.3, 0.35
ZOOM = 1.08

# (clip, group, section title or None, in override, out override, English text)
CLIPS = [
    ("IMG_8032", "intro", None, 0.0, None,
     "Hi everyone, welcome back to my channel! I'm Aisha, an OnlyFans model and a content creator, "
     "and today we're taking a look at something I always carry with me."),
    ("IMG_8033", "intro", None, None, None,
     "Today I'll show you what I keep in my makeup bag and which products are my favorites."),
    ("IMG_8034", "intro", None, None, None,
     "I don't usually carry all my makeup with me, but I always have things that end up being useful."),
    ("IMG_8035", "intro", None, None, None, "So let's open it up and see what's inside."),
    ("IMG_8036", "main", "The Bag", None, None,
     "Okay, this is my makeup bag. I like it small and easy to carry, "
     "but it's really important that everything I need fits."),
    ("IMG_8037", "main", None, None, None, "But it has to have enough room for everything important."),
    ("IMG_8039", "main", None, None, None,
     "Sometimes I change the products depending on where I'm going, but these are the ones I use the most."),
    ("IMG_8042", "main", "Fresh Skin", None, None,
     "I like a concealer that looks pretty natural and doesn't feel too heavy on the skin."),
    ("IMG_8043", "main", None, None, None,
     "I don't always wear a lot of makeup. Sometimes a good base and a good concealer are enough."),
    ("IMG_8044", "main", None, None, None,
     "Next, we have the products that bring a little more life to the face."),
    ("IMG_8045", "main", None, None, None,
     "I always carry powder, because I really like keeping my skin fresh and not too shiny during the day."),
    ("IMG_8048", "main", None, None, None,
     "I also carry blush, and I love it because just a little can change the whole look of your face."),
    ("IMG_8049", "main", None, None, None,
     "And of course, highlighter. I love when the skin has a pretty, natural glow."),
    ("IMG_8050", "main", "Eyes & Brows", None, None,
     "Now let's move on to mascara. I use this one, it's probably one of the products I use the most."),
    ("IMG_8051", "main", None, None, None,
     "Even when I don't want a full makeup look, a little mascara makes my eyes look so much more awake."),
    ("IMG_8052", "main", None, None, None,
     "I also carry a brow pencil or gel. I like to fill them in, but still keep them a little natural."),
    ("IMG_8053", "main", None, None, None, "I like to keep them defined, but natural."),
    ("IMG_8054", "main", None, None, None,
     "And sometimes I use a little eyeliner when I want a slightly more intense look."),
    ("IMG_8055", "main", "Lips", None, None,
     "And obviously, we can't forget the lips. I always carry some lip product: "
     "it can be a liner, a gloss or a lipstick."),
    ("IMG_8056", "main", None, None, None, "I like to change the color depending on my look or my mood."),
    ("IMG_8057", "main", None, None, None,
     "A light color always works well for the day, and a slightly darker one "
     "can completely transform your look for the night."),
    ("IMG_8058", "main", "Little Tools", None, None,
     "I also carry a few small tools that make everything easier."),
    ("IMG_9335", "main", None, None, None,
     "For example, a tiny mirror, a brush, a little sponge and, if I have room, a setting spray."),
    ("IMG_8059", "main", None, None, None,
     "They don't look like much, but together they make my makeup bag so much more useful."),
    ("IMG_8060", "main", "My Favorite", None, None,
     "If I had to pick one favorite product from my bag, it would probably be this one: my lip liner. I love it."),
    ("IMG_8061", "main", None, None, None,
     "It's one of those products I always end up using, even when I try to carry fewer things."),
    ("IMG_8062", "outro", "Final Thoughts", None, None,
     "So that was a little look inside my makeup bag. Now you know some of the things "
     "I always like to carry with me."),
    ("IMG_8065", "outro", None, None, None,
     "I don't need to carry a lot of products to feel ready, just a few of my favorites and some basics."),
    ("IMG_8066", "outro", None, None, None,
     "I hope you enjoyed this little look at my beauty routine. Thank you so much for spending "
     "this time with me. See you in the next video."),
    ("IMG_8067", "outro", None, None, None,
     "If you'd like to get to know me a little more and see more of my personal content, "
     "you can subscribe to my OnlyFans. See you soon, bye!"),
]
EXTRA = json.loads((PROJ / "assets/analysis/extra_clips.json").read_text(encoding="utf-8")) \
    if (PROJ / "assets/analysis/extra_clips.json").exists() else []
ONLYFANS = ("IMG_8067", 5.72)
MUSIC = ["Sound Of Freedom - Lo-Fi R&B Vibe.mp3.mp3", "Sound Of Freedom - Jazzy Rhodes Deep House.mp3.mp3"]


def main():
    tr = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
    tr.update(json.load(open(PROJ / "assets/analysis/transcripts_extra.json", encoding="utf-8")))
    bounds = json.load(open(PROJ / "assets/analysis/speech_bounds.json", encoding="utf-8"))
    clips = list(CLIPS)
    for e in EXTRA:  # [after_clip, clip, text]
        k = next(i for i, c in enumerate(clips) if c[0] == e[0]) + 1
        clips.insert(k, (e[1], clips[k - 1][1], None, e[2] if len(e) > 3 else None, None, e[-1]))
    video, sections, subs = [], [], {}
    prev_group, z = None, False
    for clip, group, title, a, b, text in clips:
        bd, ws = bounds[clip], tr[clip]
        first = ws[0]["start"] if ws[0]["start"] > 0.05 else bd["speech_in"]
        s_in = a if a is not None else max(0.0, min(bd["speech_in"], first) - TALK_IN)
        s_out = b if b is not None else min(bd["dur"], max(bd["speech_out"], ws[-1]["end"]) + TALK_OUT)
        z = False if (group != prev_group or title) else not z
        it = {"group": group, "src": clip, "in": round(s_in, 3), "out": round(s_out, 3), "speech": True}
        if z:
            it["zoom"] = ZOOM
        if title:
            sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": len(video),
                             "offset": 0.15})
        video.append(it)
        prev_group = group
        subs[clip] = timed_cues_xl(text, ws)
    for i in range(len(video) - 1):
        if video[i]["group"] != video[i + 1]["group"]:
            video[i]["pad_tail"] = 0.4
    video[-1]["pad_tail"] = 1.0
    of_item = next(i for i, v in enumerate(video) if v["src"] == ONLYFANS[0])
    tl = {
        "tag": "@aisha_noor",
        "tag_at": 0.8,
        "tag_repeats": [{"item": of_item, "offset": round(ONLYFANS[1] - video[of_item]["in"], 3),
                         "note": "'pueden suscribirse a mi OnlyFans'"}],
        "music": [str(SRC / m).replace("\\", "/") for m in MUSIC],
        "sources": {v["src"]: str(SRC / f"{v['src']}.MOV").replace("\\", "/") for v in video},
        "video": video,
        "vo": [],
        "sections": sections,
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "assets/analysis/subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False),
                                                       encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"items={len(video)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s "
          f"longest_cue={len(longest[2])} '{longest[2]}'")


if __name__ == "__main__":
    main()
