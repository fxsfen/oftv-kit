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


def sharp_windows(per_sec, i, o, length, n):
    """n non-overlapping windows of `length` s inside [i, o] with the lowest softness (mean + max of the per-second
    blurdetect values), returned in time order. Defocus / shaky moments (blur > ~9) are avoided."""
    if not per_sec:
        return None
    def score(a):
        vals = per_sec[int(a): max(int(a) + 1, int(a + length + 0.999))]
        return (sum(vals) / len(vals) + max(vals)) if vals else 99
    cands = []
    t = i
    while t + length <= o + 1e-6:
        cands.append((score(t), t))
        t += 0.5
    picked = []
    for sc, t in sorted(cands):
        if all(abs(t - p) >= length + 0.5 for p in picked):
            picked.append(t)
        if len(picked) == n:
            break
    return sorted(picked) if len(picked) == n else None


def refine_span(an, tr, key, a, b):
    """Snap a speech span to the real sound: Whisper word ends land early, so clipped endings were audible.
    End = where the energy after the last word stays below floor+8 dB for 0.15 s (+0.1 s), never into the next word;
    start likewise backwards from the first word."""
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(str(an / "wav16" / f"{key}.wav"), dtype="float32")
    hop = int(sr * 0.02)
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    thr = np.percentile(db, 20) + 8
    ws = [w for w in tr[key] if a - 0.05 <= w["start"] < b]
    if not ws:
        return a, b
    last_end, first_start = max(w["end"] for w in ws), min(w["start"] for w in ws)
    nxt = min([w["start"] for w in tr[key] if w["start"] >= b - 0.05] + [n * 0.02])
    prv = max([w["end"] for w in tr[key] if w["end"] <= a + 0.05] + [0.0])
    i, quiet = int(last_end / 0.02), 0
    while i < n and quiet < 8:
        quiet = quiet + 1 if db[i] < thr else 0
        i += 1
    end = min((i - quiet) * 0.02 + 0.12, nxt - 0.06)
    j, quiet = int(first_start / 0.02), 0
    while j > 0 and quiet < 8:
        quiet = quiet + 1 if db[j] < thr else 0
        j -= 1
    start = max((j + quiet) * 0.02 - 0.1, prv + 0.06)
    return round(min(start, a), 3) if start < a else round(start, 3), round(max(end, b), 3)


def build(proj, cfg):
    an = proj / "assets/analysis"
    S = json.load(open(an / "sources.json", encoding="utf-8"))
    tr = json.load(open(an / "transcripts.json", encoding="utf-8"))
    bp = an / "blur_per_sec.json"   # per-second softness (blurdetect); pieces are taken from the sharpest windows
    blur = json.load(open(bp)) if bp.exists() else None
    video, vo, sections, subs = [], [], [], {}

    def words(key, a, b):
        return [w for w in tr[key] if a - 0.05 <= w["start"] < b]

    def talk(group, key, a, b, text, title=None):
        a, b = refine_span(an, tr, key, a, b)
        if title:
            sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": len(video),
                             "offset": 0.6})
        video.append({"group": group, "src": key, "in": a, "out": min(b, S["dur"][key] - 0.05), "speech": True})
        # extend, never overwrite: intro / VO / outro can all come from ONE recording (lana-bunny C0001)
        subs.setdefault(key, []).extend(timed_cues_xl(text, words(key, a, b)))
        if len(video) > 1 and video[-2]["src"] == key and video[-2]["group"] == group and not video[-2].get("zoom"):
            video[-1]["zoom"] = 1.08   # jump cut inside one take

    for x in (cfg["intro"] if isinstance(cfg["intro"], list) else [cfg["intro"]]):
        talk("intro", *x)
    video[-1]["pad_tail"] = 0.4
    for sc in cfg["scenes"]:
        title, key, spans, text, clips = sc[:5]
        spans = [refine_span(an, tr, key, s_, e_) for s_, e_ in spans]
        extra = sc[5] if len(sc) > 5 else 0.0   # music-only process footage after the voice (length / breathing room)
        need = GAP_LEAD + sum(e - s for s, e in spans) + 0.3 * (len(spans) - 1) + TAIL + extra
        avail = sum(o - i for _, i, o in clips)
        first = len(video)
        if avail >= need:   # trim every shot; long shots become several evenly spaced pieces (shows progress)
            k = need / avail
            for c, i, o in clips:
                L = (o - i) * k
                n = max(1, min(4, int(L // CHUNK))) if (o - i) > 2 * L else 1
                starts = sharp_windows(blur.get(c), i, o, L / n, n) if blur else None
                for j in range(n):
                    mid = i + (o - i) * (j + 0.5) / n
                    a = starts[j] if starts else max(i, min(o - L / n, mid - L / n / 2))
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
