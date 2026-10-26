"""Measure a finished video's mix against OFTV levels (analysis only — nothing is written to the video).

Dialogue peaks should sit -12..-6 dB, music -16..-10 dB (OFTV feedback 2026-10-19), whole mix -16..-6 dB,
music never louder than dialogue, no part too loud / too soft.
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/audio"
SR = 48000


def block_peaks(x, win=0.1):
    m = np.abs(x).max(1) if x.ndim > 1 else np.abs(x)
    hop = int(SR * win)
    n = len(m) // hop
    return 20 * np.log10(m[:n * hop].reshape(n, hop).max(1) + 1e-9)


def pct(v):
    return {k: round(float(np.percentile(v, q)), 1) for k, q in (("p10", 10), ("p50", 50), ("p90", 90), ("p99", 99))} \
        | {"max": round(float(v.max()), 1)}


def lufs(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


voc, _ = sf.read(A / "A_vocals.wav", dtype="float32")
mus, _ = sf.read(A / "A_music.wav", dtype="float32")
mix, _ = sf.read(A / "A_48k.wav", dtype="float32")
bv, bm, bx = block_peaks(voc), block_peaks(mus), block_peaks(mix)
sp = bv > np.percentile(bv, 95) - 18          # blocks with speech
mu = bm > np.percentile(bm, 95) - 18          # blocks with music
rep = {
    "dialogue_peaks": pct(bv[sp]),
    "music_peaks": pct(bm[mu]),
    "music_peaks_under_speech": pct(bm[sp & mu]) if (sp & mu).any() else None,
    "mix_peaks_while_sound": pct(bx[sp | mu]),
    "lufs": {"dialogue": lufs(A / "A_vocals.wav"), "music": lufs(A / "A_music.wav"), "mix": lufs(A / "A_48k.wav")},
    "music_share_s": round(float(mu.sum()) / 10, 1),
    "speech_share_s": round(float(sp.sum()) / 10, 1),
}
# evenness: dialogue median peak per 30 s window
w = 300
rows = []
for k in range(0, len(bv) - w // 2, w):
    seg_sp = sp[k:k + w]
    if seg_sp.sum() > 30:
        rows.append((round(k / 10 / 60, 2), round(float(np.median(bv[k:k + w][seg_sp])), 1),
                     round(float(np.median(bm[k:k + w][mu[k:k + w]])), 1) if mu[k:k + w].sum() > 30 else None))
rep["per_30s_dialogue_vs_music_median_peak"] = rows
(PROJ / "artifacts/measure.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
print(json.dumps(rep, indent=1))
