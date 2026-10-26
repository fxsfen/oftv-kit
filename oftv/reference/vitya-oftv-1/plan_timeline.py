"""Eva x Lily "Halloween Dinner" collab (folder Downloads/витя 1ви, script: Google Doc 1-gVjZlM67...,
artifacts/script_en.md). Eva = 4K shoot (IMG_76xx-77xx), Lily = phone shoot (IMG_07xx-08xx).

Scenes follow the script: intro (Eva/Lily alternating) -> 1 Eva's ingredients -> 2 Lily's ingredients ->
3 Eva bakes the pie -> 4 Lily's mini pizzas -> 5 results -> 6 taste test -> goodbye -> split-screen finale.
Best take per line = the last clean full one (large-v3 per clip). Subtitles = Whisper words with per-clip fixes
of accent mishears (script wording kept where she actually says it; she says "raspberry", not "cherry").
Lily's overhead pizza shots are vertical -> 16:9 band cut out (`crop_y`). Pop-ups: Halloween set
(remotion-composer/src/oftv/HalloweenGraphics.tsx); positions picked later by place_graphics.py so they never
sit on a person (isnet person mask on the actual frame).
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[1]
A = PROJ / "assets/analysis"
SRC = Path(r"C:\Users\fosfe\Downloads") / "витя 1ви"
LOFI = PROJ.parents[1] / "music_library/lofi"
MAXC = 32
WORDS = json.load(open(A / "transcripts.json", encoding="utf-8"))
MOTION = json.load(open(A / "motion.json"))

# per-clip phrase fixes (heard -> what she says / means)
FIX = {
    "IMG_7606": [("say a special to OFF TV", "say a special thank you to OFTV"), ("OFF TV.", "OFTV."),
                 ("going prepare and Halloween dinner", "going to prepare a Halloween dinner")],
    "IMG_0786": [("Lulu,", "Lily,")],
    "IMG_7635": [("I'll also with a little", "I'll also use a little")],
    "IMG_7655": [("keep calm of the dough", "keep some of the dough")],
    "IMG_0792": [("How let me show that", "Now let me show you what")],
    "IMG_0798": [("in spider by pumpkins", "inspired by pumpkins")],
    "IMG_7676": [("cut out spooky face.", "cut out a spooky face.")],
    "IMG_7693": [("I'm internationally making it a little anyway.", "I'm intentionally making it a little uneven.")],
    "IMG_7705": [("putting in in the oven", "putting it in the oven")],
    "IMG_0814": [("I am tuning the dog", "I'm dividing the dough")],
    "IMG_0816": [("and turning to make them really there's some size", "and trying to make them roughly the same size")],
    "IMG_0818": [("and now some the most fun part decoration them", "and now comes the most fun part: decorating them")],
    "IMG_0819": [("the pepper foremost and our details are the corn", "the pepper for mouths and other details, and the corn")],
    "IMG_0822": [("different dishes", "different designs")],
    "IMG_0842": [("Now all that left", "Now all that's left")],
    "IMG_0862": [("I'm Ger and I", "I agree, and I"), ("all of these", "all of this")],
    "IMG_7733": [("spending little", "spending this little")],
    "IMG_7747": [("I love to see deer.", "I'd love to see you there.")],
    "IMG_0866": [("waiting for on my", "waiting for you on my"), ("to things. Don't share", "to things I don't share")],
    "IMG_0872": [("Halloween, Yawa!", "Halloween, Eva!")],
    "IMG_7751": [("I will see soon, Lilo.", "I will see you soon, Lily!")],
}
STOP = {"the", "a", "an", "to", "my", "and", "of", "your", "for", "in", "on", "with", "but", "so", "that", "i'm",
        "how", "it's", "if", "is", "are", "i", "can", "you", "this", "these", "make", "just", "little", "few", "which",
        "when", "what", "be", "very", "such", "it", "some", "i'll", "let's", "we", "our", "will", "am"}

_dur = {}


def dur(k):
    if k not in _dur:
        _dur[k] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                        str(SRC / f"{k}.MOV")], capture_output=True, text=True).stdout)
    return _dur[k]


E = {}


def energy(k):
    if k not in E:
        w = wave.open(str(A / "wav16" / f"{k}.wav"))
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        hop = int(w.getframerate() * 0.02)
        n = len(x) // hop
        E[k] = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    return E[k]


def quietest(k, t, lo, hi):
    r = energy(k)
    i0, i1 = max(0, int((t + lo) / 0.02)), min(len(r) - 1, int((t + hi) / 0.02))
    return round((i0 + int(np.argmin(r[i0:i1 + 1]))) * 0.02, 3)


def speech_end(k, t):
    """Whisper ends words early: last loud 20 ms frame within 1.2 s after t, + 0.25 s."""
    r = energy(k)
    floor = np.percentile(r, 20)
    i0 = int(t / 0.02)
    loud = [i for i in range(i0, min(len(r), i0 + 60)) if r[i] > floor + 14]
    return round((loud[-1] * 0.02 if loud else t) + 0.25, 3)


def voice_onset(k, a, b, db_below=10.0, pre=0.07, hold=6):
    """Cut breaths / sighs / "ah" before a line (clients asked, 10-26): from `a`, the first moment the level stays
    within `db_below` dB of the line's typical loudness (p80 over [a, b]) for 60 ms; start `pre` s before it."""
    r = energy(k)
    i0, i1 = int(a / 0.02), min(len(r), int(b / 0.02))
    if i1 - i0 < 10:
        return a
    thr = np.percentile(r[i0:i1], 80) - db_below
    for i in range(i0, i1 - hold):
        if all(r[i + j] > thr for j in range(hold)):  # 120 ms of real voice (a click or a breath never holds)
            return round(max(a, i * 0.02 - pre), 3)
    return a


