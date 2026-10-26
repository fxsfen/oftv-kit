"""Render the two-source OFTV remix from artifacts/edit_map.json.

Picture : each segment is trimmed from its 4K/25p source, converted to 30 fps and
          scaled to the target size. Consecutive segments from the same source are
          joined with hard cuts; every A<->B switch is a whip (xfade smoothleft +
          directional blur) with a whoosh.
Speech  : taken from the Demucs vocal stem (original music removed), cut on
          vocal-energy minima, 20 ms fades, spectral match A<->B, per-segment
          level trim toward the common median (clamped), gentle compression,
          then the whole dialogue bed -> -14 LUFS and -6 dB.
Music   : the three supplied tracks back to back with crossfades,
          each -> -14 LUFS, then -16 dB, faded in/out, light ducking under speech.
SFX     : whoosh -> -14 LUFS, then -11 dB.

Usage: python render_remix.py --res 480|1440 [--plan-only]
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soundfile as sf

PROJ = Path(__file__).resolve().parents[1]
ROOT = PROJ.parents[1]
WHOOSH = ROOT / "projects/miya-moore-oftv/assets/sfx/whoosh.wav"
POP = ROOT / "projects/miya-moore-oftv/assets/sfx/pop.wav"
FPS = 30
XF = 0.5        # whip duration
LEAD = 0.35     # extra picture around speech at A<->B switches (muted)
HOP = 0.01
SR = 48000


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:220], flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def ff(*args):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def ebur(path, extra=()):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), *extra, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    summ = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    tp = re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", summ)
    return i, (float(tp.group(1)) if tp else None)


# ----------------------------------------------------------------- planning
def vocal_env(key):
    x, sr = sf.read(PROJ / f"assets/audio/{key}_vocals.wav", dtype="float32")
    m = x.mean(1) if x.ndim > 1 else x
    hop = int(sr * HOP)
    n = len(m) // hop
    return 20 * np.log10(np.sqrt((m[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


QUIET_DB = -45.0
MIN_GAP = 0.05


def quiet_runs(env):
    q = env < QUIET_DB
    runs, start = [], None
    for k, v in enumerate(q):
        if v and start is None:
            start = k
        elif not v and start is not None:
            if (k - start) * HOP >= MIN_GAP:
                runs.append((start * HOP, k * HOP))
            start = None
    if start is not None:
        runs.append((start * HOP, len(q) * HOP))
    return runs


def snap(env, runs, t, side):
    """Put a boundary inside the real vocal pause nearest the word edge (energy, not ASR timing)."""
    if side == "in":
        if t < 0.05:
            return 0.0, 0.0
        c = [r for r in runs if t - 0.6 <= r[1] <= t + 0.3]
        if not c:
            return round(t - 0.05, 3), None
        g0, g1 = min(c, key=lambda r: abs(r[1] - t))
        cut = max(g0 + (g1 - g0) / 2, g1 - 0.10)
    else:
        c = [r for r in runs if t - 0.3 <= r[0] <= t + 0.6]
        if not c:
            return round(t + 0.08, 3), None
        g0, g1 = min(c, key=lambda r: abs(r[0] - t))
        cut = min(g0 + (g1 - g0) / 2, g0 + 0.16)
    return round(cut, 3), round(g1 - g0, 2)


def merged_segments(segs):
    """Segments that are contiguous in their source play as one continuous take."""
    out = []
    for s in segs:
        p = out[-1] if out else None
        if p and p["src"] == s["src"] and abs(s["s"] - p["e"]) < 0.6:
            p["e"] = s["e"]
            for k in ("out_fix", "v_tail"):
                p.pop(k, None)
                if k in s:
                    p[k] = s[k]
            p["text"] += " " + s["text"]
        else:
            out.append(dict(s))
    return out


def pieces(s, v_in, n):
    """Picture of one item as [src, start, frames] runs. 'cover' = [[from, to, src, start], ...] in the
    item's own source time: that range shows silent footage from another place (hides stock / jump cuts)."""
    out, f = [], 0
    for c0, c1, csrc, cstart, *opt in sorted(s.get("cover", [])):
        f0 = max(f, round((c0 - v_in) * FPS))
        f1 = min(n, round((c1 - v_in) * FPS))
        if f0 > f:
            out.append([s["src"], round(v_in + f / FPS, 4), f0 - f])
        if f1 > f0:
            # optional 5th field "freeze": hold the frame at cstart (hides the sources' flash transitions)
            out.append([csrc, cstart, f1 - f0] + (["freeze"] if opt and opt[0] == "freeze" else []))
        f = max(f, f1)
    if f < n:
        out.append([s["src"], round(v_in + f / FPS, 4), n - f])
    return out


