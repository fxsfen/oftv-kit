"""Put every pop-up where it covers no person: for each graphic, 3 frames across its on-screen time are taken from
the exact source frames (same crop/zoom as the edit), isnet (rembg) masks the person / main subject, and the
candidate position with the least overlap (mask dilated, subtitle strip and other visible pop-ups also blocked)
wins. Writes the chosen x/y/side props back into artifacts/timeline.json and a QA sheet of all placements."""
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

PROJ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJ / "scripts"))
import render_timeline as R  # noqa: E402

from rembg import new_session, remove  # noqa: E402

TLF = PROJ / "artifacts/timeline.json"
QA = PROJ / "assets/analysis/placement"
QA.mkdir(parents=True, exist_ok=True)
SW, SH = 960, 540          # analysis size
K = 3840 / SW              # 4K plate coords -> analysis coords
SUB_TOP = 1880             # subtitle strip (4K coords) is off-limits
session = new_session("isnet-general-use")


def frame(tl, out_t):
    """Frame of the edit at output time `out_t` (from the source, with the item's crop/zoom)."""
    for it in tl["video"]:
        n = R.nframes(it) / R.FPS
        if it["t0"] <= out_t < it["t0"] + n and not it.get("split"):
            src_t = min(it["in"] + max(0.0, out_t - it["t0"] - it.get("pad_head", 0.0)), it["out"] - 0.05)
            vf = []
            if it.get("crop_y") is not None:
                vf.append(f"crop=iw:trunc(iw*9/16/2)*2:0:(ih-oh)*{it['crop_y']}")
            if it.get("zoom"):
                z = it["zoom"]
                vf.append(f"crop=trunc(iw/{z}/2)*2:trunc(ih/{z}/2)*2:(iw-ow)/2:(ih-oh)*0.35")
            vf.append(f"scale={SW}:{SH}")
            png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{src_t:.3f}", "-i", tl["sources"][it["src"]],
                                  "-frames:v", "1", "-vf", ",".join(vf), "-f", "image2pipe", "-vcodec", "png", "-"],
                                 capture_output=True).stdout
            return Image.open(io.BytesIO(png)).convert("RGB")
    return None


def mask(img):
    m = np.array(remove(img, session=session, only_mask=True)).astype(np.float32) / 255
    m = (m > 0.35).astype(np.float32)
    # dilate ~24 px at 4K scale so pop-ups keep a little air around the person
    from scipy.ndimage import binary_dilation
    d = binary_dilation(m > 0, iterations=6).astype(np.float32)
    # head zone counts 5x: in every column the first ~22% of frame height below the top of the silhouette
    w = d.copy()
    head = int(0.22 * SH)
    for x in range(SW):
        ys = np.nonzero(d[:, x])[0]
        if len(ys) and ys[0] < 0.6 * SH:
            w[ys[0]:ys[0] + head, x] = 5.0
    return w


def text_w(s, px):  # rough text width in 4K px for the Halloween fonts
    return int(len(s) * px * 0.55)


