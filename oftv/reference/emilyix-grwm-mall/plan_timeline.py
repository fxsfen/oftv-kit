"""emilyix (@emilyix), 'домонтаж' VIDEO 1 of 4: GRWM -> taxi -> mall -> aquarium (no try-ons; those are videos 2-4).
The original shoot has no talking at all. She later filmed the hello (IMG_8461/8464/8466) and goodbye
(IMG_8468/8472/8473, says OnlyFans) on camera and sent 19 voice notes for the VO ('get ready' folder -> gr01..gr19,
script lines 4-8 and 13-26; she skipped 9-12, so brow gel / perfume / shoes play music-only).
Each voice note is one beat over hand-picked shots; a beat's shots are trimmed (centred) or slowed (>= MIN_SPEED)
to fit its line. No shared shots with videos 2-4 (store / try-on clips 8137+ are left out)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_common import refine_span  # noqa: E402
from subs_util import timed_cues_xl  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
AN = PROJ / "assets/analysis"
LOFI = Path(__file__).resolve().parents[3] / "music_library" / "lofi"
LEAD, TAIL, MIN_SPEED = 0.3, 0.45, 0.75

INTRO = [
    ("IMG_8461", "Hi guys, it's Emily, and welcome back!"),
    ("IMG_8464", "Today I have a slow, cozy day planned. I'm going to the mall, and I'm taking you with me."),
    ("IMG_8466", "But first, let's get ready together!"),
]
# (section title or None, voice note or None for music-only, subtitle text, [(clip, in, out), ...])
BEATS = [
    ("Getting Ready", "gr01", "My outfit for today is super simple: a black top, black leggings, and my favorite cozy vest.",
     [("IMG_8093", 0.3, 13.0)]),
    (None, "gr02", "I swear this vest goes with literally everything this season.", [("IMG_8097", 0.5, 24.5)]),
    (None, "gr03", "A quick brush through my hair. I like it straight and sleek.", [("IMG_8098", 3.0, 14.0)]),
    (None, "gr04", "And of course, coffee. I can't leave the house without it.", [("IMG_8098", 14.5, 21.3)]),
    (None, "gr05", "A little lip balm. My lips get so dry when it's cold outside.", [("IMG_8099", 0.0, 10.0)]),
    (None, None, "", [("IMG_8099", 10.0, 17.1), ("IMG_8102", 0.2, 3.7), ("IMG_8105", 0.0, 5.0)]),
    ("On the Way", "gr06", "I'm taking a taxi today, because the weather is so grey and cold.", [("IMG_8109", 0.0, 4.8)]),
    (None, "gr07", "I love this little ride through the city. Music in my ears, and autumn trees outside the window.",
     [("IMG_8109", 4.8, 8.0), ("IMG_8110", 0.0, 5.6)]),
    (None, ("gr08", "gr09"), ("Autumn here is so beautiful, even when it's cloudy.", "And here we are!"),
     [("IMG_8112", 0.0, 2.95), ("IMG_8113", 0.0, 2.65), ("IMG_8116", 3.4, 5.15)]),
    (None, "gr10", "Okay, let's go inside. It's freezing today!", [("IMG_8116", 0.0, 3.4), ("IMG_8117", 0.0, 5.7)]),
    ("The Mall", "gr11", "I love coming here on a weekday. It's so calm and quiet.",
     [("IMG_8118", 0.0, 3.4), ("IMG_8120", 0.0, 4.6)]),
    (None, "gr12", "The escalator, the glass roof, and the lights... It always puts me in a good mood.",
     [("IMG_8119", 0.0, 4.2), ("IMG_8124", 0.0, 2.95)]),
    (None, "gr13", "So many stores. I already know I'm going to spend way too much time here.",
     [("IMG_8122", 0.0, 5.35), ("IMG_8123", 0.0, 3.55)]),
    # one beat for the whole aquarium: 34 s of lines over 32 s of fish -> uniform slow-mo, shots in line order
    ("The Aquarium", ("gr14", "gr15", "gr16", "gr17", "gr18", "gr19"),
     ("But first, my favorite part of the whole place: the giant aquarium!",
      "Every time I come here, I stop for at least five minutes just to watch the fish.",
      "Look at this one! He is so big and so serious.",
      "And these little ones swim together like one big cloud.",
      "Honestly, it feels like a little piece of the ocean in the middle of the city.",
      "It's so calming. I could stay here for hours."),
     [("IMG_8133", 0.0, 5.2), ("IMG_8126", 0.0, 7.85), ("IMG_8127", 4.6, 8.8), ("IMG_8132", 0.0, 4.4),
      ("IMG_8127", 0.0, 4.6), ("IMG_8135", 0.0, 5.35)]),
]
OUTRO = [
    ("IMG_8468", "That was my little cozy day. Slow, calm, and exactly what I need."),
    ("IMG_8472", "Thank you so much for spending it with me."),
    ("IMG_8473", "If you want to see more of me, you can find me on my OnlyFans. Bye-bye! See you in the next video!"),
]


def main():
    S = json.load(open(AN / "sources.json", encoding="utf-8"))
    tr = json.load(open(AN / "transcripts.json", encoding="utf-8"))
    video, vo, sections, subs = [], [], [], {}

    def talk(group, key, text, title=None):
        ws = tr[key]
        a, b = refine_span(AN, tr, key, ws[0]["start"], ws[-1]["end"])
        if title:
            sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": len(video), "offset": 0.6})
        video.append({"group": group, "src": key, "in": max(0.0, a), "out": min(b, S["dur"][key] - 0.05), "speech": True})
        subs.setdefault(key, []).extend(timed_cues_xl(text, ws))

    for key, text in INTRO:
        talk("intro", key, text)
    video[1]["zoom"] = 1.08      # three takes from one tripod position: punch in on the middle one
    video[-1]["pad_tail"] = 0.4
    for title, key, text, clips in BEATS:
        first = len(video)
        avail = sum(o - i for _, i, o in clips)
        if key is None:          # music-only shots
            need = avail
        else:
            keys, texts = (key, text) if isinstance(key, tuple) else ((key,), (text,))
            t = LEAD          # several short notes can share one beat, 0.35 s apart
            for kk, tx in zip(keys, texts):
                ws = tr[kk]
                s, e = refine_span(AN, tr, kk, ws[0]["start"], ws[-1]["end"])
                e = min(e, S["dur"][kk] - 0.02)
                vo.append({"src": kk, "in": s, "out": e, "item": first, "offset": round(t, 3)})
                subs.setdefault(kk, []).extend(timed_cues_xl(tx, ws))
                t += (e - s) + 0.35
            need = t - 0.35 + TAIL
        if avail >= need:        # trim every shot around its centre
            k = need / avail
            for c, i, o in clips:
                L, mid = (o - i) * k, (i + o) / 2
                video.append({"group": "main", "src": c, "in": round(mid - L / 2, 3), "out": round(mid + L / 2, 3)})
        else:                    # not enough footage: gentle slow-mo on the whole beat
            sp = round(avail / need, 4)
            assert sp >= MIN_SPEED, (key, sp)
            for c, i, o in clips:
                video.append({"group": "main", "src": c, "in": i, "out": o, "speed": sp})
        if title:
            sections.append({"index": len(sections) + 1, "label": "Part", "title": title, "item": first, "offset": 0.15})
    for n, (key, text) in enumerate(OUTRO):
        talk("outro", key, text, title="Final Thoughts" if n == 0 else None)
        if n == 0:
            video[-1]["pad_head"] = 0.3
    video[-2]["zoom"] = 1.08
    # end on her wave after "next video" (IMG_8473 ~11.5-12.3 s), before she reaches for the phone
    video[-1]["out"] = min(S["dur"]["IMG_8473"] - 0.05, max(video[-1]["out"], WAVE_END))
    ws = tr["IMG_8473"]   # "...find me on my OnlyFans" (Whisper: "on my on the fence") -> the word after "my"
    of = ws[next(k for k, w in enumerate(ws) if w["word"].strip().lower() == "my") + 1]["start"]
    last = len(video) - 1
    srcs = {v["src"] for v in video} | {x["src"] for x in vo}
    tl = {
        "tag": "@emilyix",
        "tag_at": 0.8,
        "tag_repeats": [{"item": last, "offset": round(of - video[last]["in"], 3), "note": "'on my OnlyFans'"}],
        "music": [str(LOFI / "HoliznaCC0 - Tokyo Sunset(Lofi, Peaceful, Soft).mp3").replace("\\", "/"),
                  str(LOFI / "HoliznaCC0 - Wetlands(Lofi, Calm, Relaxed).mp3").replace("\\", "/")],
        "sources": {c: S["sources"][c] for c in srcs},
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
    print(f"items={len(video)} vo={len(vo)} sections={[s['title'] for s in sections]} "
          f"speeds={sorted({v.get('speed', 1) for v in video})} ~duration={tot:.1f}s longest_cue={len(longest[2])}")


WAVE_END = 12.4

if __name__ == "__main__":
    main()