def plan(em):
    env = {k: vocal_env(k) for k in em["sources"]}
    runs = {k: quiet_runs(e) for k, e in env.items()}
    segs = merged_segments(em["segments"])
    items = []
    for i, s in enumerate(segs):
        # in_fix / out_fix in the edit map override the automatic snap after a manual check
        a_in, f_in = (s["in_fix"], "fix") if "in_fix" in s else snap(env[s["src"]], runs[s["src"]], s["s"], "in")
        a_out, f_out = (s["out_fix"], "fix") if "out_fix" in s else snap(env[s["src"]], runs[s["src"]], s["e"], "out")
        sw_before = i > 0 and segs[i - 1]["src"] != s["src"]
        sw_after = i + 1 < len(segs) and segs[i + 1]["src"] != s["src"]
        # v_in_fix: picture starts later than the automatic lead (skips a flash frame at the head)
        v_in = s.get("v_in_fix", max(0.0, a_in - (LEAD if sw_before else 0.0)))
        v_out = a_out + (LEAD if sw_after else 0.0) + s.get("v_tail", 0.0)
        n = round((v_out - v_in) * FPS)
        items.append({"i": i, "src": s["src"], "sec": s["sec"], "a_in": a_in, "a_out": a_out, "v_in": round(v_in, 3),
                      "n": n, "switch_before": sw_before, "edge_floor_db": [f_in, f_out], "text": s["text"],
                      "pieces": pieces(s, v_in, n)})
    t = 0.0
    for it in items:
        if it["switch_before"]:
            t -= XF
        it["t0"] = round(t, 4)
        it["a_at"] = round(t + it["a_in"] - it["v_in"], 4)
        t += it["n"] / FPS
    return items, t


# ----------------------------------------------------------------- picture
def render_items(em, items, work, w, h, fast):
    import hashlib
    files = []
    def vf_for(src):
        # crop may be one string for all sources or {"A": ..., "B": ...}
        c = em.get("crop")
        c = c.get(src) if isinstance(c, dict) else c
        return ((f"crop={c}," if c else "") + (em['prefilter'] + ',' if em.get('prefilter') else '')
                + f"fps={FPS},scale={w}:{h}:flags=lanczos,setsar=1,format=yuv420p")
    vf = json.dumps({s: vf_for(s) for s in em["sources"]})
    for it in items:
        # content-addressed: re-trimming one item never reuses a stale file
        key = hashlib.md5(json.dumps([it["pieces"], vf]).encode()).hexdigest()[:10]
        dst = work / f"v_{it['i']:02d}_{key}.mkv"
        if not dst.exists():
            parts = []
            for k, (src, st, nf, *frz) in enumerate(it["pieces"]):
                p = work / f"p_{key}_{k}.mkv"
                pvf = vf_for(src) + (f",trim=end_frame=1,loop=loop={nf}:size=1:start=0,setpts=N/{FPS}/TB" if frz else "")
                ff("-ss", f"{st:.4f}", "-t", f"{nf / FPS + 0.3:.4f}", "-i", em["sources"][src], "-vf", pvf,
                   "-frames:v", nf, "-an",
                   "-c:v", "libx264", "-preset", "ultrafast" if fast else "medium", "-crf", "18" if fast else "10",
                   "-g", "30", p)
                parts.append(p)
            if len(parts) == 1:
                parts[0].replace(dst)
            else:
                lst = work / f"p_{key}.txt"
                lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
                ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst)
                for p in parts:
                    p.unlink()
        files.append(dst)
    groups, cur = [], []
    for f, it in zip(files, items):
        if it["switch_before"] and cur:
            groups.append(cur)
            cur = []
        cur.append((f, it))
    groups.append(cur)
    out = []
    for g, members in enumerate(groups):
        lst = work / f"g_{g:02d}.txt"
        lst.write_text("".join(f"file '{f.as_posix()}'\n" for f, _ in members))
        dst = work / f"g_{g:02d}.mkv"
        ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst)
        out.append({"file": dst, "t0": members[0][1]["t0"]})
    return out


