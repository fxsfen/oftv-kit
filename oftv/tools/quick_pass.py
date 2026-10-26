"""Quick analysis of one project (after intake.py) or of every project of a batch.

usage: python oftv/tools/quick_pass.py <project | batch:<name>> [audio] [sheets] [whisper] [vad] [blur]
       (no step names = audio sheets vad whisper)

audio   -> assets/analysis/wav16/<key>.wav (mono 16 kHz) for every file with sound
sheets  -> assets/analysis/sheets/<key>.jpg: 8 frames tiled 8x1 with time labels (rotation applied)
vad     -> assets/analysis/camera_speech.json: Silero speech ranges per wav (b-roll = silent ranges only)
whisper -> assets/analysis/quick_transcripts.json: small model, only on files where VAD finds speech
blur    -> assets/analysis/blur_per_sec.json: per-second blurdetect (plan_common picks the sharpest windows)
Everything resumes: finished files are skipped. Batch projects run one after another (Whisper needs the RAM).
"""
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from common import PROJECTS, load_sources, proj_dir


def run(proj, steps):
    an = proj / "assets/analysis"
    S = load_sources(proj)
    probes = json.loads((an / "probe.json").read_text(encoding="utf-8"))
    src = S["sources"]
    sheets, wav = an / "sheets", an / "wav16"
    sheets.mkdir(exist_ok=True)
    wav.mkdir(exist_ok=True)
    print(f"== {proj.name}: {len(src)} files, steps {' '.join(steps)}", flush=True)

    if "audio" in steps:
        def ext(k):
            dst = wav / f"{k}.wav"
            if probes[k].get("audio") and not dst.exists():
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src[k], "-map", "0:a:0", "-vn", "-ac", "1",
                                "-ar", "16000", str(dst)], check=False)
        with ThreadPoolExecutor(4) as ex:
            list(ex.map(ext, src))
        print("audio done", flush=True)

    if "sheets" in steps:
        def sheet(k):
            out = sheets / f"{k}.jpg"
            if out.exists() or probes[k]["kind"] not in ("video", "noext", "photo"):
                return
            d = S["dur"][k]
            tmp = sheets / f"_{k}"
            tmp.mkdir(exist_ok=True)
            n = 1 if probes[k]["kind"] == "photo" else 8
            for i in range(n):
                t = d * (i + 0.5) / n
                label = re.sub(r"[^A-Za-z0-9_ .-]", "", k)[-10:]
                subprocess.run(["ffmpeg", "-v", "error", "-y"] + (["-ss", f"{t:.2f}"] if n > 1 else []) +
                               ["-i", src[k], "-frames:v", "1", "-vf",
                                "scale=-2:224,pad=400:224:(ow-iw)/2:0,"
                                rf"drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='{label} {t:.0f}s':"
                                "x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6",
                                str(tmp / f"{i}.jpg")], check=False)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "%d.jpg"), "-vf", f"tile={n}x1",
                            "-frames:v", "1", str(out)], check=False)
            for f in tmp.glob("*.jpg"):
                f.unlink()
            tmp.rmdir()
        with ThreadPoolExecutor(3) as ex:
            list(ex.map(sheet, src))
        print("sheets done", flush=True)

    if "vad" in steps or "whisper" in steps:
        import soundfile as sf
        from faster_whisper.vad import VadOptions, get_speech_timestamps
        vp = an / "camera_speech.json"
        vad = json.loads(vp.read_text(encoding="utf-8")) if vp.exists() else {}
        for w in sorted(wav.glob("*.wav")):
            if w.stem in vad:
                continue
            x, sr = sf.read(str(w), dtype="float32")
            ts = get_speech_timestamps(x, VadOptions(threshold=0.4, min_speech_duration_ms=150,
                                                     min_silence_duration_ms=300))
            vad[w.stem] = [[round(t["start"] / sr, 2), round(t["end"] / sr, 2)] for t in ts]
        vp.write_text(json.dumps(vad, indent=0, ensure_ascii=False), encoding="utf-8")
        print("vad done", flush=True)

    if "whisper" in steps:
        from faster_whisper import WhisperModel
        m = WhisperModel("small", device="cpu", compute_type="int8")
        qf = an / "quick_transcripts.json"
        res = json.loads(qf.read_text(encoding="utf-8")) if qf.exists() else {}
        for w in sorted(wav.glob("*.wav")):
            k = w.stem
            if k in res:
                continue
            sp = sum(b - a for a, b in vad.get(k, []))
            if sp < 0.8:
                res[k] = {"lang": None, "dur": S["dur"].get(k), "speech_s": round(sp, 1), "segs": []}
            else:
                segs, inf = m.transcribe(str(w), vad_filter=False, condition_on_previous_text=False,
                                         temperature=0.0)
                res[k] = {"lang": inf.language, "dur": S["dur"].get(k), "speech_s": round(sp, 1),
                          "segs": [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()} for s in segs]}
            print(k, res[k]["lang"], res[k]["speech_s"], " | ".join(x["t"] for x in res[k]["segs"])[:300],
                  flush=True)
            qf.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print("whisper done", flush=True)

    if "blur" in steps:
        bp = an / "blur_per_sec.json"
        res = json.loads(bp.read_text()) if bp.exists() else {}
        keys = [k for k in src if probes[k]["kind"] in ("video", "noext") and k not in res]

        def one(k):
            r = subprocess.run(["ffmpeg", "-hide_banner", "-skip_frame", "nokey" if S["dur"][k] > 240 else "default",
                                "-i", src[k], "-vf",
                                "fps=5,scale=960:-2,blurdetect=block_width=32:block_height=32,metadata=print:file=-",
                                "-an", "-f", "null", "-"], capture_output=True, text=True, errors="replace")
            vals = [float(x) for x in re.findall(r"lavfi.blur=([\d.]+)", r.stdout)]
            return k, [round(sum(vals[i:i + 5]) / len(vals[i:i + 5]), 2) for i in range(0, len(vals), 5)]
        with ThreadPoolExecutor(4) as ex:
            for k, v in ex.map(one, keys):
                res[k] = v
                bp.write_text(json.dumps(res, indent=0), encoding="utf-8")
        print("blur done", flush=True)


def main():
    target, steps = sys.argv[1], [s for s in sys.argv[2:]] or ["audio", "sheets", "vad", "whisper"]
    if target.startswith("batch:"):
        b = PROJECTS / "_batches" / f"{target[6:]}.json"
        names = json.loads(b.read_text(encoding="utf-8"))["projects"]
    else:
        names = [target]
    for n in names:
        run(proj_dir(n), steps)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
