"""Render the Miya Moore OFTV edit from artifacts/edit_plan.json.

Steps (all intermediates kept under projects/miya-moore-oftv/work/):
  1. segments  : each kept range -> high-quality 4K intermediate (+8 ms audio fades)
  2. groups    : intro / main / outro concatenated losslessly
  3. overlays  : tag + section plates rendered by Remotion (VP9 + alpha)
  4. audio     : speech (denoise, -14 LUFS, -6 dB) + music (-14 LUFS, -16 dB)
                 + whooshes (-14 LUFS, -11 dB)  ->  mix.wav
  5. subtitles : ASS built from the word-level transcript
  6. final     : whip transitions, overlays, burned subtitles, H.264/AAC MP4

Usage: python render_edit.py [--test SECONDS] [--duck]
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
ROOT = PROJ.parents[1]
WORK = PROJ / "work"
FPS = 30
XF = 0.5                     # whip transition length (s)
ZOOM = 1.08                  # punch-in factor on visible jump cuts
OUT_W, OUT_H = 2560, 1440    # 2K delivery
SECTION_DUR = 4.8            # plate fully readable ~4 s (+ in/out animation)
POP_LEAD = 0.03              # pop lands as the plate starts moving
JUMP_BODY = 9.0              # body-region diff above which a cut gets a punch-in
MUSIC = [
    r"C:\Users\fosfe\Downloads\ОФТВБЛЯЯТЬ\Музыка\Sound Of Freedom - Lo-Fi R&B Vibe.mp3.mp3",
    r"C:\Users\fosfe\Downloads\ОФТВБЛЯЯТЬ\Музыка\Sound Of Freedom - Chil Hip-Hop Beat .mp3.mp3",
]
SUB_FIXES = {  # transcription slips -> what she says / means (subtitles only)
    "Nyambor": "Miya Moore", "Miyamu": "Miya Moore", "activators": "activities",
    "enjoyed the process": "enjoy the process",
    "Bye -bye": "Bye-bye", "self -expression": "self-expression", "\ufffd": "—",
}
# Word-level subtitle edits keyed by the word's source start time:
# None drops a stutter / repeated word, a string replaces the word.
WORD_EDITS = {
    42.68: None, 141.68: None, 341.40: None, 287.60: None, 258.78: None,
    75.82: "something.", 76.5: "So", 82.16: "me.", 85.2: "reasons", 87.32: "because it",
    89.54: "down.", 89.98: "Life", 249.72: "rewarding.", 280.14: "So,", 288.24: "it", 258.36: "it.", 137.86: "creativity.",
    325.8: "sketchbook.", 336.4: "hobbies.", 342.74: "projects,", 340.56: "lifestyle,", 341.84: "creative",
}


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:220])
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def ff(*args):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def loudness(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True, errors="replace").stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1])


def nframes(seg):
    return round((seg["src_out"] - seg["src_in"]) * FPS)


# ---------------------------------------------------------------- 1. segments
def render_segments(plan, segs, src):
    jumps = {round(j[2], 3): j[5] for j in json.load(open(PROJ / "assets/analysis/cut_jumps.json"))}
    zoomed = False
    out = []
    for i, s in enumerate(segs):
        if i and segs[i - 1]["group"] == s["group"] and jumps.get(round(s["src_in"], 3), 0) > JUMP_BODY:
            zoomed = not zoomed
        elif i and segs[i - 1]["group"] != s["group"]:
            zoomed = False
        s["zoom"] = zoomed
        dst = WORK / f"seg_{i:02d}.mkv"
        n = nframes(s)
        dur = n / FPS
        vf = "fps=30"
        if zoomed:
            # Punch-in is cropped from the 4K source, so at 1440p it stays fully sharp.
            vf += f",crop=trunc(iw/{ZOOM}/2)*2:trunc(ih/{ZOOM}/2)*2:(iw-ow)/2:(ih-oh)*0.30"
        vf += f",scale={OUT_W}:{OUT_H}:flags=lanczos,setsar=1,format=yuv420p"
        if not dst.exists():
            ff("-ss", f"{s['src_in']:.4f}", "-i", src, "-t", f"{dur:.4f}",
               "-vf", vf, "-frames:v", n,
               "-af", f"afade=t=in:d=0.008,afade=t=out:st={dur - 0.008:.4f}:d=0.008,apad,atrim=0:{dur:.4f}",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-g", "30",
               "-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2", dst)
        out.append(dst)
    return out


# ---------------------------------------------------------------- 2. groups
def render_groups(segs, files):
    groups = []
    for g in dict.fromkeys(s["group"] for s in segs):
        lst = WORK / f"group_{g}.txt"
        lst.write_text("".join(f"file '{f.as_posix()}'\n" for f, s in zip(files, segs) if s["group"] == g))
        dst = WORK / f"group_{g}.mkv"
        ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst)
        frames = sum(nframes(s) for s in segs if s["group"] == g)
        groups.append({"name": g, "file": dst, "dur": frames / FPS})
    return groups


# ---------------------------------------------------------------- 3. overlays
def render_overlays(plan, offsets):
    rc = ROOT / "remotion-composer"
    jobs = [("tag", "TagPlate", {"tag": plan["tag"]["text"]}, plan["tag"]["start"], plan["tag"]["duration"])]
    for s in plan["sections"]:
        jobs.append((f"sec{s['index']}", "SectionPlate", {"index": s["index"], "title": s["title"]},
                     shift(s["out_t"], s["src_t"], plan, offsets), SECTION_DUR))
    out = []
    for name, comp, props, start, dur in jobs:
        dst = WORK / f"ov_{name}.webm"
        pfile = WORK / f"ov_{name}.json"
        pfile.write_text(json.dumps(props))
        if not dst.exists():
            run(["npx.cmd", "remotion", "render", "src/oftv/index.tsx", comp, dst, f"--props={pfile}",
                 "--codec=vp9", "--pixel-format=yuva420p", "--image-format=png", f"--scale={OUT_W / 3840}",
                 "--log=error"], cwd=rc)
        out.append({"file": dst, "start": start, "dur": dur})
    return out


def group_offset(group, plan):
    return plan["groups"].index(group) * XF


def shift(out_t, src_t, plan, offsets):
    """Plan out_t is before transitions; each whip overlaps XF seconds."""
    seg = next(s for s in plan["segments"] if s["src_in"] - 0.5 <= src_t <= s["src_out"])
    return out_t - group_offset(seg["group"], plan)


# ---------------------------------------------------------------- 4. audio
def build_audio(groups, total, duck):
    speech = WORK / "speech_raw.wav"
    # Whip overlaps happen inside pauses, so a short crossfade of the speech is safe.
    inp, fc, last = [], [], "[0:a]"
    for i, g in enumerate(groups):
        inp += ["-i", g["file"]]
    for i in range(1, len(groups)):
        fc.append(f"{last}[{i}:a]acrossfade=d={XF}:c1=tri:c2=tri[x{i}]")
        last = f"[x{i}]"
    ff(*inp, "-filter_complex", ";".join(fc) or "[0:a]anull[x0]", "-map", last if fc else "[x0]",
       "-ac", "1", "-c:a", "pcm_s24le", speech)

    clean = WORK / "speech_clean.wav"
    # Light, voice-safe cleanup: rumble cut + gentle spectral NR, then even out level.
    ff("-i", speech, "-af", "highpass=f=80,afftdn=nr=12:nf=-56:tn=1,"
       "acompressor=threshold=-30dB:ratio=2.5:attack=15:release=250:makeup=1,"
       "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "-c:a", "pcm_s24le", clean)
    speech_lufs = loudness(clean)

    music_parts = []
    for i, m in enumerate(MUSIC):
        dst = WORK / f"music_{i}.wav"
        ff("-i", m, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", dst)
        music_parts.append(dst)
    whoosh = WORK / "whoosh_norm.wav"
    w_l = loudness(PROJ / "assets/sfx/whoosh.wav")
    ff("-i", PROJ / "assets/sfx/whoosh.wav", "-af", f"volume={-14 - w_l:.2f}dB", "-ar", "48000", whoosh)
    # A single pop is too short for integrated loudness, so measure a looped train.
    train = WORK / "pop_train.wav"
    ff("-stream_loop", "6", "-i", PROJ / "assets/sfx/pop.wav", train)
    pop = WORK / "pop_norm.wav"
    ff("-i", PROJ / "assets/sfx/pop.wav", "-af", f"volume={-14 - loudness(train):.2f}dB", "-ar", "48000", pop)

    return clean, speech_lufs, music_parts, whoosh, pop


def mix_audio(clean, music_parts, whoosh, pop, overlays, groups, total, music_switch, duck, test):
    mix = WORK / ("mix_duck.wav" if duck else "mix.wav")
    xf_music = 6.0
    a_len = music_switch + xf_music / 2
    fc = [
        f"[0:a]volume=-6dB,aformat=channel_layouts=stereo[sp]",
        f"[1:a]atrim=0:{a_len:.3f},afade=t=in:d=2.5[ma]",
        f"[2:a]afade=t=in:d=0.1[mb0]",
        f"[ma][mb0]acrossfade=d={xf_music}:c1=qsin:c2=qsin,atrim=0:{total:.3f},"
        f"afade=t=out:st={total - 5:.3f}:d=5,volume=-16dB[mus]",
    ]
    whooshes, t = [], 0.0
    for g in groups[:-1]:
        t += g["dur"] - XF
        whooshes.append(t + XF / 2 - 0.45)
        t += 0  # next group starts at t (overlap already subtracted)
    wl = []
    for i, wt in enumerate(whooshes):
        if wt < total:
            fc.append(f"[3:a]volume=-11dB,adelay={int(wt * 1000)}|{int(wt * 1000)},apad[w{i}]")
            wl.append(f"[w{i}]")
    pops = [o["start"] + POP_LEAD for o in overlays if o["start"] < total]
    fc.append(f"[4:a]volume=-11dB,asplit={len(pops)}" + "".join(f"[pp{i}]" for i in range(len(pops))))
    for i, pt in enumerate(pops):
        ms = int(pt * 1000)
        fc.append(f"[pp{i}]adelay={ms}|{ms},apad[p{i}]")
        wl.append(f"[p{i}]")
    if duck:
        fc.append("[sp]asplit=2[sp1][sc]")
        fc.append("[mus][sc]sidechaincompress=threshold=0.03:ratio=3:attack=80:release=600[musd]")
        sp, mus = "[sp1]", "[musd]"
    else:
        sp, mus = "[sp]", "[mus]"
    fc.append(f"{sp}{mus}{''.join(wl)}amix=inputs={2 + len(wl)}:normalize=0:duration=first,"
              f"alimiter=limit=0.89:level=false[out]")
    ff("-i", clean, "-i", music_parts[0], "-i", music_parts[1], "-i", whoosh, "-i", pop,
       "-filter_complex", ";".join(fc), "-map", "[out]", "-t", f"{total:.3f}",
       "-ar", "48000", "-c:a", "pcm_s24le", mix)
    return mix, whooshes


# ---------------------------------------------------------------- 5. subtitles
def ass_time(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def build_subs(plan, total):
    words = json.load(open(PROJ / "assets/analysis/transcript_novad.json", encoding="utf-8"))["words"]
    mapped = []
    for w in words:
        key = round(w["start"], 2)
        if key in WORD_EDITS:
            if WORD_EDITS[key] is None:
                continue
            w = dict(w, word=WORD_EDITS[key])
        if w["end"] - w["start"] < 0.05:  # zero-length words from the aligner
            w = dict(w, end=w["start"] + 0.15)
        # Whisper word edges drift ±0.3 s, so attach each word to the kept
        # segment it overlaps most instead of trusting its midpoint.
        ov = [(min(w["end"], s["src_out"]) - max(w["start"], s["src_in"]), s) for s in plan["segments"]]
        best, seg = max(ov, key=lambda x: x[0])
        if best <= 0.02:
            continue
        off = seg["out_in"] - seg["src_in"] - group_offset(seg["group"], plan)
        st = max(w["start"], seg["src_in"]) + off
        en = min(w["end"], seg["src_out"]) + off
        mapped.append([w["word"].strip(), st, en])
    cues, cur = [], []
    for i, w in enumerate(mapped):
        cur.append(w)
        text = " ".join(x[0] for x in cur)
        nxt_gap = mapped[i + 1][1] - w[2] if i + 1 < len(mapped) else 9
        if (re.search(r"[.!?]$", w[0]) or len(text) > 38 or nxt_gap > 0.6
                or (re.search(r",$", w[0]) and len(text) > 22)):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    lines = []
    for i, c in enumerate(cues):
        text = " ".join(x[0] for x in c)
        for k, v in SUB_FIXES.items():
            text = text.replace(k, v)
        text = re.sub(r"\s+", " ", text).strip()
        if not text or text in {"—", "."}:
            continue
        prev = lines[-1].rsplit(",,", 1)[-1] if lines else "."
        if text[0].islower() and re.search(r"[.!?]$", prev):
            text = text[0].upper() + text[1:]
        elif text[0].isupper() and not re.search(r"[.!?]$", prev) and not re.match(r"(I\b|I'|OnlyFans|OFTV|Miya)", text):
            text = text[0].lower() + text[1:]
        st = c[0][1]
        en = max(c[-1][2] + 0.25, st + 1.0)
        if i + 1 < len(cues):
            en = min(en, cues[i + 1][0][1] - 0.04)
        if st >= total:
            break
        lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(min(en, total))},Sub,,0,0,0,,{text.upper()}")
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 3840
PlayResY: 2160
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Segoe UI Semibold,84,&H00FFFFFF,&H00FFFFFF,&H50000000,&H7A000000,0,0,0,0,100,100,1.5,0,1,4.5,2.5,2,300,300,55,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dst = WORK / "subtitles.ass"
    dst.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
    srt = PROJ / "assets" / "subtitles.srt"
    srt.write_text("".join(
        f"{n + 1}\n{l.split(',')[1].replace('.', ',')}0 --> {l.split(',')[2].replace('.', ',')}0\n{l.split(',,', 2)[-1].split(',,')[-1]}\n\n"
        for n, l in enumerate(lines)), encoding="utf-8")
    return dst


# ---------------------------------------------------------------- 6. final
def render_final(groups, overlays, subs, mix, total, dst, test):
    inp = []
    for g in groups:
        inp += ["-i", g["file"]]
    for o in overlays:
        inp += ["-c:v", "libvpx-vp9", "-i", o["file"]]
    inp += ["-i", mix]
    n_g = len(groups)
    fc, last, t = [], "[0:v]", 0.0
    for i in range(1, n_g):
        t += groups[i - 1]["dur"] - XF
        # classic smooth slide + horizontal motion blur = whip ("вжух")
        fc.append(f"{last}[{i}:v]xfade=transition=smoothleft:duration={XF}:offset={t:.4f}[x{i}]")
        fc.append(f"[x{i}]dblur=angle=0:radius=19:enable='between(t,{t + 0.08:.3f},{t + XF - 0.08:.3f})'[b{i}]")
        last = f"[b{i}]"
    for k, o in enumerate(overlays):
        if o["start"] >= total:
            continue
        idx = n_g + k
        fc.append(f"[{idx}:v]setpts=PTS-STARTPTS+{o['start']:.3f}/TB[o{k}]")
        fc.append(f"{last}[o{k}]overlay=0:0:eof_action=pass[v{k}]")
        last = f"[v{k}]"
    subs_path = subs.as_posix().replace(":", "\\:")
    fc.append(f"{last}subtitles=filename='{subs_path}',format=yuv420p[vout]")
    ff(*inp, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n_g + len(overlays)}:a",
       "-t", f"{total:.3f}", "-r", "30",
       "-c:v", "libx264", "-preset", "fast" if test else "slow", "-crf", "16",
       "-profile:v", "high", "-level:v", "5.0", "-pix_fmt", "yuv420p",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-x264-params", "keyint=60:min-keyint=30",
       "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
       "-movflags", "+faststart", dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", type=float, default=0.0, help="render only the first N output seconds")
    ap.add_argument("--duck", action="store_true", help="also duck music under speech")
    a = ap.parse_args()
    WORK.mkdir(exist_ok=True)
    plan = json.load(open(PROJ / "artifacts/edit_plan.json", encoding="utf-8"))
    segs = plan["segments"]
    if a.test:
        segs = [s for s in segs if s["out_in"] - group_offset(s["group"], plan) < a.test]
    files = render_segments(plan, segs, plan["source"])
    groups = render_groups(segs, files)
    total = sum(g["dur"] for g in groups) - XF * (len(groups) - 1)
    if a.test:
        total = min(total, a.test)
    overlays = render_overlays(plan, None)
    clean, sp_lufs, music, whoosh, pop = build_audio(groups, total, a.duck)
    sec3 = next(s for s in plan["sections"] if s["index"] == 3)
    switch = shift(sec3["out_t"], sec3["src_t"], plan, None)
    mix, whooshes = mix_audio(clean, music, whoosh, pop, overlays, groups, total, switch, a.duck, a.test)
    subs = build_subs(plan, total)
    (PROJ / "renders").mkdir(exist_ok=True)
    name = ("test_" if a.test else "final_") + ("duck" if a.duck else "static") + ".mp4"
    dst = PROJ / "renders" / name
    render_final(groups, overlays, subs, mix, total, dst, a.test)
    report = {"output": str(dst), "duration": round(total, 3), "speech_lufs_before_gain": sp_lufs,
              "whooshes_at": [round(w, 2) for w in whooshes], "music_switch_at": round(switch, 2),
              "zoomed_segments": [i for i, s in enumerate(segs) if s.get("zoom")],
              "sections_out": [(s["title"], round(shift(s["out_t"], s["src_t"], plan, None), 2)) for s in plan["sections"]]}
    if not a.test:
        def ts(t):
            return f"{int(t // 60)}:{int(t % 60):02d}"
        chap = ["0:00 Intro"] + [f"{ts(shift(s['out_t'], s['src_t'], plan, None))} {s['title']}" for s in plan["sections"]]
        (PROJ / "renders" / "chapters.txt").write_text("\n".join(chap) + "\n", encoding="utf-8")
        report["chapters"] = chap
    (PROJ / "artifacts" / ("render_report_test.json" if a.test else "render_report.json")).write_text(
        json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()