# ----------------------------------------------------------------- audio
def band_db(x, sr):
    """Long-term average spectrum (dB) in 1/3-octave bands, speech frames only."""
    hop, nfft = 2048, 4096
    frames = np.lib.stride_tricks.sliding_window_view(x, nfft)[::hop]
    rms = 20 * np.log10(np.sqrt((frames ** 2).mean(1)) + 1e-9)
    frames = frames[rms > np.percentile(rms, 60)]
    spec = (np.abs(np.fft.rfft(frames * np.hanning(nfft), axis=1)) ** 2).mean(0)
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    centers = [100 * 2 ** (k / 3) for k in range(0, 23)]          # 100 Hz .. ~16 kHz
    out = []
    for c in centers:
        sel = (freqs >= c / 2 ** (1 / 6)) & (freqs < c * 2 ** (1 / 6))
        out.append(10 * np.log10(spec[sel].mean() + 1e-20))
    return np.array(centers), np.array(out)


def eq_match(work):
    """Meet-in-the-middle EQ: each source gets half of the A/B tonal difference (±4 dB max)."""
    curves = {}
    for k in "AB":
        x, sr = sf.read(PROJ / f"assets/audio/{k}_vocals.wav", dtype="float32")
        c, db = band_db(x.mean(1), sr)
        curves[k] = db - db.mean()
    diff = curves["A"] - curves["B"]
    diff = np.convolve(diff, [0.25, 0.5, 0.25], mode="same")      # smooth
    eq = {}
    for k, sign in (("A", -0.5), ("B", 0.5)):
        g = np.clip(sign * diff, -4, 4)
        eq[k] = "firequalizer=gain_entry='" + ";".join(f"entry({f:.0f},{v:.2f})" for f, v in zip(c, g)) + "'"
    (work / "eq_match.json").write_text(json.dumps({"bands_hz": c.round(0).tolist(),
                                                    "A_minus_B_db": diff.round(2).tolist()}, indent=1))
    return eq


