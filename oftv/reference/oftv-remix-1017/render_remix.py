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
        v_in = max(0.0, a_in - (LEAD if sw_before else 0.0))
        v_out = a_out + (LEAD if sw_after else 0.0) + s.get("v_tail", 0.0)
        n = round((v_out - v_in) * FPS)
        items.append({"i": i, "src": s["src"], "sec": s["sec"], "a_in": a_in, "a_out": a_out, "v_in": round(v_in, 3),
                      "n": n, "switch_before": sw_before, "edge_floor_db": [f_in, f_out], "text": s["text"]})
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
    files = []
    for it in items:
        dst = work / f"v_{it['i']:02d}.mkv"
        if not dst.exists():
            ff("-ss", f"{it['v_in']:.4f}", "-i", em["sources"][it["src"]], "-t", f"{it['n'] / FPS + 0.3:.4f}",
               "-vf", f"fps={FPS},scale={w}:{h}:flags=lanczos,setsar=1,format=yuv420p",
               "-frames:v", it["n"], "-an",
               "-c:v", "libx264", "-preset", "ultrafast" if fast else "medium", "-crf", "18" if fast else "10",
               "-g", "30", dst)
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
    i0, _ = ebur(comp)
    ff("-i", comp, "-af", f"volume={-14 - i0:.2f}dB,alimiter=limit=0.84:level=false:attack=3:release=60",
       "-c:a", "pcm_f32le", speech)
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


def build_mix(speech, music, work, total, whooshes, pops=()):
    w = work / "whoosh.wav"
    i0, _ = ebur(WHOOSH)
    ff("-i", WHOOSH, "-af", f"volume={-14 - i0:.2f}dB", "-ar", SR, "-ac", 2, "-c:a", "pcm_f32le", w)
    # a single pop is too short for EBU gating -> measure a looped train of it
    train = work / "pop_train.wav"
    ff("-stream_loop", "6", "-i", POP, train)
    pop = work / "pop.wav"
    ff("-i", POP, "-af", f"volume={-14 - ebur(train)[0]:.2f}dB", "-ar", SR, "-ac", 2, "-c:a", "pcm_f32le", pop)
    fc = ["[0:a]volume=-6dB,aformat=channel_layouts=stereo,asplit=2[sp][key]",
          f"[1:a]atrim=0:{total:.3f},afade=t=in:d=2.5,afade=t=out:st={total - 5:.3f}:d=5,volume=-16dB[mu0]",
          # light ducking: ~3 dB under speech, slow release so the bed does not pump
          "[mu0][key]sidechaincompress=threshold=0.02:ratio=2:attack=80:release=900:makeup=1[mu]"]
    extra = []
    fc.append(f"[2:a]volume=-11dB,asplit={len(whooshes)}" + "".join(f"[wh{i}]" for i in range(len(whooshes))))
    for i, t in enumerate(whooshes):
        ms = int(max(0, t) * 1000)
        fc.append(f"[wh{i}]adelay={ms}:all=1,apad[w{i}]")
        extra.append(f"[w{i}]")
    if pops:
        fc.append(f"[3:a]volume=-11dB,asplit={len(pops)}" + "".join(f"[pp{i}]" for i in range(len(pops))))
        for i, t in enumerate(pops):
            ms = int(t * 1000)
            fc.append(f"[pp{i}]adelay={ms}:all=1,apad[p{i}]")
            extra.append(f"[p{i}]")
    fc.append(f"[sp][mu]{''.join(extra)}amix=inputs={2 + len(extra)}:normalize=0:duration=first,"
              "alimiter=limit=0.89:level=false[out]")
    mix = work / "mix.wav"
    ff("-i", speech, "-i", music, "-i", w, "-i", pop, "-filter_complex", ";".join(fc), "-map", "[out]",
       "-t", f"{total:.3f}", "-ar", SR, "-c:a", "pcm_s24le", mix)
    # stems for the report
    ff("-i", music, "-af", f"atrim=0:{total:.3f},volume=-16dB", "-c:a", "pcm_f32le", work / "music_stem.wav")
    return mix


# ----------------------------------------------------------------- overlays + subtitles
def render_overlays(em, items, work, h):
    """Tag plate (Remotion TagPlate, VP9 alpha) at each time listed in edit_map['tag']['at']."""
    tag = em.get("tag")
    if not tag:
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


def build_subs(em, items, work, total, max_chars=32):
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
    lines, plain = [], []
    for i, c in enumerate(merged):
        text = re.sub(r"\s+", " ", " ".join(x[0] for x in c)).strip()
        st = c[0][1]
        en = max(c[-1][2] + 0.25, st + 0.9)
        if i + 1 < len(merged):
            en = min(en, merged[i + 1][0][1] - 0.04)
        lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(min(en, total))},Sub,,0,0,0,,{text.upper()}")
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
    dst.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
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
    ff(*inp, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n + len(overlays)}:a",
       "-t", f"{total:.3f}", "-r", FPS, "-fps_mode", "cfr", "-c:v", "libx264",
       "-preset", "veryfast" if fast else "slow", "-crf", "26" if fast else "14", "-profile:v", "high",
       "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-c:a", "aac", "-b:a", "160k" if fast else "320k", "-ar", SR, "-movflags", "+faststart", dst)


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
