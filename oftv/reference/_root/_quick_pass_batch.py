"""Quick analysis of one source folder into projects/<proj>/assets/analysis.
usage: python _quick_pass_batch.py <src folder name under 'монтаж пн'> <project> [audio] [sheets] [whisper]
audio -> wav16 per clip; sheets -> 8 seeked frames tiled 8x1 (display rotation applied by ffmpeg);
whisper -> small model on clips whose Silero VAD finds speech (silent b-roll is skipped)."""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "монтаж пн"][0]
SRC = Path(sys.argv[1]) if Path(sys.argv[1]).is_absolute() else BASE / sys.argv[1]
OUT = Path(__file__).resolve().parent / sys.argv[2] / "assets" / "analysis"
SHEETS, WAV = OUT / "sheets", OUT / "wav16"
for d in (SHEETS, WAV):
    d.mkdir(parents=True, exist_ok=True)
EXT = {".mov", ".mp4", ".m4a", ".ogg", ".mp3"}
clips = sorted(c for c in SRC.iterdir() if c.suffix.lower() in EXT and "halloween" not in c.name.lower())


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json",
                        str(p)], capture_output=True, text=True, encoding="utf-8")
    j = json.loads(r.stdout)
    t = {s["codec_type"] for s in j["streams"]}
    return float(j["format"].get("duration", 0)), "audio" in t, "video" in t and p.suffix.lower() != ".mp3"


info = {c.stem: probe(c) for c in clips}
key = {c.stem: c for c in clips}

if "audio" in sys.argv:
    def ext(c):
        dst = WAV / f"{c.stem}.wav"
        if info[c.stem][1] and not dst.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(c), "-map", "0:a:0", "-vn", "-ac", "1",
                            "-ar", "16000", str(dst)], check=True)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(ext, clips))
    print("audio done", flush=True)

if "sheets" in sys.argv:
    def sheet(c):
        out = SHEETS / f"{c.stem}.jpg"
        if out.exists() or not info[c.stem][2]:
            return
        d = info[c.stem][0]
        tmp = SHEETS / f"_{c.stem}"
        tmp.mkdir(exist_ok=True)
        for k in range(8):
            t = min(d * (k + 0.5) / 8, max(0.0, d - 0.25))  # very short clips: never seek past the last frame
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(c), "-frames:v", "1",
                            "-vf", "scale=-2:224,pad=400:224:(ow-iw)/2:0,"
                                   f"drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='{c.stem[-4:]} {t:.0f}s':"
                                   "x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6",
                            str(tmp / f"{k}.jpg")], check=False)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "%d.jpg"), "-vf", "tile=8x1", "-frames:v", "1",
                        str(out)], check=True)
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(sheet, clips))
    print("sheets done", flush=True)

if "whisper" in sys.argv:
    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio
    from faster_whisper.vad import get_speech_timestamps, VadOptions
    m = WhisperModel("small", device="cpu", compute_type="int8")
    qf = OUT / "quick_transcripts.json"
    res = json.loads(qf.read_text(encoding="utf-8")) if qf.exists() else {}
    for c in clips:
        w = WAV / f"{c.stem}.wav"
        if not w.exists() or c.stem in res:
            continue
        ts = get_speech_timestamps(decode_audio(str(w)), VadOptions(threshold=0.5, min_silence_duration_ms=300))
        sp = sum(t["end"] - t["start"] for t in ts) / 16000
        if sp < 0.8:
            res[c.stem] = {"lang": None, "dur": round(info[c.stem][0], 1), "speech_s": round(sp, 1), "segs": []}
        else:
            segs, inf = m.transcribe(str(w), vad_filter=False, condition_on_previous_text=False, temperature=0.0)
            res[c.stem] = {"lang": inf.language, "dur": round(info[c.stem][0], 1), "speech_s": round(sp, 1),
                           "segs": [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()} for s in segs]}
        print(c.stem, res[c.stem]["lang"], res[c.stem]["speech_s"],
              " | ".join(x["t"] for x in res[c.stem]["segs"]), flush=True)
        qf.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("whisper done", flush=True)