def breaths(k, a, b, gap_min=0.35, after=0.12, before=0.09):
    """Breath noises inside a line: in every pause >= gap_min between voiced runs, the audible-but-not-voice part
    (above room noise + 10 dB) is muted, keeping `after`/`before` s of air around the words. Source times."""
    r = energy(k)
    i0, i1 = int(a / 0.02), min(len(r), int(b / 0.02))
    if i1 - i0 < 20:
        return []
    seg = r[i0:i1]
    voiced = seg > np.percentile(seg, 80) - 10
    floor = np.percentile(seg, 10)
    idx = np.nonzero(voiced)[0]
    out = []
    for p, q in zip(idx[:-1], idx[1:]):
        if (q - p) * 0.02 < gap_min:
            continue
        lo, hi = p + int(after / 0.02), q - int(before / 0.02)
        noisy = [j for j in range(lo, hi) if seg[j] > floor + 10]
        if len(noisy) >= 4:
            out.append([round(a + (noisy[0] - 1) * 0.02, 3), round(a + (noisy[-1] + 2) * 0.02, 3)])
    return out


ONSETS = []  # (clip, old start, new start) - report


def words(k):
    """Whisper words with per-clip fixes applied (fix spreads the old span's times over the new tokens)."""
    ws = [[s, e, w.strip()] for s, e, w in WORDS[k] if w.strip() not in ("Thank", "you.", "You", "you", "Thank you.")
          or k in ("IMG_7733", "IMG_7746", "IMG_7739", "IMG_0871")]
    for bad, good in FIX.get(k, []):
        b, g = bad.split(), good.split()
        for i in range(len(ws) - len(b) + 1):
            if [x[2] for x in ws[i:i + len(b)]] == b:
                s, e = ws[i][0], ws[i + len(b) - 1][1]
                step = (e - s) / len(g)
                ws[i:i + len(b)] = [[s + j * step, s + (j + 1) * step, t] for j, t in enumerate(g)]
                break
        else:
            print("  ! fix not found", k, bad)
    return ws


