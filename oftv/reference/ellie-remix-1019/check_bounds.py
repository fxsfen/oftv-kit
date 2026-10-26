"""Print voc-transcript words and vocal pauses around every edit-map boundary."""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf
sys.path.insert(0, str(Path(__file__).parent))
from render_remix import vocal_env, quiet_runs, merged_segments, PROJ
em = json.load(open(PROJ / "artifacts/edit_map.json", encoding="utf-8"))
keys = sys.argv[1:] or ["A", "B"]
W = {k: json.load(open(PROJ / f"assets/analysis/transcript_{k}_voc.json", encoding="utf-8"))["words"] for k in keys}
R = {k: quiet_runs(vocal_env(k)) for k in keys}
def ctx(k, t, a, b):
    ws = " ".join(f"{w['word'].strip()}[{w['start']:.2f}-{w['end']:.2f}]" for w in W[k] if t - a <= w["start"] <= t + b)
    gs = " ".join(f"({g0:.2f}-{g1:.2f})" for g0, g1 in R[k] if t - a <= g1 and g0 <= t + b)
    return ws + "\n      gaps: " + gs
for i, s in enumerate(merged_segments(em["segments"])):
    if s["src"] not in keys: continue
    print(f"#{i} {s['src']} s={s['s']} e={s['e']}  {s['text'][:60]}")
    print("   IN :", ctx(s["src"], s["s"], 1.5, 1.0))
    print("   OUT:", ctx(s["src"], s["e"], 1.0, 1.5))