def build_speech(em, items, work, total):
    eq = eq_match(work)
    clean = {}
    for k in em["sources"]:
        dst = work / f"{k}_voice_clean.wav"
        if not dst.exists():
            ff("-i", PROJ / f"assets/audio/{k}_vocals.wav", "-ac", "1", "-af",
               f"highpass=f=75,lowpass=f=16000,adeclick,afftdn=nr=8:nf=-60:tn=1,{eq[k]}",
               "-ar", SR, "-c:a", "pcm_f32le", dst)
        clean[k] = dst
    clips = []
    for it in items:
        raw = work / f"sp_{it['i']:02d}.wav"
        d = it["a_out"] - it["a_in"]
        ff("-ss", f"{it['a_in']:.4f}", "-i", clean[it["src"]], "-t", f"{d:.4f}", "-af",
           f"afade=t=in:d=0.02,afade=t=out:st={d - 0.03:.4f}:d=0.03", "-c:a", "pcm_f32le", raw)
        clips.append(raw)
    # per-segment level trim toward the median, clamped so the voice stays natural
    lv = [ebur(c)[0] for c in clips]
    med = float(np.median(lv))
    trims = [float(np.clip(med - v, -5, 5)) for v in lv]
    inp, fc = [], []
    for k, (c, it, g) in enumerate(zip(clips, items, trims)):
        inp += ["-i", c]
        ms = int(round(it["a_at"] * 1000))
        fc.append(f"[{k}:a]volume={g:.2f}dB,adelay={ms},apad[s{k}]")
    fc.append("".join(f"[s{k}]" for k in range(len(clips))) +
              f"amix=inputs={len(clips)}:normalize=0,atrim=0:{total:.3f}[o]")
    ff(*inp, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", SR, "-c:a", "pcm_f32le", work / "speech_raw.wav")
    comp = work / "speech_comp.wav"
    ff("-i", work / "speech_raw.wav", "-af",
       "acompressor=threshold=-26dB:ratio=2.5:attack=12:release=220:makeup=2,"
       "equalizer=f=3200:t=q:w=1.2:g=1.5", "-c:a", "pcm_f32le", comp)
    speech = work / "speech_bed.wav"
    # no loudness target / limiter here: build_mix sets the final dialogue level by block peaks
    # (a -14 LUFS gain + limiter at this stage flattened the speech peaks)
    ff("-i", comp, "-c:a", "pcm_f32le", speech)
    return speech, {"segment_lufs": [round(v, 1) for v in lv], "median": round(med, 1),
                    "trims_db": [round(t, 2) for t in trims], "eq": json.loads((work / "eq_match.json").read_text())}


def build_music(em, work, total):
    norm = []
    for k, m in enumerate(em["music"]):
        dst = work / f"music_{k}.wav"
        if not dst.exists():
            i0, _ = ebur(m)
            ff("-i", m, "-af", f"volume={-14 - i0:.2f}dB", "-ar", SR, "-ac", 2, "-c:a", "pcm_f32le", dst)
        norm.append(dst)
    chain = work / "music_chain.wav"
    inp = sum((["-i", f] for f in norm), [])
    fc, last = [], "[0:a]"
    for k in range(1, len(norm)):
        fc.append(f"{last}[{k}:a]acrossfade=d=6:c1=tri:c2=tri[m{k}]")
        last = f"[m{k}]"
    ff(*inp, "-filter_complex", ";".join(fc), "-map", last, "-c:a", "pcm_f32le", chain)
    dur = sf.info(str(chain)).duration
    if dur < total + 1:
        # loop the chain with a crossfade if the edit outgrows the three tracks
        ff("-i", chain, "-i", chain, "-filter_complex", "[0:a][1:a]acrossfade=d=4[m]", "-map", "[m]",
           "-c:a", "pcm_f32le", work / "music_long.wav")
        chain = work / "music_long.wav"
    return chain, round(dur, 2)


# OFTV mix levels (default since 2026-10-19), as 100 ms block peaks of each element in the final mix
DIA_MED, DIA_CEIL = -10.0, -6.0
MUS_MED, MUS_CEIL = -14.0, -10.0
SFX_PEAK = -12.0


def block_peaks(x, win=0.1):
    m = np.abs(x).max(1) if x.ndim > 1 else np.abs(x)
    hop = int(SR * win)
    n = len(m) // hop
    return 20 * np.log10(m[:n * hop].reshape(n, hop).max(1) + 1e-9)


def peak_stats(x, active):
    act = block_peaks(x)[active[:len(block_peaks(x))]]
    return {k: round(float(np.percentile(act, q)), 1) for k, q in (("p10", 10), ("p50", 50), ("p90", 90))} | \
        {"max": round(float(act.max()), 1)}


def activity(x, thr_db=-18):
    bp = block_peaks(x)
    return bp > np.percentile(bp, 95) + thr_db


def build_mix(speech, music, work, total, whooshes, pops=()):
    # dialogue bed (already evened per line + compressed) -> median block peak DIA_MED, ceiling DIA_CEIL
    v, _ = sf.read(speech, dtype="float32")
    sp_act = activity(v)
    g_v = DIA_MED - peak_stats(v, sp_act)["p50"]
    dia = work / "dia_final.wav"
    ff("-i", speech, "-af", f"volume={g_v:.2f}dB,alimiter=limit={10 ** (DIA_CEIL / 20):.4f}:level=false:attack=2:release=50,"
       "pan=stereo|c0=c0|c1=c0", "-c:a", "pcm_f32le", dia)   # mono -> both channels at full level (no -3 dB pan law)
    # music: smooth level, fades, -> median block peak MUS_MED while playing, ceiling MUS_CEIL; no ducking
    m1 = work / "music_proc.wav"
    ff("-i", music, "-af", f"atrim=0:{total:.3f},acompressor=threshold=-28dB:ratio=2:attack=60:release=600:makeup=1,"
       f"afade=t=in:d=2.5,afade=t=out:st={total - 5:.3f}:d=5", "-c:a", "pcm_f32le", m1)
    m, _ = sf.read(m1, dtype="float32")
    mu_act = activity(m)
    g_m = MUS_MED - peak_stats(m, mu_act)["p50"]
    mus = work / "music_stem.wav"
    ff("-i", m1, "-af", f"volume={g_m:.2f}dB,alimiter=limit={10 ** (MUS_CEIL / 20):.4f}:level=false:attack=5:release=120",
       "-c:a", "pcm_f32le", mus)
    # SFX: each sample's own peak -> SFX_PEAK
    sfx = {}
    for name, src in (("whoosh", WHOOSH), ("pop", POP)):
        x, _ = sf.read(src, dtype="float32")
        pk = 20 * np.log10(np.abs(x).max() + 1e-9)
        sfx[name] = work / f"{name}.wav"
        ff("-i", src, "-af", f"volume={SFX_PEAK - pk:.2f}dB", "-ar", SR, "-ac", 2, "-c:a", "pcm_f32le", sfx[name])
    fc, extra = [], []
    if whooshes:
        fc.append("[2:a]asplit=" + str(len(whooshes)) + "".join(f"[wh{i}]" for i in range(len(whooshes))))
        for i, t in enumerate(whooshes):
            fc.append(f"[wh{i}]adelay={int(max(0, t) * 1000)}:all=1,apad[w{i}]")
            extra.append(f"[w{i}]")
    if pops:
        fc.append("[3:a]asplit=" + str(len(pops)) + "".join(f"[pp{i}]" for i in range(len(pops))))
        for i, t in enumerate(pops):
            fc.append(f"[pp{i}]adelay={int(t * 1000)}:all=1,apad[p{i}]")
            extra.append(f"[p{i}]")
    fc.append(f"[0:a][1:a]{''.join(extra)}amix=inputs={2 + len(extra)}:normalize=0:duration=first,"
              "alimiter=limit=0.891:level=false[out]")
    mix = work / "mix.wav"
    ff("-i", dia, "-i", mus, "-i", sfx["whoosh"], "-i", sfx["pop"], "-filter_complex", ";".join(fc), "-map", "[out]",
       "-t", f"{total:.3f}", "-ar", SR, "-c:a", "pcm_s24le", mix)
    d2, _ = sf.read(dia, dtype="float32")
    m2, _ = sf.read(mus, dtype="float32")
    rep = {"gain_db": {"dialogue": round(g_v, 2), "music": round(g_m, 2)},
           "dialogue_peaks": peak_stats(d2, sp_act), "music_peaks": peak_stats(m2, mu_act)}
    (PROJ / "artifacts/mix_levels.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print("LEVELS", json.dumps(rep), flush=True)
    return mix


# ----------------------------------------------------------------- overlays + subtitles
def render_overlays(em, items, work, h):
    """Tag plate (Remotion TagPlate, VP9 alpha) at each time listed in edit_map['tag']['at']."""
    tag = em.get("tag")
    if not tag or not tag.get("at"):
        return []
    rc = ROOT / "remotion-composer"
    dst = work / f"ov_tag_{h}.webm"
    pf = work / "ov_tag.json"
    pf.write_text(json.dumps({"tag": tag["name"]}))
    if not dst.exists():
        run(["npx.cmd", "remotion", "render", "src/oftv/index.tsx", "TagPlate", dst, f"--props={pf}",
             "--codec=vp9", "--pixel-format=yuva420p", "--image-format=png", f"--scale={h / 2160}", "--log=error"],
            cwd=rc)
    out = []
    for a in tag["at"]:
        if "item" in a:   # anchored to a source time inside a timeline segment
            it = items[a["item"]]
            t = it["a_at"] + a["src_t"] - it["a_in"]
        else:
            t = a["t"]
        out.append({"file": dst, "start": round(t, 3)})
    return out


SMALL = {"the", "a", "an", "to", "my", "and", "of", "in", "with", "for", "your", "i", "on", "at", "or", "but",
         "it", "is", "that", "this", "you", "we", "so", "if", "as", "from", "into", "can", "be"}


def apply_edits(words, rules):
    """rules: [[old phrase, new phrase]] matched case-insensitively on bare tokens; new tokens share the span.
    An empty new phrase deletes the words."""
    bare = lambda w: re.sub(r"[^\w'°\-]", "", w.lower())
    for old, new in rules:
        o = old.lower().split()
        i = 0
        while i <= len(words) - len(o):
            if [bare(w["word"]) for w in words[i:i + len(o)]] == [bare(x) for x in o]:
                st, en = words[i]["start"], words[i + len(o) - 1]["end"]
                nt = new.split()
                step = (en - st) / max(1, len(nt))
                words[i:i + len(o)] = [{"word": x, "start": st + k * step, "end": st + (k + 1) * step}
                                       for k, x in enumerate(nt)]
                i += max(1, len(nt))
            else:
                i += 1
    return words


def split_balanced(ph, max_chars):
    """Split a phrase into the fewest one-line cues, balanced in length (DP over word breaks)."""
    toks = [x[0] for x in ph]
    n = len(toks)
    length = lambda i, j: len(" ".join(toks[i:j]))
    if length(0, n) <= max_chars:
        return [ph]
    k = -(-length(0, n) // max_chars)
    while True:
        target = length(0, n) / k
        best = {0: (0.0, [])}
        for j in range(1, n + 1):
            cands = []
            for i in range(j):
                if i not in best or length(i, j) > max_chars:
                    continue
                cost = (length(i, j) - target) ** 2
                last = re.sub(r"\W", "", toks[j - 1].lower())
                if j < n and last in SMALL:
                    cost += 400
                if j < n and toks[j - 1].endswith(","):
                    cost -= 250
                if j - i == 1 and n > 1:
                    cost += 300
                cands.append((best[i][0] + cost, best[i][1] + [j]))
            if cands:
                best[j] = min(cands)
        if n in best and len(best[n][1]) <= k + 1:
            cuts = [0] + best[n][1]
            return [ph[cuts[q]:cuts[q + 1]] for q in range(len(cuts) - 1)]
        k += 1


def translated_words(em, items):
    """English sentences (timed to the source sentence) -> pseudo-words timed by character offset."""
    tr = json.load(open(PROJ / em["subs_en"], encoding="utf-8"))
    mapped = []
    for it in items:
        for s0, e0, en in tr.get(it["src"], []):
            mid = (s0 + e0) / 2
            if not (it["a_in"] - 0.05 <= mid <= it["a_out"] + 0.05):
                continue
            st = it["a_at"] + max(s0, it["a_in"]) - it["a_in"]
            et = it["a_at"] + min(e0, it["a_out"]) - it["a_in"]
            toks = en.split()
            total_c = sum(len(t) + 1 for t in toks)
            c = 0
            for k, t in enumerate(toks):
                a = st + (et - st) * c / total_c
                c += len(t) + 1
                b = st + (et - st) * c / total_c
                # sentence end -> force a phrase break via punctuation; mark sentence id in slot 3
                mapped.append([t, a, b, (it["i"], s0)])
    return mapped


def build_subs(em, items, work, total, max_chars=32):
    if em.get("subs_en"):
        mapped = translated_words(em, items)
        merged = split_mapped(mapped, max_chars)
        boxes = sub_boxes(em, items, merged, total) if em.get("sub_box") else []
        return write_subs(merged, work, total, boxes)
    words_db = {k: json.load(open(PROJ / f"assets/analysis/transcript_{k}.json", encoding="utf-8"))["words"]
                for k in em["sources"]}
    edits = em.get("sub_edits", {})
    mapped = []
    for it in items:
        ws = [dict(w, word=w["word"].strip()) for w in words_db[it["src"]]
              if it["a_in"] - 0.02 <= (w["start"] + w["end"]) / 2 <= it["a_out"] - 0.06]
        ws = apply_edits(ws, edits.get(it["src"], []))
        for w in ws:
            st = it["a_at"] + max(w["start"], it["a_in"]) - it["a_in"]
            en = it["a_at"] + min(w["end"], it["a_out"]) - it["a_in"]
            mapped.append([w["word"], st, max(en, st + 0.12), it["i"]])
    return write_subs(split_mapped(mapped, max_chars), work, total)


def split_mapped(mapped, max_chars):
    # phrases end at sentence ends, pauses and segment changes; long phrases are split into
    # balanced one-line cues (<= max_chars), preferring commas and never ending on "the / to / and…"
    phrases, cur = [], []
    for i, w in enumerate(mapped):
        nxt = mapped[i + 1] if i + 1 < len(mapped) else None
        cur.append(w)
        if nxt is None or nxt[3] != w[3] or nxt[1] - w[2] > 0.6 or re.search(r"[.!?:]$", w[0]):
            phrases.append(cur)
            cur = []
    merged = []
    for ph in phrases:
        merged += split_balanced(ph, max_chars)
    return merged


def cue_times(merged, total):
    out = []
    for i, c in enumerate(merged):
        st = c[0][1]
        en = max(c[-1][2] + 0.25, st + 0.9)
        if i + 1 < len(merged):
            en = min(en, merged[i + 1][0][1] - 0.04)
        out.append((st, min(en, total), re.sub(r"\s+", " ", " ".join(x[0] for x in c)).strip()))
    return out


def burned_scan(em, items):
    """Burned-in subtitle extents per timeline item (cached): [(out_t, x0, x1)]."""
    import scan_burned
    cache_f = PROJ / "artifacts/burned_scan.json"
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    out = []
    for it in items:
        key = f"{it['src']}@{it['v_in']}+{it['n']}"
        if key not in cache:
            cache[key] = scan_burned.scan(em["sources"][it["src"]], it["v_in"], it["n"] / FPS)
            cache_f.write_text(json.dumps(cache))
        out += [(it["t0"] + t - it["v_in"], a, b) for t, a, b in cache[key]]
    return out


def sub_boxes(em, items, merged, total, step=0.2, char_w=54):
    """Black boxes behind our subtitles that also hide the sources' burned-in subtitles."""
    cfg = em["sub_box"]
    pad = cfg.get("pad", 70)
    scan = burned_scan(em, items)
    cues = cue_times(merged, total)
    n = int(total / step) + 1
    x0 = np.full(n, np.inf)
    x1 = np.full(n, -np.inf)
    cue_id = np.full(n, -1)
    for t, a, b in scan:
        if a is None:
            continue
        # burned text can sit a frame or two longer than the 5 fps scan sees -> widen by one step
        for k in range(max(0, int(t / step) - 1), min(n, int(t / step) + 2)):
            x0[k] = min(x0[k], a)
            x1[k] = max(x1[k], b)
    for ci, (st, en, text) in enumerate(cues):
        w = len(text) * char_w
        for k in range(int(st / step), min(n, int(np.ceil(en / step)))):
            x0[k] = min(x0[k], 1920 - w / 2)
            x1[k] = max(x1[k], 1920 + w / 2)
            cue_id[k] = ci
    boxes, k = [], 0
    while k < n:
        if not np.isfinite(x0[k]):
            k += 1
            continue
        j = k
        while j + 1 < n and np.isfinite(x0[j + 1]) and cue_id[j + 1] == cue_id[k]:
            j += 1
        a = max(0, int(x0[k:j + 1].min()) - pad)
        b = min(3840, int(x1[k:j + 1].max()) + pad)
        boxes.append((k * step, min(total, (j + 1) * step), a, b))
        k = j + 1
    # merge neighbours with a tiny gap so the box does not flicker between cues
    merged_b = []
    for bx in boxes:
        if merged_b and bx[0] - merged_b[-1][1] < 0.45:
            p0 = merged_b[-1]
            if abs(bx[2] - p0[2]) < 40 and abs(bx[3] - p0[3]) < 40:
                merged_b[-1] = (p0[0], bx[1], min(p0[2], bx[2]), max(p0[3], bx[3]))
                continue
            merged_b[-1] = (p0[0], bx[0], p0[2], p0[3])   # close the gap: no blink to the old text
        merged_b.append(bx)
    y0, y1 = cfg["y0"], cfg["y1"]
    ev = []
    for st, en, a, b in merged_b:
        ev.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Sub,,0,0,0,,"
                  f"{{\\an7\\pos({a},{y0})\\bord0\\shad0\\1c&H000000&\\1a&H00&\\p1}}"
                  f"m 0 0 l {b - a} 0 {b - a} {y1 - y0} 0 {y1 - y0}{{\\p0}}")
    (PROJ / "artifacts/sub_boxes.json").write_text(json.dumps(merged_b))
    return ev


def write_subs(merged, work, total, boxes=()):
    lines, plain = [], []
    for i, c in enumerate(merged):
        text = re.sub(r"\s+", " ", " ".join(x[0] for x in c)).strip()
        st = c[0][1]
        en = max(c[-1][2] + 0.25, st + 0.9)
        if i + 1 < len(merged):
            en = min(en, merged[i + 1][0][1] - 0.04)
        lines.append(f"Dialogue: 1,{ass_time(st)},{ass_time(min(en, total))},Sub,,0,0,0,,{text.upper()}")
        plain.append(f"{st:7.2f} [{len(text):2d}] {text}")
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 3840
PlayResY: 2160
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Segoe UI Semibold,84,&H00FFFFFF,&H00FFFFFF,&H50000000,&H7A000000,0,0,0,0,100,100,1.5,0,1,4.5,2.5,2,300,300,55,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dst = work / "subs.ass"
    dst.write_text(head + "\n".join(list(boxes) + lines) + "\n", encoding="utf-8")
    (PROJ / "artifacts/subtitles.txt").write_text("\n".join(plain), encoding="utf-8")
    return dst, plain


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


# ----------------------------------------------------------------- final
def render_final(groups, mix, total, dst, h, fast, overlays=(), subs=None):
    inp = sum((["-i", g["file"]] for g in groups), [])
    for o in overlays:
        inp += ["-c:v", "libvpx-vp9", "-i", o["file"]]
    inp += ["-i", mix]
    n = len(groups)
    fc, last = [], "[0:v]"
    blur = max(3, round(19 * h / 1440))
    for i in range(1, len(groups)):
        off = groups[i]["t0"]
        fc.append(f"{last}[{i}:v]xfade=transition=smoothleft:duration={XF}:offset={off:.4f}[x{i}]")
        fc.append(f"[x{i}]dblur=angle=0:radius={blur}:enable='between(t,{off + 0.08:.3f},{off + XF - 0.08:.3f})'[b{i}]")
        last = f"[b{i}]"
    for k, o in enumerate(overlays):
        fc.append(f"[{n + k}:v]setpts=PTS-STARTPTS+{o['start']:.3f}/TB[o{k}]")
        fc.append(f"{last}[o{k}]overlay=0:0:eof_action=pass[v{k}]")
        last = f"[v{k}]"
    if subs:
        sp = subs.as_posix().replace(":", "\\:")
        fc.append(f"{last}subtitles=filename='{sp}'[vs]")
        last = "[vs]"
    fc.append(f"{last}format=yuv420p[vout]")
    common = ["-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
              "-color_range", "tv", "-c:a", "aac", "-b:a", "160k" if fast else "320k", "-ar", SR,
              "-movflags", "+faststart", dst]
    head = [*inp, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n + len(overlays)}:a",
            "-t", f"{total:.3f}", "-r", FPS, "-fps_mode", "cfr"]
    x264 = ["-c:v", "libx264", "-preset", "veryfast" if fast else "slow", "-crf", "26" if fast else "14",
            "-profile:v", "high"]
    if fast:
        ff(*head, *x264, *common)
        return
    try:   # Intel Quick Sync: same quality as x264 crf 14-16 at ~3.5x the speed (see OFTV playbook)
        ff(*head, "-c:v", "h264_qsv", "-preset", "slow", "-global_quality", "16", "-profile:v", "high", *common)
    except subprocess.CalledProcessError:
        ff(*head, *x264, *common)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=480, choices=[480, 1440])
    ap.add_argument("--plan-only", action="store_true")
    a = ap.parse_args()
    h = a.res
    w = 854 if h == 480 else 2560
    fast = h == 480
    em = json.load(open(PROJ / "artifacts/edit_map.json", encoding="utf-8"))
    items, total = plan(em)
    (PROJ / "artifacts/timeline.json").write_text(json.dumps({"total": round(total, 3), "items": items}, indent=1,
                                                             ensure_ascii=False), encoding="utf-8")
    print(f"total {total:.2f} s, {len(items)} segments, {sum(i['switch_before'] for i in items)} A/B switches")
    if a.plan_only:
        return
    work = PROJ / f"work_{h}"
    work.mkdir(exist_ok=True)
    awork = PROJ / "work_audio"
    awork.mkdir(exist_ok=True)
    groups = render_items(em, items, work, w, h, fast)
    whooshes = [g["t0"] + XF / 2 - 0.45 for g in groups[1:]]
    overlays = render_overlays(em, items, work, h)
    speech, sp_report = build_speech(em, items, awork, total)
    music, mdur = build_music(em, awork, total)
    mix = build_mix(speech, music, awork, total, whooshes, [o["start"] + 0.03 for o in overlays])
    subs, cues = build_subs(em, items, work, total)
    dst = PROJ / "renders" / ("preview_480p.mp4" if fast else "final_2k.mp4")
    render_final(groups, mix, total, dst, h, fast, overlays, subs)
    rep = {"output": str(dst), "duration": round(total, 2), "music_chain_s": mdur, "speech": sp_report}
    (PROJ / f"artifacts/render_report_{h}.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("output", "duration", "music_chain_s")}))


if __name__ == "__main__":
    main()
