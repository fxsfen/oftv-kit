"""zoey_bee (@zoey_bee), 'монтаж вт': Leeloo (The Fifth Element) Halloween costume, she talks herself (English).
No voice-over recordings arrived, so: keep her speech pieces (retakes / false starts removed), fast-forward the quiet
dressing / wig / combing stretches (muted, speed 2-2.5x, music only), punch-in 1.08 on jump cuts inside one clip.
IMG_1372 = Russian blooper, skipped; the 'doo-doo' humming is skipped. Whisper's 'Thank you' lines are noise."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from subs_util import timed_cues_xl  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
AN = PROJ / "assets/analysis"
SRC = Path(r"C:\Users\fosfe\Downloads") / "монтаж вт" / "zoey_bee"
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"
JUNK = {"Thank you.", "Thank you for watching.", "Thanks for watching!", ""}

# (group, section title or None, clip, a, b, text or None, speed)  text None + speed>1 = fast-forward, muted
EDIT = [
    ("intro", None, "IMG_1366", 1.6, 22.2,   # 0-1.5: she steps back from the phone
     "Hi guys! My name is Zoey B, I'm an OnlyFans model and also an OFTV creator, and today I want to remind you "
     "that very soon it will be a holiday! Now is October, right? And very soon will be Halloween.", 1),
    ("intro", None, "IMG_1366", 31.1, 48.1,
     "And I hope you will celebrate this holiday. And of course you need some costume. "
     "So today I will show you my own costume, and let's see it.", 1),
    ("intro", None, "IMG_1366", 48.8, 60.34,   # ends on 'I will show you'; 'explain everything' runs into a lean to the lens
     "Maybe you will understand what exactly I will wear because of this hair. But maybe no. "
     "So anyway, I will show you.", 1),
    ("intro", None, "IMG_1366", 71.8, 86.4,
     "As you can see, I have this strange thing. And this. At first sight it's nothing, right? "
     "But when I put it on my body, maybe you will understand.", 1),

    ("main", "The Costume", "IMG_1367", 0.8, 4.9, "When you live alone, sometimes it's so hard", 1),   # her first 'to' cut (no 'to to')
    ("main", None, "IMG_1367", 4.9, 12.9, None, 2.0),
    ("main", None, "IMG_1367", 12.9, 15.3, "to wear some dress.", 1),
    ("main", None, "IMG_1367", 15.3, 17.6, None, 2.0),
    ("main", None, "IMG_1367", 17.6, 22.6, "Oh, finally. I get it.", 1),
    ("main", None, "IMG_1367", 22.6, 31.9, None, 2.0),
    ("main", None, "IMG_1367", 31.9, 47.95,   # 'it's not, that's not all' stutter + walk to the camera cut
     "Nice. Of course, I have some underwear, beige underwear, because without it I wouldn't feel comfortable. "
     "Okay, nice.", 1),
    ("main", None, "IMG_1367", 52.3, 64.2,
     "This skirt I put here. Maybe you already can understand which movie this costume is from.", 1),
    ("main", None, "IMG_1367", 65.2, 76.7,
     "And I want to tell you, I bought this material myself and brought it to a tailor, and she created it for me.", 1),

    ("main", "The Wig", "IMG_1368", 7.9, 11.15, "As you can see, I have a wig,", 1),
    ("main", None, "IMG_1368", 19.4, 21.0, "red hair.", 1),   # 'and of course this thing / of course...' repeat cut
    ("main", None, "IMG_1368", 26.4, 41.3,
     "Of course I don't need this thing in this part of my head. I need to put it lower, "
     "maximum lower, as low as possible.", 1),
    ("main", None, "IMG_1368", 41.3, 56.4, None, 2.0),
    ("main", None, "IMG_1368", 59.7, 81.6, None, 2.5),
    ("main", None, "IMG_1368", 81.6, 85.6, "Oh my God, too messy.", 1),   # 85.8+: face right in the lens
    ("main", None, "IMG_1368", 96.9, 107.3, None, 2.0),

    ("main", "Final Touches", "IMG_1369", 0.0, 27.4, None, 2.5),
    ("main", None, "IMG_1369", 27.4, 39.2, "Now it's better. Maybe I need to cut a little bit of this fringe.", 1),
    ("main", None, "IMG_1369", 39.2, 59.9, None, 2.5),
    ("main", None, "IMG_1369", 59.9, 65.9, "Like this. It's too sexy, but I can see.", 1),
    ("main", None, "IMG_1369", 65.9, 82.9, None, 2.5),
    ("main", None, "IMG_1369", 82.9, 84.7, "I need my gun.", 1),
    ("main", None, "IMG_1369", 88.3, 105.7,
     "I like this costume, to be honest. Yes, I wore it already last year, but it doesn't matter. "
     "I spent too much time and too much love on this costume, so I want to use it one more time. Why not?", 1),
    ("main", None, "IMG_1369", 112.5, 121.5, None, 2.0),   # 105-112 / 122+: leaning in
    ("main", None, "IMG_1369", 122.9, 125.2, "So, do you like it?", 1),

    # the pumpkin delivery (IMG_1370) is cut out completely (user, 2026-10-23)

    ("outro", "Final Thoughts", "IMG_1369", 159.9, 165.7, "So guys, please guess which movie this costume is from,", 1),
    ("outro", None, "IMG_1369", 178.2, 184.2, "and please tell me which costume you will wear to a Halloween party.", 1),
    ("outro", None, "IMG_1369", 189.0, 204.0,
     "Thank you so much for watching this video. I hope you like my style, I hope you like my look, "
     "and I want to remind you: I'm Zoey B, I'm an OnlyFans model and also an OFTV creator.", 1),
    ("outro", None, "IMG_1371", 2.1, 12.6,   # 12.9+: walks to the phone
     "If you want to see more of my lifestyle or exclusive content, please subscribe to my OnlyFans, "
     "and see you in the next video. Bye!", 1),
]
ONLYFANS_WORD = ("IMG_1371", "OmniFans")   # whisper's spelling of 'OnlyFans' in the subscribe line
MUSIC = ["HoliznaCC0 - Ghost Town.mp3", "HoliznaCC0 - Doodles(LoFi, Happy).mp3", "HoliznaCC0 - Warm Fuzz(LoFi, Retro).mp3"]


def main():
    tr = json.load(open(AN / "transcripts.json", encoding="utf-8"))
    ph = json.load(open(AN / "phrases.json", encoding="utf-8"))
    junk = {k: [(p["a"], p["b"]) for p in v if p["t"].strip() in JUNK] for k, v in ph.items()}
    dur = {}
    video, sections, subs = [], [], {}
    prev = None
    for group, title, clip, a, b, text, speed in EDIT:
        if clip not in dur:
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(SRC / f"{clip}.MOV")], capture_output=True, text=True)
            dur[clip] = float(r.stdout)
        b = min(b, dur[clip] - 0.05)
        if title:
            sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": len(video),
                             "offset": 0.6 if group == "outro" else 0.2})
        it = {"group": group, "src": clip, "in": a, "out": round(b, 3)}
        if text:
            it["speech"] = True
            ws = [w for w in tr[clip] if a - 0.05 <= w["start"] < b
                  and not any(s - 0.01 <= w["start"] < e for s, e in junk.get(clip, []))]
            subs.setdefault(clip, []).extend(timed_cues_xl(text, ws))
        else:
            it["speed"] = speed
        # jump cut inside the same clip -> alternate a 1.08 punch-in so the cut reads as intended
        if prev and prev["src"] == clip and prev["group"] == group and not prev.get("zoom"):
            it["zoom"] = 1.08
        video.append(it)
        prev = it
    first_main = next(i for i, v in enumerate(video) if v["group"] == "main")
    first_out = next(i for i, v in enumerate(video) if v["group"] == "outro")
    video[first_main - 1]["pad_tail"] = 0.4
    video[first_out]["pad_head"] = 0.4
    video[-1]["pad_tail"] = 0.8
    last = len(video) - 1
    of = next(w["start"] for w in tr[ONLYFANS_WORD[0]] if ONLYFANS_WORD[1] in w["word"])
    tl = {
        "tag": "@zoey_bee",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": round(of - video[last]["in"], 3),
                         "note": "'please subscribe to my OnlyFans'"}],
        "music": [str(LOFI / m).replace("\\", "/") for m in MUSIC],
        "sources": {c: str(SRC / f"{c}.MOV").replace("\\", "/") for c in {v["src"] for v in video}},
        "video": video,
        "vo": [],
        "sections": sections,
        "word_edits": {},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (AN / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum((v["out"] - v["in"]) / v.get("speed", 1) + v.get("pad_tail", 0) + v.get("pad_head", 0)
              for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    print(f"items={len(video)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s "
          f"longest_cue={len(longest[2])} onlyfans_at={of}")


if __name__ == "__main__":
    main()
