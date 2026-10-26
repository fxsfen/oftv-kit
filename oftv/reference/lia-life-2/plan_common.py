"""Shared planner for Bela Cruz 'Guion' videos (bela-cruz-29 / -30).

Structure of every Guion folder: ESC 1 = on-camera intro (one take), ESC 2-6 = silent-ish takes + one Spanish
voice note per scene (VOZ EN OFF), ESC 7 = on-camera outro. Spanish voice kept (recorded on the RIGHT channel
only -> speech_channel 1), English subtitles = hand translation timed from the Spanish words (timed_cues_xl),
English plates. B-roll of each scene is trimmed (or slowed, never below MIN_SPEED) to fit its voice note.
"""
import json
from pathlib import Path

from subs_util import timed_cues_xl

GAP_LEAD, TAIL = 0.5, 0.6
MIN_SPEED = 0.75
CHUNK = 3.5   # min seconds per piece when a long shot is split


def build(proj, cfg):
    an = proj / "assets/analysis"
    S = json.load(open(an / "sources.json", encoding="utf-8"))
    tr = json.load(open(an / "transcripts.json", encoding="utf-8"))
    video, vo, sections, subs = [], [], [], {}

    def words(key, a, b):
        return [w for w in tr[key] if a - 0.05 <= w["start"] < b]

    def talk(group, key, a, b, text, title=None):
        if title:
            sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": len(video),
                             "offset": 0.6})
        video.append({"group": group, "src": key, "in": a, "out": min(b, S["dur"][key] - 0.05), "speech": True})
        subs[key] = timed_cues_xl(text, words(key, a, b))

    for x in (cfg["intro"] if isinstance(cfg["intro"], list) else [cfg["intro"]]):
        talk("intro", *x)
    video[-1]["pad_tail"] = 0.4
    for title, key, spans, text, clips in cfg["scenes"]:
        need = GAP_LEAD + sum(e - s for s, e in spans) + 0.3 * (len(spans) - 1) + TAIL
        avail = sum(o - i for _, i, o in clips)
        first = len(video)
        if avail >= need:   # trim every shot; long shots become several evenly spaced pieces (shows progress)
            k = need / avail
            for c, i, o in clips:
                L = (o - i) * k
                n = max(1, min(4, int(L // CHUNK))) if (o - i) > 2 * L else 1
                for j in range(n):
                    mid = i + (o - i) * (j + 0.5) / n
                    a = max(i, min(o - L / n, mid - L / n / 2))
                    video.append({"group": "main", "src": c, "in": round(a, 3), "out": round(a + L / n, 3)})
        else:               # not enough footage: gentle slow-mo
            sp = round(avail / need, 4)
            assert sp >= MIN_SPEED, (title, sp)
            for c, i, o in clips:
                video.append({"group": "main", "src": c, "in": i, "out": o, "speed": sp})
        t = GAP_LEAD
        for s, e in spans:
            vo.append({"src": key, "in": s, "out": e, "item": first, "offset": round(t, 3)})
            t += (e - s) + 0.3
        allw = [w for s, e in spans for w in words(key, s, e)]
        subs.setdefault(key, []).extend(timed_cues_xl(text, allw))
        sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": first, "offset": 0.15})
    outs = cfg["outro"] if isinstance(cfg["outro"], list) else [cfg["outro"]]
    for n_o, x in enumerate(outs):
        talk("outro", *x, title="Final Thoughts" if n_o == 0 else None)
        if n_o == 0:
            video[-1]["pad_head"] = 0.3
    video[-1]["pad_tail"] = 0.8
    last = len(video) - 1
    srcs = {v["src"] for v in video} | {x["src"] for x in vo}
    tl = {
        "tag": cfg["tag"],
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": round((0.3 if len(outs) == 1 else 0.0) + cfg["onlyfans_at"]
                                                       - video[last]["in"], 3),
                         "note": "'pueden suscribirse a mi OnlyFans'"}],
        "speech_channel": cfg.get("speech_channel"),
        "music": cfg["music"],
        "sources": {c: S["sources"][c] for c in srcs},
        "video": video,
        "vo": vo,
        "sections": sections,
        "word_edits": {},
    }
    (proj / "artifacts").mkdir(exist_ok=True)
    (proj / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    (an / "subs_en.json").write_text(json.dumps(subs, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum((v["out"] - v["in"]) / v.get("speed", 1) + v.get("pad_tail", 0) + v.get("pad_head", 0)
              for v in video) - 1.0
    longest = max((c for v in subs.values() for c in v), key=lambda c: len(c[2]))
    print(f"items={len(video)} vo={len(vo)} sections={[s['title'] for s in sections]} "
          f"speeds={sorted({v.get('speed', 1) for v in video})} ~duration={tot:.1f}s longest_cue={len(longest[2])}")
