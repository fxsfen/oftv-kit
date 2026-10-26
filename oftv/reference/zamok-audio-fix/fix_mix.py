"""Re-balance dialogue vs music of a finished video to OFTV's suggested mix levels.

OFTV feedback: music too quiet. Suggested meter levels: dialogue -12..-6 dB, music -16..-10 dB.
Interpreted as 100 ms block peaks of each element in the final mix:
  dialogue: median ~ -9 dBFS during speech, hard ceiling -6 dBFS
  music   : median ~ -13 dBFS while it plays, hard ceiling -10 dBFS
Stems come from Demucs (vocals / everything else). Video stream is copied untouched.

Usage: python fix_mix.py [--measure-only]
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

PROJ = Path(__file__).resolve().parents[1]
SRC = "C:/Users/fosfe/Downloads/замок2к.mp4"
A = PROJ / "assets/audio"
SR = 48000
DIA_MED, DIA_CEIL = -10.0, -6.0
MUS_MED, MUS_CEIL = -14.0, -10.0


def ff(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, a)], check=True)


def block_peaks(x, win=0.1):
    m = np.abs(x).max(1) if x.ndim > 1 else np.abs(x)
    hop = int(SR * win)
    n = len(m) // hop
    return 20 * np.log10(m[:n * hop].reshape(n, hop).max(1) + 1e-9)


def stats(x, active):
    bp = block_peaks(x)
    act = bp[active[:len(bp)]]
    return {k: round(float(np.percentile(act, q)), 1) for k, q in
            (("p10", 10), ("p50", 50), ("p90", 90), ("p99", 99))} | {"max": round(float(act.max()), 1)}


def activity(x, thr_db):
    """Blocks where this element is actually playing (relative to its own loudest parts)."""
    bp = block_peaks(x)
    ref = np.percentile(bp, 95)
    return bp > ref + thr_db


def main():
    voc, _ = sf.read(A / "A_vocals.wav", dtype="float32")
    mus, _ = sf.read(A / "A_music.wav", dtype="float32")
    sp_act = activity(voc, -18)
    mu_act = activity(mus, -18)
    rep = {"before": {"dialogue": stats(voc, sp_act), "music": stats(mus, mu_act)}}
    if "--measure-only" in sys.argv:
        print(json.dumps(rep, indent=1))
        return
    # 1) dialogue: gentle clean-up + compression to even it out, then gain to the target median
    v1 = A / "voc_proc.wav"
    ff("-i", A / "A_vocals.wav", "-af",
       "highpass=f=70,afftdn=nr=6:nf=-60:tn=1,"
       "acompressor=threshold=-24dB:ratio=3:attack=8:release=200:makeup=1",
       "-c:a", "pcm_f32le", v1)
    v, _ = sf.read(v1, dtype="float32")
    g_v = DIA_MED - stats(v, sp_act)["p50"]
    # 2) music: smooth level (slow compressor) then gain to the target median
    m1 = A / "mus_proc.wav"
    ff("-i", A / "A_music.wav", "-af", "acompressor=threshold=-28dB:ratio=2:attack=60:release=600:makeup=1",
       "-c:a", "pcm_f32le", m1)
    m, _ = sf.read(m1, dtype="float32")
    g_m = MUS_MED - stats(m, mu_act)["p50"]
    # 3) apply gains + per-stem ceilings, sum, final safety limiter at -1 dBFS
    vf = A / "voc_final.wav"
    mf = A / "mus_final.wav"
    ff("-i", v1, "-af", f"volume={g_v:.2f}dB,alimiter=limit={10 ** (DIA_CEIL / 20):.4f}:level=false:attack=2:release=50",
       "-c:a", "pcm_f32le", vf)
    ff("-i", m1, "-af", f"volume={g_m:.2f}dB,alimiter=limit={10 ** (MUS_CEIL / 20):.4f}:level=false:attack=5:release=120",
       "-c:a", "pcm_f32le", mf)
    mix = A / "mix_fixed.wav"
    ff("-i", vf, "-i", mf, "-filter_complex",
       "[0:a][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false[o]", "-map", "[o]",
       "-c:a", "pcm_s24le", mix)
    v2, _ = sf.read(vf, dtype="float32")
    m2, _ = sf.read(mf, dtype="float32")
    rep["gain_db"] = {"dialogue": round(g_v, 2), "music": round(g_m, 2)}
    rep["after"] = {"dialogue": stats(v2, sp_act), "music": stats(m2, mu_act)}
    # 4) mux: copy the video stream, new AAC 320k audio
    dst = PROJ / "renders/замок2к_audiofix.mp4"
    ff("-i", SRC, "-i", mix, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
       "-ar", SR, "-shortest", "-movflags", "+faststart", dst)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(dst), "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    s = err[err.rfind("Summary:"):]
    rep["final_mix_ebur128"] = " ".join(s.split())[:200]
    (PROJ / "artifacts/mix_report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rep, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
