"""Copy a finished project's deliverables to Desktop\\OFTV готово\\<tag> <date>\\ and open the folder.

usage: python oftv/tools/deliver.py <project> [--no-open]
Copies renders/final_2k.mp4 (as "<tag> <date>.mp4"), cover*.jpg, title_description.txt, chapters.txt.
"""
import ctypes
import datetime as dt
import json
import os
import shutil
import sys
from pathlib import Path

from common import proj_dir


def desktop():
    buf = ctypes.create_unicode_buffer(260)
    if ctypes.windll.shell32.SHGetFolderPathW(None, 0x10, None, 0, buf) == 0:   # CSIDL_DESKTOPDIRECTORY (OneDrive-safe)
        return Path(buf.value)
    return Path.home() / "Desktop"


def main():
    proj = proj_dir(sys.argv[1])
    job = json.loads((proj / "job.json").read_text(encoding="utf-8")) if (proj / "job.json").exists() else {}
    tag = job.get("tag", "@" + proj.name)
    r = proj / "renders"
    final = r / "final_2k.mp4"
    if not final.exists():
        raise SystemExit(f"{final} not found — render --res 1440 first")
    name = f"{tag.lstrip('@')} {dt.date.today():%d.%m}"
    out = desktop() / "OFTV готово" / name
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final, out / f"{name}.mp4")
    n = 1
    for f in sorted(r.glob("*.jpg")) + [r / "title_description.txt", r / "chapters.txt"]:
        if f.exists():
            shutil.copy2(f, out / f.name)
            n += 1
    job["status"] = "delivered"
    job["delivered_to"] = str(out)
    (proj / "job.json").write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{n} files -> {out}")
    if "--no-open" not in sys.argv:
        os.startfile(out)


if __name__ == "__main__":
    main()
