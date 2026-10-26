"""Step 1 of every OFTV job: turn a dropped folder into project(s) under projects/.

usage: python oftv/tools/intake.py <folder name under Downloads | path> [--single | --batch] [--date MMDD]

  single  - the folder holds one model's footage (files directly inside, nested camera folders are fine);
            folder name = model tag.
  batch   - the folder holds only sub-folders, one per model, each named by the model's tag
            (e.g. "монтаж пн/daisyyyli", "монтаж пн/lia_life"). A "music" sub-folder is shared music for all.
  Auto-detected when neither flag is given: files directly inside -> single, otherwise batch.

For each model it creates projects/<tag-slug>-<MMDD>/ with
  job.json                      tag, source folder, shared music, batch name
  assets/analysis/sources.json  {"sources": {key: path}, "dur": {key: seconds}}  (same format as plan_common)
  assets/analysis/probe.json    resolution / rotation / fps / HDR / audio per file
  scripts/                      the current templates (plan_common, render_timeline, subs_util, sharpness,
                                plan_timeline_example) — never overwritten if they exist
and prints a summary with warnings (vertical clips, HDR, 60 fps, < 2:00 of footage, no voice notes, files without
extension). Re-running is safe: an existing project with the same source folder is reused.
"""
import argparse
import datetime as dt
import json
import re
import shutil
from concurrent.futures import ThreadPoolExecutor

from common import (MUSIC_DIRS, PROJECTS, TEMPLATES, find_folder, kind, media_files, nfc, probe, slugify)


SHOOT_WORDS = ("google", "drive", "видео", "video", "camera", "dcim", "apple", "esc", "toma", "voz", "фото", "foto",
               "photo", "часть", "part", "день", "day", "new folder", "новая папка", "halloween", "hallowin")


def looks_like_tag(name):
    """Model folders are named like OnlyFans handles (daisyyyli, lia_life, @mia.tesh); shoot folders are not."""
    n = name.strip()
    return bool(re.fullmatch(r"@?[A-Za-z][\w.\-]{1,40}", n)) and not any(w in n.lower() for w in SHOOT_WORDS)


def unit_list(folder, mode):
    direct = [p for p in folder.iterdir() if p.is_file() and kind(p)]
    subs = [d for d in sorted(folder.iterdir()) if d.is_dir() and nfc(d.name) not in MUSIC_DIRS
            and media_files(d)]
    music_dir = next((d for d in folder.iterdir() if d.is_dir() and nfc(d.name) in MUSIC_DIRS), None)
    if mode is None:
        tagged = [d for d in subs if looks_like_tag(d.name)]
        mode = "batch" if subs and not direct and len(tagged) * 2 > len(subs) else "single"
    if mode == "single":
        return mode, [folder], music_dir
    return mode, subs, music_dir


def existing_project(src):
    for j in PROJECTS.glob("*/job.json"):
        try:
            if json.loads(j.read_text(encoding="utf-8")).get("src") == str(src):
                return j.parent
        except (ValueError, OSError):
            pass
    return None