def cues(ws):
    toks = [w[2] for w in ws]
    n = len(toks)
    best = [(0.0, -1)] + [(1e9, -1)] * n
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            txt = " ".join(toks[i:j])
            if len(txt) > MAXC and j - i > 1:
                break
            last = toks[j - 1].lower().strip(",.!?:")
            cost = (len(txt) - 24) ** 2 / 50 + 3
            if j < n and (last in STOP or last.isdigit()):
                cost += 40
            if j < n and toks[j - 1][-1] in ",.!?:":
                cost -= 4
            if re.search(r"[.!?] ", txt):
                cost += 25
            if len(txt) < 10 and n > 1:
                cost += 15
            if best[i][0] + cost < best[j][0]:
                best[j] = (best[i][0] + cost, i)
    seg, j = [], n
    while j > 0:
        i = best[j][1]
        seg.append((i, j))
        j = i
    return [[ws[i][0], ws[j - 1][1], " ".join(toks[i:j])] for i, j in reversed(seg)]


def active(k, i, o, length):
    """Start of the most active `length` window in [i, o] (hands working, not a still frame)."""
    d = MOTION.get(k)
    if not d or o - i <= length + 0.01:
        return round(i + max(0.0, (o - i - length) / 2), 3)
    best, bs, t = -1.0, i, i
    while t + length <= o + 1e-6:
        a, b = int(t * 4), max(int((t + length) * 4), int(t * 4) + 1)
        m = sum(d[a:b]) / (b - a)
        if m > best:
            best, bs = m, t
        t += 0.25
    return round(bs, 3)


class TL:
    def __init__(self):
        self.video, self.vo, self.sections, self.subs, self.graphics = [], [], [], {}, []

    def _sub(self, k, a, b):
        ws = [w for w in words(k) if a - 0.05 <= w[0] < b - 0.05]
        self.subs.setdefault(k, []).extend(cues(ws))

    def talk(self, k, a, b, group="main", zoom=1.0, pad_tail=0.0, snap=True, gfx=(), max_out=None):
        """On-camera piece. a/b in source seconds; b is pushed to the real end of the last word, but never past
        max_out (where she reaches for the camera)."""
        if snap:
            a = quietest(k, a, -0.12, 0.08)
            b = min(speech_end(k, b), dur(k) - 0.05, max_out or 1e9)
            a0, a = a, voice_onset(k, a, b)
            ONSETS.append((k, a0, a))
        it = {"group": group, "src": k, "in": round(a, 3), "out": round(b, 3), "speech": True,
              "mute": breaths(k, a, b)}
        if zoom != 1.0:
            it["zoom"] = zoom
        if pad_tail:
            it["pad_tail"] = pad_tail
        self.video.append(it)
        self._sub(k, a, b)
        self._gfx(len(self.video) - 1, gfx)
        return len(self.video) - 1

    def broll(self, k, i, o, length=None, group="main", crop_y=None, gfx=()):
        length = length or (o - i)
        st = active(k, i, o, length)
        it = {"group": group, "src": k, "in": st, "out": round(st + length, 3)}
        if crop_y is not None:
            it["crop_y"] = crop_y
        self.video.append(it)
        self._gfx(len(self.video) - 1, gfx)
        return len(self.video) - 1

    def voice(self, pieces, clips, group="main", lead=0.4, gap=0.45, tail=0.6, gfx=()):
        """Voice pieces [(clip, a, b)] laid one after another over b-roll [(clip, in, out, crop_y)] fitted to them."""
        ps = [(k, quietest(k, a, -0.12, 0.06), min(speech_end(k, b), dur(k) - 0.05)) for k, a, b in pieces]
        ps2 = [(k, voice_onset(k, s, e), e) for k, s, e in ps]
        ONSETS.extend((k, s, s2) for (k, s, _), (_, s2, _) in zip(ps, ps2))
        ps = ps2
        need = lead + sum(e - s for _, s, e in ps) + gap * (len(ps) - 1) + tail
        avail = sum(o - i for _, i, o, _ in clips)
        kf = need / avail
        assert kf <= 1, (pieces, need, avail)
        first = len(self.video)
        for k, i, o, cy in clips:
            self.broll(k, i, o, (o - i) * kf, group, cy)
        t = lead
        starts = []
        for k, s, e in ps:
            self.vo.append({"src": k, "in": s, "out": e, "item": first, "offset": round(t, 3), "mute": breaths(k, s, e)})
            self._sub(k, s, e)
            starts.append(t)
            t += (e - s) + gap
        for off, comp, props, d, *rest in gfx:  # offsets relative to the block start
            self.graphics.append({"comp": comp, "props": props, "dur": d, "item": first, "offset": off,
                                  "sfx": rest[0] if rest else "pop"})
        return first, starts

    def _gfx(self, item, gfx):
        for off, comp, props, d, *rest in gfx:
            self.graphics.append({"comp": comp, "props": props, "dur": d, "item": item, "offset": off,
                                  "sfx": rest[0] if rest else "pop"})

    def scene(self, n, title, who, color="orange"):
        self.graphics.append({"comp": "HwScene", "props": {"index": n, "title": title, "who": who, "color": color},
                              "dur": 3.4, "item": len(self.video), "offset": 0.2, "sfx": "whoosh"})
        self.sections.append({"index": n, "title": title, "item": len(self.video), "offset": 0.2, "chapter": title})


