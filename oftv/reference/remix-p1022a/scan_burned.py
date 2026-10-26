"""Find the sources' burned-in subtitles (white text with a dark outline) in the bottom strip.

scan(src, t0, dur) -> list of (time, x0, x1) in 4K pixels at 5 fps; x0 = x1 = None when no text.
Used to size the black boxes that hide the old subtitles behind ours.
"""
import subprocess
import sys

import numpy as np

Y0, H = 1985, 170          # strip in 4K coordinates
SW, SH = 960, 44           # analysis size (x4 horizontally)
FPS = 5


def strip_frames(src, t0, dur):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t0:.3f}", "-i", src, "-t", f"{dur:.3f}",
           "-vf", f"fps={FPS},crop=3840:{H}:0:{Y0},scale={SW}:{SH}:flags=area,format=gray",
           "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, SH, SW)


def text_extent(f):
    f = f.astype(np.int16)
    bright = f > 205
    dark = f < 80
    # a bright pixel with a dark pixel within 2 px = glyph next to its outline / shadow
    near = np.zeros_like(dark)
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            near |= np.roll(np.roll(dark, dy, 0), dx, 1)
    feat = bright & near
    cols = feat.sum(0)
    on = np.where(cols >= 2)[0]
    if feat.sum() < 150 or (feat.sum(1) > 3).sum() < 8 or len(on) < 6:   # text: ~900-2000 px over 15+ rows
        return None, None
    # keep the densest run of columns (gaps <= 40 px) — the subtitle line
    runs, s = [], on[0]
    for a, b in zip(on, on[1:]):
        if b - a > 40:
            runs.append((s, a))
            s = b
    runs.append((s, on[-1]))
    s0, s1 = max(runs, key=lambda r: cols[r[0]:r[1] + 1].sum())
    if s1 - s0 < 10:
        return None, None
    return int(s0 * 3840 / SW), int((s1 + 1) * 3840 / SW)


def scan(src, t0, dur):
    fr = strip_frames(src, t0, dur)
    return [(round(t0 + k / FPS, 2), *text_extent(f)) for k, f in enumerate(fr)]


if __name__ == "__main__":
    src, t0, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    for t, a, b in scan(src, t0, dur):
        print(t, a, b)
