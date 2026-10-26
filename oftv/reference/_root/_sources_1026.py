"""sources.json (+ optional blur_per_sec.json) for a 2026-10-26 'монтаж пнд' project.
usage: python _sources_1026.py <project> <subfolder under монтаж пнд> [blur]
Voice notes (.m4a) are keyed by their stem as in wav16 (file names may be NFD)."""
import json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
PROJ = Path(__file__).resolve().parent / sys.argv[1]
AN = PROJ / "assets/analysis"
BASE = [d for d in Path(r"C:\Users\fosfe\Downloads").iterdir() if d.name == "монтаж пнд"][0]
SRC = BASE / sys.argv[2] if sys.argv[2] != "-" else BASE
sub = [d for d in SRC.parent.iterdir() if d.name == SRC.name][0] if SRC.exists() else \
    [d for d in BASE.rglob("*") if d.is_dir() and d.name.startswith(sys.argv[2].split("/")[-1])][0]
S = {"sources": {}, "dur": {}}
for p in sorted(sub.iterdir()):
    if p.suffix.lower() not in (".mov", ".m4a", ".mp4"):
        continue
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    S["sources"][p.stem] = str(p).replace("\\", "/")
    S["dur"][p.stem] = round(float(r.stdout), 3)
AN.mkdir(parents=True, exist_ok=True)
(AN / "sources.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(S["sources"]), "sources")
if "blur" in sys.argv:
    sp = json.load(open(AN / "camera_speech.json", encoding="utf-8")) if (AN / "camera_speech.json").exists() else {}
    bp = AN / "blur_per_sec.json"
    res = json.load(open(bp)) if bp.exists() else {}
    keys = [k for k, v in S["sources"].items() if v.lower().endswith((".mov", ".mp4")) and k not in res]

    def one(k):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-skip_frame", "nokey" if S["dur"][k] > 240 else "default",
                            "-i", S["sources"][k], "-vf",
                            "fps=5,scale=960:-2,blurdetect=block_width=32:block_height=32,metadata=print:file=-",
                            "-an", "-f", "null", "-"], capture_output=True, text=True, errors="replace")
        vals = [float(x) for x in re.findall(r"lavfi.blur=([\d.]+)", r.stdout)]
        return k, [round(sum(vals[i:i + 5]) / len(vals[i:i + 5]), 2) for i in range(0, len(vals), 5)]
    with ThreadPoolExecutor(4) as ex:
        for k, v in ex.map(one, keys):
            res[k] = v
            bp.write_text(json.dumps(res, indent=0), encoding="utf-8")
            print(k, len(v), "s", flush=True)
