"""Shared helpers for the OFTV kit tools: repo paths, folder lookup (NFC/NFD-safe), media probing, project jobs."""
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = Path(os.environ.get("OFTV_PROJECTS") or ROOT / "projects")   # env override for dry runs
TEMPLATES = ROOT / "oftv" / "templates"
DOWNLOADS = Path(os.path.expanduser("~")) / "Downloads"

VIDEO_EXT = {".mov", ".mp4", ".m4v", ".mkv", ".avi", ".mts", ".webm"}
AUDIO_EXT = {".m4a", ".mp3", ".wav", ".aac", ".ogg", ".opus", ".flac", ".caf", ".amr"}
PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
MUSIC_DIRS = {"music", "музыка", "music for video", "sound", "songs"}

# cp1251 consoles crash on Thai / emoji folder names
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def nfc(s):
    return unicodedata.normalize("NFC", s).casefold().strip()


def find_folder(arg):
    """Absolute/relative path, or a folder name under Downloads (also one level deeper). Names may be NFD on disk."""
    p = Path(arg).expanduser()
    if p.is_absolute() and p.exists():
        return p
    if p.exists() and p.is_dir():
        return p.resolve()
    want = nfc(arg.strip("/\\"))
    parts = [nfc(x) for x in re.split(r"[\\/]", arg.strip("/\\"))]
    if len(parts) > 1:   # "монтаж пн/daisy"
        cur = DOWNLOADS
        for part in parts:
            nxt = [d for d in cur.iterdir() if d.is_dir() and nfc(d.name) == part]
            if not nxt:
                break
            cur = nxt[0]
        else:
            return cur
    for base in [DOWNLOADS] + [d for d in DOWNLOADS.iterdir() if d.is_dir()]:
        try:
            for d in base.iterdir():
                if d.is_dir() and nfc(d.name) == want:
                    return d
        except PermissionError:
            continue
    raise SystemExit(f"Folder not found: {arg!r} (looked in {DOWNLOADS} and one level below)")


def kind(p):
    e = p.suffix.lower()
    if e in VIDEO_EXT:
        return "video"
    if e in AUDIO_EXT:
        return "audio"
    if e in PHOTO_EXT:
        return "photo"
    if e == "" and p.stat().st_size > 1_000_000:
        return "noext"   # e.g. "ESC 3 TOMA 3.1" — a .MOV that lost its extension
    return None


def media_files(folder, skip_music=True):
    out = []
    for p in sorted(folder.rglob("*")):
        if not p.is_file() or p.name.startswith((".", "~")):
            continue
        if skip_music and any(nfc(x) in MUSIC_DIRS for x in p.relative_to(folder).parts[:-1]):
            continue
        if kind(p):
            out.append(p)
    return out


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(p)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        j = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        j = {}
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"
              and s.get("disposition", {}).get("attached_pic") != 1), None)
    a = next((s for s in j.get("streams", []) if s.get("codec_type") == "audio"), None)
    info = {"dur": round(float(j.get("format", {}).get("duration", 0) or 0), 3), "audio": bool(a),
            "audio_ch": a.get("channels") if a else 0}
    if v:
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = int(float(sd["rotation"]))
        rot = rot or int(v.get("tags", {}).get("rotate", 0) or 0)
        w, h = v.get("width", 0), v.get("height", 0)
        if abs(rot) in (90, 270):
            w, h = h, w
        num, _, den = (v.get("avg_frame_rate") or "0/1").partition("/")
        fps = round(float(num) / float(den or 1), 2) if float(den or 1) else 0
        info.update({"w": w, "h": h, "rot": rot, "fps": fps, "pix_fmt": v.get("pix_fmt"),
                     "trc": v.get("color_transfer"), "range": v.get("color_range"),
                     "created": v.get("tags", {}).get("creation_time") or j.get("format", {}).get("tags", {}).get("creation_time")})
    return info


def slugify(tag):
    s = unicodedata.normalize("NFKD", tag.lstrip("@")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "model"


def proj_dir(name):
    p = PROJECTS / name
    if not p.exists():
        raise SystemExit(f"No project {name!r} in {PROJECTS}")
    return p


def load_sources(proj):
    return json.loads((proj / "assets/analysis/sources.json").read_text(encoding="utf-8"))