EVA_ING = ["250 g flour", "120 g butter", "80 g sugar", "1 egg", "Vanilla sugar", "Pinch of salt", "300 g raspberries",
           "Powdered sugar"]
LILY_ING = ["Pizza dough", "Tomato sauce", "Mozzarella", "Olive oil", "Black olives", "Sweet pepper", "Corn"]


def main():
    t = TL()
    # ---------------- INTRO ----------------
    t.talk("IMG_7606", 0.0, 26.4, "intro", gfx=[
        (0.4, "HwTitle", {"eyebrow": "Eva x Lily", "lines": ["Halloween", "Dinner"], "sub": "a spooky little collab"}, 5.0),
        (6.2, "HwName", {"name": "Eva", "role": "raspberry pie", "icon": "berry", "color": "orange"}, 3.8)])
    t.talk("IMG_0786", 4.8, 22.7, "intro", zoom=1.0, gfx=[
        (0.6, "HwName", {"name": "Lily", "role": "mini pizzas", "icon": "pizza", "color": "purple"}, 3.8),
        (1.2, "TagPlate", {"tag": "@Little_lilyyy"}, 5.5)])
    t.talk("IMG_7608", 0.0, 4.0, "intro", gfx=[
        (0.5, "HwSticker", {"text": "Raspberry pie", "sub": "with a spooky face", "icon": "berry", "color": "blood"}, 3.2)])
    t.talk("IMG_0788", 1.2, 5.9, "intro", gfx=[
        (1.0, "HwSticker", {"text": "Mini pizzas", "sub": "with fun faces", "icon": "pizza", "color": "purple"}, 3.4)])
    t.talk("IMG_0790", 1.2, 5.4, "intro", pad_tail=0.5)

    # ---------------- 1. EVA'S INGREDIENTS ----------------
    t.scene(1, "Pie Ingredients", "Eva", "orange")
    t.talk("IMG_7619", 0.0, 4.3)
    t.talk("IMG_7628", 0.0, 25.4, gfx=[
        (0.6, "HwList", {"title": "Raspberry Pie", "items": EVA_ING, "icon": "berry", "color": "orange", "every": 3.0}, 26.5)])
    t.talk("IMG_7633", 0.0, 4.6)
    t.talk("IMG_7635", 0.0, 5.4)
    t.talk("IMG_7655", 0.0, 5.8, gfx=[(1.6, "HwSticker", {"text": "Spooky face", "sub": "coming soon", "icon": "ghost", "color": "orange"}, 3.0)])
    t.talk("IMG_7666", 0.0, 12.2)

    # ---------------- 2. LILY'S INGREDIENTS ----------------
    t.scene(2, "Pizza Ingredients", "Lily", "purple")
    t.voice([("IMG_0792", 3.2, 7.6), ("IMG_0792", 11.4, 17.2), ("IMG_0794", 0.0, 5.9)],
         [("IMG_0795", 2.0, 63.0, None)], gfx=[
             (0.6, "HwList", {"title": "Mini Pizzas", "items": LILY_ING, "icon": "pizza", "color": "purple", "every": 2.2}, 17.5)])
    t.talk("IMG_0798", 0.95, 15.6, gfx=[(8.0, "HwSticker", {"text": "Pumpkins", "sub": "& spiders", "icon": "spider", "color": "purple"}, 3.6)])
    t.talk("IMG_0806", 4.55, 10.1)  # 3.2-3.6 = leftover "this" of the stumble

    # ---------------- 3. EVA BAKES THE PIE ----------------
    t.scene(3, "Baking the Pie", "Eva", "orange")
    t.talk("IMG_7668", 0.0, 1.4)
    t.talk("IMG_7671", 1.0, 9.6, gfx=[(0.4, "HwStep", {"step": 1, "total": 5, "label": "Make the dough", "who": "Eva", "color": "orange"}, 4.0)])
    t.broll("IMG_7671", 10.5, 29.0, 3.2)
    t.talk("IMG_7671", 29.9, 34.1)
    t.talk("IMG_7673", 0.0, 6.0, gfx=[(0.4, "HwStep", {"step": 2, "total": 5, "label": "Egg & vanilla", "who": "Eva", "color": "orange"}, 3.6)])
    t.broll("IMG_7673", 8.0, 96.0, 3.5)
    t.talk("IMG_7673", 98.0, 103.5, gfx=[(0.3, "HwStep", {"step": 3, "total": 5, "label": "Knead it smooth", "who": "Eva", "color": "orange"}, 3.6)])
    t.broll("IMG_7673", 105.0, 160.0, 3.0)
    t.talk("IMG_7673", 161.1, 164.0)
    t.talk("IMG_7676", 0.0, 5.7, gfx=[(0.3, "HwStep", {"step": 4, "total": 5, "label": "Raspberry filling", "who": "Eva", "color": "orange"}, 4.0)])
    t.broll("IMG_7676", 7.0, 210.0, 4.0)
    t.talk("IMG_7676", 216.5, 225.5, gfx=[(0.3, "HwStep", {"step": 5, "total": 5, "label": "Spooky face top", "who": "Eva", "color": "orange"}, 4.0)])
    t.broll("IMG_7677", 10.0, 170.0, 3.5)
    t.broll("IMG_7684", 12.0, 100.0, 3.5, gfx=[(0.5, "HwSticker", {"text": "Spooky face!", "icon": "ghost", "color": "orange"}, 2.8)])
    t.talk("IMG_7693", 0.0, 10.7)
    t.talk("IMG_7705", 0.0, 4.7, gfx=[(0.6, "HwSticker", {"text": "Into the oven", "icon": "oven", "color": "orange"}, 3.2)])

    # ---------------- 4. LILY'S MINI PIZZAS ----------------
    t.scene(4, "Mini Pizzas", "Lily", "purple")
    t.talk("IMG_0811", 1.0, 4.4)
    t.voice([("IMG_0814", 1.5, 5.0)], [("IMG_0824", 0.3, 10.2, 0.5), ("IMG_0825", 0.3, 11.3, 0.5)],
         gfx=[(0.3, "HwStep", {"step": 1, "total": 5, "label": "Divide the dough", "who": "Lily", "color": "purple"}, 3.6)])
    t.voice([("IMG_0816", 1.0, 7.6)], [("IMG_0826", 0.5, 27.0, 0.5), ("IMG_0827", 0.5, 11.0, 0.5), ("IMG_0828", 20.0, 200.0, 0.5)],
         gfx=[(0.3, "HwStep", {"step": 2, "total": 5, "label": "Roll & shape", "who": "Lily", "color": "purple"}, 3.6)])
    t.voice([("IMG_0816", 10.0, 13.4)], [("IMG_0830", 30.0, 72.0, 0.5)],
         gfx=[(0.3, "HwStep", {"step": 3, "total": 5, "label": "Tomato sauce", "who": "Lily", "color": "purple"}, 3.4)])
    t.voice([("IMG_0817", 0.0, 2.0)], [("IMG_0831", 5.0, 60.0, 0.5)],
         gfx=[(0.2, "HwStep", {"step": 4, "total": 5, "label": "Mozzarella", "who": "Lily", "color": "purple"}, 3.0)])
    t.voice([("IMG_0818", 0.0, 4.2), ("IMG_0819", 0.0, 12.7)],
         [("IMG_0832", 5.0, 135.0, 0.5), ("IMG_0833", 1.0, 27.0, 0.5), ("IMG_0834", 2.0, 72.0, None)],
         gfx=[(0.3, "HwStep", {"step": 5, "total": 5, "label": "Decorate!", "who": "Lily", "color": "purple"}, 3.4),
              (7.5, "HwSticker", {"text": "Olive eyes", "icon": "spider", "color": "purple"}, 3.2)])
    t.voice([("IMG_0822", 0.0, 7.2)], [("IMG_0835", 0.3, 6.6, None), ("IMG_0836", 0.3, 8.5, None)])
    t.talk("IMG_0842", 0.95, 13.1, gfx=[(1.0, "HwSticker", {"text": "Into the oven", "icon": "oven", "color": "purple"}, 3.2)])
    t.broll("IMG_0837", 0.2, 7.8, 4.0)

    # ---------------- 5. RESULTS ----------------
    t.scene(5, "The Results", "Eva & Lily", "slime")
    t.talk("IMG_7706", 0.0, 2.1, gfx=[(0.3, "HwStamp", {"text": "READY!", "sub": "RASPBERRY PIE", "color": "orange"}, 2.6)])
    t.talk("IMG_7711", 0.0, 17.1)
    t.talk("IMG_0845", 0.8, 3.9, gfx=[(0.3, "HwStamp", {"text": "READY!", "sub": "MINI PIZZAS", "color": "purple"}, 2.6)])
    t.broll("IMG_0847", 0.3, 10.2, 4.0)
    t.talk("IMG_0849", 0.75, 6.7)
    for k, i, o in (("IMG_0850", 0.2, 2.9), ("IMG_0852", 0.2, 5.0), ("IMG_0854", 0.2, 4.9), ("IMG_0855", 0.2, 5.5)):
        t.broll(k, i, o, 2.2)

    # ---------------- 6. TASTE TEST ----------------
    t.scene(6, "Taste Test", "Eva & Lily", "slime")
    t.talk("IMG_7716", 0.0, 3.2)
    t.broll("IMG_7717", 1.0, 38.0, 4.0)
    t.talk("IMG_7718", 8.0, 11.8, gfx=[(0.2, "HwStamp", {"text": "YUM!", "color": "blood"}, 2.2)])
    t.talk("IMG_7718", 15.6, 21.4)
    t.talk("IMG_7719", 1.8, 7.5)
    t.talk("IMG_0856", 0.9, 3.8)
    t.broll("IMG_0857", 0.5, 20.0, 3.5)
    t.talk("IMG_0858", 7.8, 17.3, gfx=[(0.2, "HwStamp", {"text": "MMM!", "color": "purple"}, 2.2)])
    t.talk("IMG_0860", 1.1, 7.5)
    t.talk("IMG_7724", 0.0, 6.4)
    t.talk("IMG_0862", 0.82, 11.7, pad_tail=0.5)

    # ---------------- GOODBYE ----------------
    t.talk("IMG_7733", 0.0, 4.9, "outro")
    t.talk("IMG_7739", 0.0, 5.2, "outro", zoom=1.08)
    t.talk("IMG_7746", 0.0, 6.6, "outro")
    t.talk("IMG_7747", 0.0, 1.6, "outro", zoom=1.08)
    t.talk("IMG_0866", 0.9, 18.7, "outro", gfx=[(3.9, "TagPlate", {"tag": "@Little_lilyyy"}, 5.5)])
    t.talk("IMG_0871", 0.9, 8.5, "outro", zoom=1.08, max_out=9.82)
    t.talk("IMG_7763", 0.0, 6.9, "outro")
    # split-screen finale: Lily "Happy Halloween, Eva!" -> Eva "I will see you soon, Lily!" -> both "Bye everyone!"
    L1 = (quietest("IMG_0872", 0.7, -0.1, 0.1), min(speech_end("IMG_0872", 2.3), 2.95))  # reaches at 3.0
    R1 = (quietest("IMG_7751", 0.0, -0.05, 0.1), speech_end("IMG_7751", 2.2))
    d1 = (L1[1] - L1[0]) + 0.25 + (R1[1] - R1[0]) + 0.2
    t.video.append({"group": "outro", "src": "IMG_0872", "in": 0, "out": d1, "dur": round(d1, 3), "split": [
        {"src": "IMG_0872", "in": L1[0], "out": L1[1], "speech": True, "pad_head": 0.0},
        {"src": "IMG_7751", "in": R1[0], "out": R1[1], "speech": True, "pad_head": round(L1[1] - L1[0] + 0.25, 3)}]})
    t._gfx(len(t.video) - 1, [(0.0, "HwSplit", {"left": "Lily", "right": "Eva"}, round(d1 + 3.6, 2))])
    L2 = (0.85, 2.75)  # arm at the lens before 0.85 and after 2.75; the wave stays
    R2 = (quietest("IMG_7752", 0.0, -0.05, 0.1), min(speech_end("IMG_7752", 1.3) + 0.8, dur("IMG_7752") - 0.05))
    d2 = max(L2[1] - L2[0], R2[1] - R2[0])
    t.video.append({"group": "outro", "src": "IMG_0873", "in": 0, "out": d2, "dur": round(d2, 3), "split": [
        {"src": "IMG_0873", "in": L2[0], "out": L2[1], "speech": True},
        {"src": "IMG_7752", "in": R2[0], "out": R2[1], "speech": True}]})
    t._sub("IMG_0872", L1[0], L1[1])
    t._sub("IMG_7751", R1[0], R1[1])
    t.subs.setdefault("IMG_0873", []).append([L2[0], L2[0] + 1.6, "Bye-bye, everyone!"])

    # music: calm but spooky-titled CC0 lofi (no music in the folder), chained with 6 s crossfades
    music = [LOFI / f"HoliznaCC0 - {n}.mp3" for n in ("Ghost Town", "Into The Mist(Lofi, Calm, Relaxed)",
                                                     "Moon Unit(Lofi, Reflection, Dreamy)", "Ease into Night(Lofi, Relax, Chill)")]
    tl = {"tag": None, "music": [m.as_posix() for m in music],
          "sources": {k: (SRC / f"{k}.MOV").as_posix() for k in
                      {v["src"] for v in t.video} | {v["src"] for v in t.vo} |
                      {x["src"] for v in t.video for x in v.get("split", [])}},
          "video": t.video, "vo": t.vo, "sections": [], "chapters": t.sections, "graphics": t.graphics}
    (A / "subs_en.json").write_text(json.dumps(t.subs, indent=1, ensure_ascii=False), encoding="utf-8")
    (PROJ / "artifacts").mkdir(exist_ok=True)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps(tl, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum((v["dur"] if v.get("split") else v["out"] - v["in"]) + v.get("pad_tail", 0) for v in t.video) - 1.0
    print(f"items={len(t.video)} vo={len(t.vo)} graphics={len(t.graphics)} ~duration={tot:.1f}s ({tot / 60:.1f} min)")
    (A / "onsets.json").write_text(json.dumps(ONSETS))
    nm = sum(len(v.get("mute", [])) for v in t.video + t.vo)
    print("breaths muted inside lines:", nm, "| s:", round(sum(b - a for v in t.video + t.vo for a, b in v.get("mute", [])), 1))
    print("breath trims:", sum(1 for _, x, y in ONSETS if y - x > 0.05), "of", len(ONSETS),
          "| total", round(sum(y - x for _, x, y in ONSETS), 1), "s")
    print("long cues:", [c[2] for v in t.subs.values() for c in v if len(c[2]) > MAXC])


if __name__ == "__main__":
    main()