def rects(g):
    """Candidate placements: list of (props_update, (x0, y0, x1, y1)) in 4K coords, preferred first."""
    c, p = g["comp"], g["props"]
    out = []
    if c == "HwTitle":
        h = 900
        for side in ("left", "right"):
            x0 = 220 if side == "left" else 3840 - 220 - 1350
            out.append(({"side": side, "top": 420}, (x0, 420, x0 + 1350, 420 + h)))
    elif c == "HwList":
        h = 240 + len(p["items"]) * 118
        for side in ("left", "right"):
            x0 = 180 if side == "left" else 3840 - 180 - 1220
            top = max(120, min(260, SUB_TOP - 40 - h))
            out.append(({"side": side, "top": top}, (x0, top, x0 + 1220, top + h)))
    elif c == "HwScene":
        w, h = 290 + 44 + text_w(p["title"], 196) + 60, 330
        for side in ("left", "right"):
            x0 = 190 if side == "left" else 3840 - 190 - w
            out.append(({"side": side, "bottom": 330}, (x0, 2160 - 330 - h, x0 + w, 2160 - 330)))
    elif c == "HwStamp":
        w, h = text_w(p["text"], 200) + 300, 340 + (70 if p.get("sub") else 0)
        for cx, cy in ((3000, 620), (840, 620), (3000, 1250), (840, 1250), (1920, 420)):
            out.append(({"x": cx, "y": cy}, (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)))
    elif c in ("HwName", "HwStep", "HwSticker"):
        if c == "HwName":
            w, h = 300 + max(text_w(p["name"], 210), text_w(p["role"], 58) + 60) + 120, 330
        elif c == "HwStep":
            w, h = max(1100, 330 + text_w(p["label"], 116) + 120), 340
        else:
            w, h = 230 + max(text_w(p["text"], 104), text_w(p.get("sub", ""), 52)) + 120, 230 + (50 if p.get("sub") else 0)
        ys = (150, 700, SUB_TOP - 60 - h)
        for y in ys:
            for anchor in ("left", "right"):
                x = 160 if anchor == "left" else 3840 - 160
                x0 = x if anchor == "left" else x - w
                out.append(({"x": x, "y": y, "anchor": anchor}, (x0, y, x0 + w, y + h)))
    return out


def overlap(m, r, others):
    x0, y0, x1, y1 = [int(v / K) for v in r]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(SW, x1), min(SH, y1)
    if x1 <= x0 or y1 <= y0:
        return 9.0
    sc = float(m[y0:y1, x0:x1].mean())
    if r[3] > SUB_TOP:
        sc += 0.5
    for o in others:
        ix = max(0, min(r[2], o[2]) - max(r[0], o[0])) * max(0, min(r[3], o[3]) - max(r[1], o[1]))
        if ix:
            sc += 1.0
    return sc


def main():
    tl = json.load(open(TLF, encoding="utf-8"))
    R.layout(tl)
    placed = []  # (start, end, rect)
    for gi, g in enumerate(tl["graphics"]):
        if g["comp"] == "HwSplit":
            continue
        if g["comp"] == "TagPlate":  # fixed top-right plate: just reserve its area
            placed.append((g["at"], g["at"] + g["dur"], (2860, 70, 3770, 360)))
            continue
        a, b = g["at"], g["at"] + g["dur"]
        ms = [mask(f) for f in (frame(tl, t) for t in (a + 0.3, (a + b) / 2, b - 0.3)) if f is not None]
        m = np.maximum.reduce(ms) if ms else np.zeros((SH, SW), np.float32)
        others = [r for s, e, r in placed if s < b and e > a]
        cands = rects(g)
        scores = [overlap(m, r, others) + 0.02 * k for k, (_, r) in enumerate(cands)]
        k = int(np.argmin(scores))
        upd, r = cands[k]
        g["props"].update(upd)
        placed.append((a, b, r))
        # QA image: mask + chosen rect
        img = frame(tl, (a + b) / 2) or Image.new("RGB", (SW, SH))
        d = ImageDraw.Draw(img)
        over = Image.fromarray((m * 120).astype(np.uint8)).convert("L")
        img.paste(Image.new("RGB", (SW, SH), (255, 0, 80)), (0, 0), over.point(lambda v: min(255, v * 2)))
        d.rectangle([v / K for v in r], outline=(0, 255, 120), width=3)
        d.text((6, 6), f"{gi} {g['comp']} {g['at']:.1f}s score {scores[k]:.2f}", fill=(255, 255, 0))
        img.save(QA / f"{gi:02d}.jpg")
        print(f"{gi:2d} {g['comp']:10s} at {a:6.1f}s -> {upd} score {scores[k]:.2f}", flush=True)
    for g in tl["graphics"]:
        for kk in ("at", "item_t0"):
            g.pop(kk, None)
    for x in tl["vo"] + tl.get("chapters", []):
        x.pop("at", None)
    for it in tl["video"]:
        it.pop("t0", None)
    TLF.write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
