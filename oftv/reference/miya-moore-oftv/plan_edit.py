"""Build the edit plan (EDL) for the Miya Moore OFTV talking-head edit.

Inputs : assets/analysis/transcript_novad.json, assets/audio/speech_16k.wav
Output : artifacts/edit_plan.json  (segments in source time + output time,
         removed ranges with reasons, review flags, section markers)

Editorial decisions (which takes to keep) live in KEEP / REMOVE below so a
single choice can be changed and the plan regenerated.
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
FPS = 30
HOP = 0.01                 # energy frame (s)
SIL_DB = -47.0             # below this = silence (noise floor ~ -56 dBFS)
MAX_PAUSE = 0.80           # pauses longer than this get shortened
KEEP_PAUSE = 0.45          # ...down to this
EDGE_PAD = 0.12            # minimum breath kept around speech at hard cuts

# --- Editorial decisions (source seconds) ---------------------------------
# Groups are joined by whip transitions; cuts inside a group are hard cuts.
GROUPS = {
    # Group tails/heads carry >= XF of real silence so the whip never eats speech.
    "intro": [(27.75, 58.40)],
    "main": [(57.85, 111.75), (126.40, 258.68), (277.60, 278.10)],  # last = 0.5 s room-tone filler
    "outro": [(279.60, 287.62), (288.20, 306.25), (318.25, 365.10)],
}
REMOVED = [
    (0.00, 27.75, "Intro take 1 — abandoned mid-sentence ('the things I...'); take 2 kept", "auto"),
    (111.75, 126.40, "False start 'I'm no longer thinking about…' + 11.6 s pause; retake kept", "auto"),
    (258.68, 279.60, "First take of 'So if I had to explain…' — stumbles ('convenience… the election'); retake kept", "auto"),
    (287.62, 288.20, "Stray 'it's' before 'It combines'", "auto"),
    (306.25, 318.25, "Background noise + 'Sorry about the noise' aside", "auto"),
]
FLAGS = [
    (27.06, "Intro take 2: Whisper heard the name as 'Nyambor' — check she says 'Miya Moore' clearly. Take 1 (2.6 s) has a clean name but breaks off."),
    (42.68, "'enjoy. joy.' — possible double word; left untouched."),
    (141.04, "'helps helps me' — possible stutter; left untouched (cut would be < 0.2 s)."),
    (341.40, "'my lifestyle style, creative projects' — slip of tongue; left untouched."),
]
SECTIONS = [  # (source time, title) — plate appears at the start of that line
    (58.42, "My Creative Escape"),
    (83.60, "Slowing Down"),
    (159.82, "Freedom to Create"),
    (211.40, "Sharing What I Learn"),
    (280.14, "Final Thoughts"),
]
TAG = {"text": "@miya_moore", "start": 0.8, "duration": 5.5}


def load_energy(path):
    w = wave.open(str(path))
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(sr * HOP)
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


def silences(db, a, b):
    """Silent runs inside [a, b] longer than MAX_PAUSE."""
    i0, i1 = int(a / HOP), int(b / HOP)
    quiet = db[i0:i1] < SIL_DB
    out, st = [], None
    for k, q in enumerate(quiet):
        t = (i0 + k) * HOP
        if q and st is None:
            st = t
        elif not q and st is not None:
            if t - st > MAX_PAUSE:
                out.append((st, t))
            st = None
    return out


def snap(t):
    return round(round(t * FPS) / FPS, 4)


def main():
    db = load_energy(PROJ / "assets/audio/speech_16k.wav")
    segments, out_t = [], 0.0
    for group, ranges in GROUPS.items():
        for a, b in ranges:
            pieces, cur = [], a
            for s, e in silences(db, a, b):
                # never touch silence that touches the range edges (those are cut points)
                if s - a < 0.05 or b - e < 0.05:
                    continue
                trim = (e - s) - KEEP_PAUSE
                pieces.append((cur, s + KEEP_PAUSE / 2))
                cur = e - KEEP_PAUSE / 2
                assert trim > 0
            pieces.append((cur, b))
            for s, e in pieces:
                s, e = snap(s), snap(e)
                if e - s < 2 / FPS:
                    continue
                segments.append({"group": group, "src_in": s, "src_out": e,
                                 "out_in": round(out_t, 4), "out_out": round(out_t + e - s, 4)})
                out_t += e - s

    def to_out(t):
        for sg in segments:
            if sg["src_in"] - 0.5 <= t <= sg["src_out"]:
                return round(sg["out_in"] + max(0.0, t - sg["src_in"]), 3)
        return None

    pauses_trimmed = sum(
        1 for i in range(1, len(segments)) if segments[i]["group"] == segments[i - 1]["group"]
        and segments[i]["src_in"] - segments[i - 1]["src_out"] < MAX_PAUSE + 20
    )
    plan = {
        "source": "C:/Users/fosfe/Downloads/IMG_1894.MOV",
        "fps": FPS,
        "segments": segments,
        "groups": list(GROUPS),
        "removed": [{"src_in": a, "src_out": b, "reason": r, "mode": m} for a, b, r, m in REMOVED],
        "review_flags": [{"src_t": t, "out_t": to_out(t), "note": n} for t, n in FLAGS],
        "sections": [{"index": i + 1, "title": ti, "src_t": t, "out_t": to_out(t)} for i, (t, ti) in enumerate(SECTIONS)],
        "tag": TAG,
        "stats": {"source_s": 367.36, "output_s_before_transitions": round(out_t, 2),
                  "segments": len(segments), "internal_cuts": pauses_trimmed},
    }
    dst = PROJ / "artifacts/edit_plan.json"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(plan["stats"]))
    for s in plan["sections"]:
        print("section", s)
    for f in plan["review_flags"]:
        print("flag", f["out_t"], f["note"][:70])


if __name__ == "__main__":
    sys.exit(main())