def make_project(src, date, batch, music_dir):
    proj = existing_project(src)
    if proj is None:
        base = f"{slugify(src.name)}-{date}"
        name, n = base, 1
        while (PROJECTS / name).exists():
            n += 1
            name = f"{base}{chr(ord('a') + n - 2)}"
        proj = PROJECTS / name
    an = proj / "assets/analysis"
    an.mkdir(parents=True, exist_ok=True)
    (proj / "scripts").mkdir(exist_ok=True)
    (proj / "renders").mkdir(exist_ok=True)
    for t in TEMPLATES.glob("*.py"):
        dst = proj / "scripts" / t.name
        if not dst.exists():
            shutil.copy2(t, dst)

    files = media_files(src)
    keys, sources, durs, probes = {}, {}, {}, {}
    with ThreadPoolExecutor(6) as ex:
        infos = list(ex.map(probe, files))
    for p, info in zip(files, infos):
        k = p.stem
        if k in keys:   # same name in two camera folders
            k = f"{p.parent.name}_{p.stem}"
        keys[k] = p
        sources[k] = str(p).replace("\\", "/")
        durs[k] = info["dur"]
        probes[k] = {"kind": kind(p), "rel": str(p.relative_to(src)), **info}
    music = sorted(str(p).replace("\\", "/") for p in music_dir.rglob("*") if p.is_file() and kind(p) == "audio") \
        if music_dir else []
    tag = src.name.strip()
    tag = tag if tag.startswith("@") else "@" + tag
    job = {"tag": tag, "tag_confirmed": False, "src": str(src), "batch": batch, "shared_music": music,
           "created": dt.date.today().isoformat(), "status": "intake"}
    jp = proj / "job.json"
    if jp.exists():
        old = json.loads(jp.read_text(encoding="utf-8"))
        job = {**job, **{k: old[k] for k in ("tag", "tag_confirmed", "status") if k in old}}
    jp.write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
    (an / "sources.json").write_text(json.dumps({"sources": sources, "dur": durs}, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
    (an / "probe.json").write_text(json.dumps(probes, ensure_ascii=False, indent=1), encoding="utf-8")
    return proj, job, probes


def report(proj, job, probes):
    vids = {k: v for k, v in probes.items() if v["kind"] in ("video", "noext")}
    auds = {k: v for k, v in probes.items() if v["kind"] == "audio"}
    photos = [k for k, v in probes.items() if v["kind"] == "photo"]
    total = sum(v["dur"] for v in vids.values())
    warn = []
    vert = [k for k, v in vids.items() if v.get("h", 0) > v.get("w", 0)]
    # black portrait clips with only sound are usually voice notes recorded on camera — flagged, decided on sheets
    if vert:
        warn.append(f"{len(vert)} vertical clip(s) (voice notes filmed on camera, or need a horizontal export): "
                    + ", ".join(vert[:8]) + (" …" if len(vert) > 8 else ""))
    hdr = [k for k, v in vids.items() if v.get("trc") in ("arib-std-b67", "smpte2084")]
    if hdr:
        warn.append(f"{len(hdr)} HDR (HLG/PQ) clip(s) — force bt709 per segment (playbook gotcha)")
    if any(v.get("fps", 0) > 31 for v in vids.values()):
        warn.append("60 fps clips present -> fps=30")
    if any(v["kind"] == "noext" for v in probes.values()):
        warn.append("files without extension — ask the user before renaming them to .MOV")
    if total < 120:
        warn.append(f"only {total:.0f} s of video — < 2:00 OFTV minimum, needs slow-mo / photos / ask")
    if not auds:
        warn.append("no separate audio files (voice notes / music) — check if she talks on camera; music from "
                    "music_library/lofi if none")
    tops = sorted({v["rel"].replace("\\", "/").split("/")[0] for v in probes.values() if "/" in v["rel"].replace("\\", "/")})
    if len(tops) > 1:
        warn.append(f"sub-folders {', '.join(tops)} — may be SEPARATE videos (one shoot each): check the sheets, "
                    "split into <slug> / <slug>b if so")
    small = [k for k, v in vids.items() if 0 < min(v.get("w", 0), v.get("h", 0)) < 1080]
    if small:
        warn.append(f"{len(small)} clip(s) below 1080p")
    res = sorted({f'{v.get("w")}x{v.get("h")}' for v in vids.values()})
    print(f"\n== {job['tag']}  ->  projects/{proj.name}")
    print(f"   source: {job['src']}")
    print(f"   {len(vids)} video ({total / 60:.1f} min, {', '.join(res[:4])}), {len(auds)} audio "
          f"({', '.join(list(auds)[:6])}{' …' if len(auds) > 6 else ''}), {len(photos)} photo")
    if job["shared_music"]:
        print(f"   shared music: {len(job['shared_music'])} file(s)")
    for w in warn:
        print("   ! " + w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--single", action="store_const", dest="mode", const="single")
    g.add_argument("--batch", action="store_const", dest="mode", const="batch")
    ap.add_argument("--date", default=dt.date.today().strftime("%m%d"))
    a = ap.parse_args()
    folder = find_folder(a.folder)
    mode, units, music_dir = unit_list(folder, a.mode)
    if not units:
        raise SystemExit(f"No video/audio files in {folder}")
    print(f"{folder}  ->  {mode}, {len(units)} video folder(s)")
    batch = folder.name if mode == "batch" else None
    made = []
    for u in units:
        proj, job, probes = make_project(u, a.date, batch, music_dir)
        report(proj, job, probes)
        made.append(proj.name)
    if batch:
        bd = PROJECTS / "_batches"
        bd.mkdir(exist_ok=True)
        (bd / f"{slugify(batch)}-{a.date}.json").write_text(
            json.dumps({"folder": str(folder), "projects": made}, ensure_ascii=False, indent=1), encoding="utf-8")
    free = shutil.disk_usage(PROJECTS).free / 2**30
    print(f"\nprojects: {' '.join(made)}")
    print(f"free disk: {free:.0f} GB" + ("  ! low — each project needs 3-6 GB of work files" if free < 30 else ""))


if __name__ == "__main__":
    main()
