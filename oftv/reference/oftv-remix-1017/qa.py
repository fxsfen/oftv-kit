"""Technical QA of a render: format, loudness per stem, speech consistency, black frames, dropouts.

Usage: python qa.py renders/preview_480p.mp4 [--asr]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

PROJ = Path(__file__).resolve().parents[1]
AW = PROJ / "work_audio"


def sh(*a):
    return subprocess.run([str(x) for x in a], capture_output=True, text=True, errors="replace")


def ebur(path, af="ebur128=peak=true"):
    err = sh("ffmpeg", "-hide_banner", "-i", path, "-af", af, "-f", "null", "-").stderr
    s = err[err.rfind("Summary:"):]
    g = lambda pat: float(re.search(pat, s).group(1)) if re.search(pat, s) else None
    return {"I_LUFS": g(r"I:\s+(-?[\d.]+) LUFS"), "LRA": g(r"LRA:\s+(-?[\d.]+) LU"),
            "TruePeak_dBFS": g(r"Peak:\s+(-?[\d.]+) dBFS")}


def short_term_db(path, win=3.0):
    x, sr = sf.read(str(path), dtype="float32")
    m = x.mean(1) if x.ndim > 1 else x
    hop = int(sr * win)
    n = len(m) // hop
    return 20 * np.log10(np.sqrt((m[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


def main():
    dst = PROJ / sys.argv[1]
    rep = {}
    pr = json.loads(sh("ffprobe", "-v", "error", "-show_entries",
                       "format=duration,size,bit_rate:stream=codec_name,codec_type,width,height,r_frame_rate,avg_frame_rate,"
                       "pix_fmt,color_transfer,color_primaries,sample_rate,channels",
                       "-of", "json", dst).stdout)
    rep["probe"] = pr
    rep["mix"] = ebur(dst)
    tl = json.load(open(PROJ / "artifacts/timeline.json", encoding="utf-8"))
    # dialogue / music stems as they sit in the mix (after the -6 / -16 dB offsets)
    rep["speech_stem_in_mix"] = ebur(AW / "speech_bed.wav", "volume=-6dB,ebur128=peak=true")
    rep["music_stem_in_mix"] = ebur(AW / "music_stem.wav")
    # per-segment dialogue level in the final bed
    x, sr = sf.read(str(AW / "speech_bed.wav"), dtype="float32")
    seg = []
    for it in tl["items"]:
        a = int(it["a_at"] * sr)
        b = int((it["a_at"] + it["a_out"] - it["a_in"]) * sr)
        y = x[a:b]
        y = y[np.abs(y) > 10 ** (-50 / 20)]
        seg.append(round(float(20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-9)) - 6, 1))
    rep["dialogue_rms_per_segment_dB"] = seg
    rep["dialogue_spread_dB"] = round(max(seg) - min(seg), 1)
    st = short_term_db(AW / "mix.wav")
    rep["mix_3s_rms_dB"] = {"min": round(float(st.min()), 1), "p5": round(float(np.percentile(st, 5)), 1),
                            "median": round(float(np.median(st)), 1), "max": round(float(st.max()), 1)}
    err = sh("ffmpeg", "-hide_banner", "-i", dst, "-vf", "blackdetect=d=0.1:pix_th=0.06", "-an", "-f", "null", "-").stderr
    rep["black_segments"] = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)
    err = sh("ffmpeg", "-hide_banner", "-i", dst, "-af", "silencedetect=n=-50dB:d=1.0", "-vn", "-f", "null", "-").stderr
    rep["audio_silences_over_1s"] = re.findall(r"silence_start: ([\d.]+)", err)
    err = sh("ffmpeg", "-hide_banner", "-v", "error", "-i", dst, "-f", "null", "-").stderr
    rep["decode_errors"] = err.strip()[:500]
    if "--asr" in sys.argv:
        from faster_whisper import WhisperModel
        m = WhisperModel("small", device="cpu", compute_type="int8")
        segs, _ = m.transcribe(str(AW / "speech_bed.wav"), language="en", vad_filter=False)
        lines = [f"{s.start:7.2f} {s.text.strip()}" for s in segs]
        (PROJ / "artifacts/qa_transcript.txt").write_text("\n".join(lines), encoding="utf-8")
    out = PROJ / f"artifacts/qa_{dst.stem}.json"
    out.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in rep.items() if k != "probe"}, indent=1))
    for s in pr["streams"]:
        print(s)
    print(pr["format"])


if __name__ == "__main__":
    main()
