"""Checks that this PC can run OFTV edits. usage: python oftv/tools/doctor.py   (exit code 1 if something blocks)"""
import importlib
import shutil
import subprocess
import sys

from common import DOWNLOADS, ROOT

ok, bad, warn = [], [], []


def check(cond, good, fail, blocking=True):
    (ok if cond else (bad if blocking else warn)).append(good if cond else fail)


check(sys.version_info[:2] >= (3, 10), f"python {sys.version.split()[0]}", "python >= 3.10 needed")
for mod in ("numpy", "soundfile", "faster_whisper", "PIL", "cv2", "rembg", "demucs", "scipy"):
    try:
        importlib.import_module(mod)
        ok.append(f"module {mod}")
    except Exception as e:   # noqa: BLE001
        (bad if mod in ("numpy", "soundfile", "faster_whisper") else warn).append(f"module {mod}: {e.__class__.__name__}")
for exe in ("ffmpeg", "ffprobe", "node", "git"):
    check(shutil.which(exe), f"{exe} found", f"{exe} not on PATH")
check(shutil.which("npx.cmd") or shutil.which("npx"), "npx found", "npx not on PATH")
check((ROOT / "remotion-composer/node_modules/remotion").exists(), "remotion installed",
      "remotion-composer/node_modules missing -> npm install in remotion-composer")
lofi = list((ROOT / "music_library/lofi").glob("*.mp3"))
check(len(lofi) > 20, f"lofi library: {len(lofi)} tracks", "music_library/lofi is empty (CC0 music for folders "
      "without music)", blocking=False)
check((ROOT / "oftv/assets/sfx/whoosh.wav").exists(), "sfx present", "oftv/assets/sfx missing")
check(DOWNLOADS.exists(), f"Downloads: {DOWNLOADS}", "no Downloads folder")

if shutil.which("ffmpeg"):
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=256x144:d=0.2", "-c:v", "h264_qsv",
                        "-f", "null", "-"], capture_output=True, text=True)
    check(r.returncode == 0, "Intel Quick Sync (h264_qsv) works — fast 2K encode",
          "no h264_qsv — renderer falls back to libx264 (slower, same quality)", blocking=False)

free = shutil.disk_usage(ROOT).free / 2**30
check(free > 40, f"free disk {free:.0f} GB", f"free disk only {free:.0f} GB — need 40+ GB (3-6 GB per project)",
      blocking=free < 15)
try:
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                    ("avail", ctypes.c_ulonglong)] + [(f"x{i}", ctypes.c_ulonglong) for i in range(5)]
    m = MS()
    m.l = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    ram = m.total / 2**30
    check(ram >= 15, f"RAM {ram:.0f} GB", f"RAM {ram:.0f} GB — Whisper large-v3 needs 16 GB", blocking=ram < 7)
except Exception:   # noqa: BLE001
    pass
try:
    from huggingface_hub import scan_cache_dir
    names = {r.repo_id for r in scan_cache_dir().repos}
    for mdl in ("small", "large-v3"):
        check(f"Systran/faster-whisper-{mdl}" in names, f"whisper {mdl} downloaded",
              f"whisper {mdl} not downloaded yet (downloads on first use)", blocking=False)
except Exception:   # noqa: BLE001
    pass

for s in ok:
    print("OK   " + s)
for s in warn:
    print("WARN " + s)
for s in bad:
    print("FAIL " + s)
print("\nREADY" if not bad else "\nNOT READY")
sys.exit(1 if bad else 0)
