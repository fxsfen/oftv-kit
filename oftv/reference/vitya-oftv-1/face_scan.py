"""Face boxes per clip (mediapipe, 2 fps, display orientation) -> assets/analysis/faces.json
{clip: [[t, [[x0, y0, x1, y1], ...]], ...]} in 0..1 frame coordinates. Used to keep pop-ups off faces."""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import mediapipe as mp
import numpy as np

PROJ = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\fosfe\Downloads") / "витя 1ви"
OUT = PROJ / "assets/analysis/faces.json"
W, H = 480, 270  # landscape analysis size; portrait clips come out 270x480 after autorotate scale


def frames(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
                        "-of", "json", str(path)], capture_output=True, text=True)
    j = json.loads(p.stdout)["streams"][0]
    rot = next((abs(int(s.get("rotation", 0))) for s in j.get("side_data_list", []) if "rotation" in s), 0)
    w, h = j["width"], j["height"]
    if rot in (90, 270):
        w, h = h, w
    ww, hh = (W, H) if w >= h else (H, W)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps=2,scale={ww}:{hh}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(raw) // (ww * hh * 3)
    return np.frombuffer(raw[: n * ww * hh * 3], dtype=np.uint8).reshape(n, hh, ww, 3)


def scan(path):
    det = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    res = []
    for i, f in enumerate(frames(path)):
        r = det.process(f)
        boxes = []
        for d in r.detections or []:
            b = d.location_data.relative_bounding_box
            boxes.append([round(max(0, b.xmin), 3), round(max(0, b.ymin), 3),
                          round(min(1, b.xmin + b.width), 3), round(min(1, b.ymin + b.height), 3)])
        res.append([i / 2, boxes])
    return path.stem, res


if __name__ == "__main__":
    out = json.loads(OUT.read_text()) if OUT.exists() else {}
    clips = [c for c in sorted(SRC.glob("*.MOV")) if c.stem not in out]
    with ThreadPoolExecutor(3) as ex:
        for k, r in ex.map(scan, clips):
            out[k] = r
            OUT.write_text(json.dumps(out))
            print(k, sum(1 for _, b in r if b), "/", len(r), flush=True)
    print("ALL DONE", flush=True)
