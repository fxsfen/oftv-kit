"""Timeline for @zoey_bee 'strangest Halloween dream' — an already edited 4K
talking-head (zzz.mp4) with baked-in picture-in-picture 'dream' inserts.

We only remove retakes (kept ranges below, boundaries from the phrase-level
large-v3 pass + 0.12 s fine split) and never cut or zoom inside a dream insert
(assets/analysis/overlays.json: 30.2-40.2, 156.0-166.1, 179.7-189.7). Jump cuts
on the static shot alternate a 1.08 punch-in, but only on pieces without an insert
(a crop would cut the PiP in the top-left corner).
"""
import json
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
SRC = "C:/Users/fosfe/Downloads/Новая папка (15)/zzz.mp4"
Z = 1.08

# (group, in, out, zoom, pad_tail)
PIECES = [
    ("intro", 0.00, 11.88, None, 0.5),     # "Hi OFTV ... strangest Halloween dream I've ever had."
    ("main", 11.88, 22.10, Z, None),        # cut: "And I was... very / and I was wearing this." (22.1-26.7)
    ("main", 26.70, 50.80, None, None),     # dream insert 30.2-40.2 inside -> no zoom
    ("main", 53.20, 66.45, Z, None),        # cut: 2nd "and everyone was wearing costumes" (50.8-53.2)
    ("main", 70.55, 122.55, None, None),    # cut: "And somehow, it felt completely normal" first take (66.45-70.55)
    ("main", 125.45, 154.25, Z, None),      # cut: "Honestly, I think pretty cool." take 1 (122.55-125.45)
    ("main", 154.25, 174.15, None, None),   # split in the pause before the insert 156-166 (no zoom there)
    ("main", 174.95, 179.40, Z, None),      # cut: stray "Oh" (174.15-174.95)
    ("main", 179.40, 233.60, None, 0.5),    # insert 179.7-189.7 inside
    ("outro", 233.60, 266.25, None, 0.7),   # "So that was my weird little Halloween dream ... Bye!"
]
SECTIONS = [  # (source time, title)
    (28.70, "Lost at a Party"),
    (73.50, "Everyone Knew Me"),
    (125.55, "The Mysterious Door"),
    (197.20, "Waking Up"),
    (233.80, "Final Thoughts"),
]
TAG_END_SRC = 260.40  # "You can always find me on my OnlyFans"


def main():
    overlays = json.load(open(PROJ / "assets/analysis/overlays.json"))
    video = []
    for g, a, b, z, pad in PIECES:
        if z:
            assert not any(o0 < b and o1 > a for o0, o1 in overlays if o1 - o0 > 1), (a, b)
        it = {"group": g, "src": "zzz", "in": a, "out": b, "speech": True}
        if z:
            it["zoom"] = z
        if pad:
            it["pad_tail"] = pad
        video.append(it)

    def anchor(t):
        for i, it in enumerate(video):
            if it["in"] - 0.01 <= t < it["out"]:
                return {"item": i, "offset": round(t - it["in"], 3)}
        raise ValueError(t)

    sections = [{"index": k + 1, "label": "Part", "title": ti, **anchor(t)} for k, (t, ti) in enumerate(SECTIONS)]
    for s in sections:
        s["chapter"] = s["title"]
    tl = {
        "tag": "@zoey_bee",
        "tag_at": 0.8,
        "tag_repeats": [{**anchor(TAG_END_SRC), "note": "'You can always find me on my OnlyFans'"}],
        "music": ["C:/Users/fosfe/Downloads/Новая папка (15)/HoliznaPATREON - halloween.mp3",
                  "C:/Users/fosfe/Downloads/Новая папка (15)/Soundore - Halloween.mp3"],
        "sources": {"zzz": SRC},
        "transcript_keys": {"zzz": "zzz"},
        "video": video,
        "vo": [],
        "sections": sections,
        "word_edits": {},
    }
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(v["out"] - v["in"] + v.get("pad_tail", 0) for v in video) - 1.0
    print(f"items={len(video)} sections={[s['title'] for s in sections]} ~duration={tot:.1f}s")


if __name__ == "__main__":
    main()

