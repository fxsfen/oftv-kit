"""Multi-source OFTV edit renderer (talking intro/outro + b-roll with voice-over).

Reads artifacts/timeline.json and renders:
  video items  -> per-item intermediates at the target height, concatenated per group
  groups       -> joined with whip transitions (xfade smoothleft + motion blur)
  audio        -> on-camera speech (from talking items) + voice-over clips placed
                  at fixed output times; b-roll audio is never used.
                  Mix recipe: every source normalised to -14 LUFS, then
                  dialogue/VO -6 dB, music -16 dB, whoosh/pop -11 dB.
  overlays     -> tag + section plates (Remotion, VP9 alpha), pop on each plate
  subtitles    -> uppercase ASS from word timestamps of speech + VO

Usage: python render_timeline.py --res 480|1440
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
ROOT = PROJ.parents[1]
SHARED_SFX = ROOT / "projects/miya-moore-oftv/assets/sfx"
FPS = 30
XF = 0.5
SECTION_DUR = 4.8
TAG_DUR = 5.5


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:200], flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def ff(*args):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def nframes(it):
    # pad_tail = frozen last frame, so a whip can start after the last word
    return round((it["out"] - it["in"] + it.get("pad_tail", 0.0)) * FPS)


def layout(tl):
    """Assign output start times; groups overlap by XF at whip transitions."""
    t, prev_group = 0.0, None
    for it in tl["video"]:
        if prev_group is not None and it["group"] != prev_group:
            t -= XF
        it["t0"] = round(t, 4)
        t += nframes(it) / FPS
        prev_group = it["group"]
    # VO clips and section plates are anchored to a video item (+ offset) so a
    # trim upstream never desyncs them.
    for x in tl["vo"] + tl["sections"] + tl.get("tag_repeats", []):
        if "item" in x:
            x["at"] = round(tl["video"][x["item"]]["t0"] + x.get("offset", 0.0), 3)
    return t


def render_items(tl, work, w, h, fast):
    files = []
    for i, it in enumerate(tl["video"]):
        dst = work / f"v_{i:02d}.mkv"
        n = nframes(it)
        vf = "fps=30"
        if it.get("zoom"):
            z = it["zoom"]
            vf += f",crop=trunc(iw/{z}/2)*2:trunc(ih/{z}/2)*2:(iw-ow)/2:(ih-oh)*0.35"
        # iPhone clips mix full-range (yuvj420p) and limited-range video; a range change
        # mid-stream breaks the final filter graph, so normalise everything to tv range.
        vf += f",scale={w}:{h}:flags=lanczos:out_range=tv,setsar=1,format=yuv420p"
        if it.get("pad_tail"):
            vf += f",tpad=stop_mode=clone:stop_duration={it['pad_tail']}"
        if not dst.exists():
            ff("-ss", f"{it['in']:.4f}", "-t", f"{it['out'] - it['in'] + 0.1:.4f}", "-i", tl["sources"][it["src"]],
               "-vf", vf, "-frames:v", n, "-an", "-color_range", "tv",
               "-c:v", "libx264", "-preset", "ultrafast" if fast else "veryfast", "-crf", "20" if fast else "12",
               "-g", "30", dst)
        files.append(dst)
    groups = []
    for g in dict.fromkeys(it["group"] for it in tl["video"]):
        lst = work / f"g_{g}.txt"
        lst.write_text("".join(f"file '{f.as_posix()}'\n" for f, it in zip(files, tl["video"]) if it["group"] == g))
        dst = work / f"g_{g}.mkv"
        ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst)
        items = [it for it in tl["video"] if it["group"] == g]
        groups.append({"file": dst, "t0": items[0]["t0"], "dur": sum(nframes(x) for x in items) / FPS})
    return groups


def speech_clips(tl):
    """On-camera speech follows its video item; VO clips sit at explicit output times."""
    clips = []
    for it in tl["video"]:
        if it.get("speech"):
            clips.append({"src": tl["sources"][it["src"]], "in": it["in"], "out": it["out"], "at": it["t0"],
                          "words": it["src"]})
    for vo in tl["vo"]:
        clips.append({"src": tl["sources"][vo["src"]], "in": vo["in"], "out": vo["out"], "at": vo["at"],
                      "words": vo["src"]})
    return clips


def build_audio(tl, work, total, overlays, whooshes):
    clips = speech_clips(tl)
    norm = []
    for k, c in enumerate(clips):
        raw = work / f"sp_{k:02d}.wav"
        d = c["out"] - c["in"]
        ff("-ss", f"{c['in']:.4f}", "-i", c["src"], "-t", f"{d:.4f}", "-vn", "-ac", "1", "-ar", "48000",
           "-af", f"highpass=f=80,afftdn=nr=10:nf=-50:tn=1,afade=t=in:d=0.03,afade=t=out:st={d - 0.05:.4f}:d=0.05",
           raw)
        # Phone voice notes run ~10 dB hotter than the on-camera mic: level every
        # line on its own first so the voice stays even across sources.
        lev = work / f"spn_{k:02d}.wav"
        ff("-i", raw, "-af", f"volume={-16 - loudness(raw):.2f}dB", "-ar", "48000", lev)
        norm.append((lev, c["at"]))
    # One loudness target for all dialogue so on-camera and VO sit at the same level.
    speech = work / "speech_bed.wav"
    inp, fc = [], []
    for k, (f, at) in enumerate(norm):
        inp += ["-i", f]
        ms = int(at * 1000)
        fc.append(f"[{k}:a]adelay={ms}|{ms},apad[s{k}]")
    fc.append("".join(f"[s{k}]" for k in range(len(norm))) + f"amix=inputs={len(norm)}:normalize=0,atrim=0:{total:.3f}[o]")
    ff(*inp, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000", work / "speech_raw.wav")
    ff("-i", work / "speech_raw.wav", "-af",
       "acompressor=threshold=-28dB:ratio=2.5:attack=15:release=250,loudnorm=I=-14:TP=-1.5:LRA=9",
       "-ar", "48000", speech)

    music = work / "music.wav"
    tracks = tl["music"] if isinstance(tl["music"], list) else [tl["music"]]
    parts = []
    for i, m in enumerate(tracks):
        p = work / f"music_{i}.wav"
        ff("-i", m, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", p)
        parts.append(p)
    if len(parts) == 1:
        music = parts[0]
    else:  # chain tracks with a 6 s crossfade
        inp, fc, last = [], [], "[0:a]"
        for i, p in enumerate(parts):
            inp += ["-i", p]
        for i in range(1, len(parts)):
            fc.append(f"{last}[{i}:a]acrossfade=d=6:c1=qsin:c2=qsin[m{i}]")
            last = f"[m{i}]"
        ff(*inp, "-filter_complex", ";".join(fc), "-map", last, "-ar", "48000", music)
    whoosh = work / "whoosh.wav"
    ff("-i", SHARED_SFX / "whoosh.wav", "-af", f"volume={-14 - loudness(SHARED_SFX / 'whoosh.wav'):.2f}dB",
       "-ar", "48000", whoosh)
    train = work / "pop_train.wav"
    ff("-stream_loop", "6", "-i", SHARED_SFX / "pop.wav", train)
    pop = work / "pop.wav"
    ff("-i", SHARED_SFX / "pop.wav", "-af", f"volume={-14 - loudness(train):.2f}dB", "-ar", "48000", pop)

    fc = ["[0:a]volume=-6dB,aformat=channel_layouts=stereo[sp]",
          f"[1:a]atrim=0:{total:.3f},afade=t=in:d=2,afade=t=out:st={total - 4:.3f}:d=4,volume=-16dB[mu]"]
    extra = []
    for i, wt in enumerate(whooshes):
        ms = int(max(0, wt) * 1000)
        fc.append(f"[2:a]volume=-11dB,adelay={ms}|{ms},apad[w{i}]")
        extra.append(f"[w{i}]")
    pops = [o["start"] + 0.03 for o in overlays]
    fc.append(f"[3:a]volume=-11dB,asplit={len(pops)}" + "".join(f"[pp{i}]" for i in range(len(pops))))
    for i, pt in enumerate(pops):
        ms = int(pt * 1000)
        fc.append(f"[pp{i}]adelay={ms}|{ms},apad[p{i}]")
        extra.append(f"[p{i}]")
    fc.append(f"[sp][mu]{''.join(extra)}amix=inputs={2 + len(extra)}:normalize=0:duration=first,"
              "alimiter=limit=0.89:level=false[out]")
    mix = work / "mix.wav"
    ff("-i", speech, "-i", music, "-i", whoosh, "-i", pop, "-filter_complex", ";".join(fc),
       "-map", "[out]", "-t", f"{total:.3f}", "-ar", "48000", "-c:a", "pcm_s24le", mix)
    return mix, clips


def render_overlays(tl, work, h):
    rc = ROOT / "remotion-composer"
    jobs = [("tag", "TagPlate", {"tag": tl["tag"]}, tl.get("tag_at", 0.8))]
    for k, s in enumerate(tl["sections"]):
        jobs.append((f"sec{k + 1}", "SectionPlate",
                     {"index": s["index"], "title": s["title"], "label": s.get("label", "Part")}, s["at"]))
    out = []
    for name, comp, props, start in jobs:
        dst = work / f"ov_{name}_{h}.webm"
        pf = work / f"ov_{name}.json"
        pf.write_text(json.dumps(props))
        if not dst.exists():
            run(["npx.cmd", "remotion", "render", "src/oftv/index.tsx", comp, dst, f"--props={pf}",
                 "--codec=vp9", "--pixel-format=yuva420p", "--image-format=png",
                 f"--scale={h / 2160}", "--log=error"], cwd=rc)
        out.append({"file": dst, "start": start})
    # Same tag plate again (e.g. when she mentions OnlyFans / says goodbye).
    for rep in tl.get("tag_repeats", []):
        out.append({"file": out[0]["file"], "start": rep["at"]})
    return out


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def build_subs(tl, clips, work, total):
    words_db = json.load(open(PROJ / "assets/analysis/transcripts.json", encoding="utf-8"))
    edits = {(k.split("@")[0], round(float(k.split("@")[1]), 2)): v for k, v in tl.get("word_edits", {}).items()}
    mapped = []
    for c in clips:
        for w in words_db[tl["transcript_keys"][c["words"]]]:
            if w["end"] <= c["in"] + 0.02 or w["start"] >= c["out"] - 0.02:
                continue
            key = (c["words"], round(w["start"], 2))
            text = w["word"].strip()
            if key in edits:
                if edits[key] is None:
                    continue
                text = edits[key]
            st = c["at"] + max(w["start"], c["in"]) - c["in"]
            en = c["at"] + min(max(w["end"], w["start"] + 0.15), c["out"]) - c["in"]
            mapped.append([text, st, en])
    mapped.sort(key=lambda x: x[1])
    cues, cur = [], []
    for i, w in enumerate(mapped):
        cur.append(w)
        text = " ".join(x[0] for x in cur)
        gap = mapped[i + 1][1] - w[2] if i + 1 < len(mapped) else 9
        if re.search(r"[.!?]$", w[0]) or len(text) > 36 or gap > 0.6 or (w[0].endswith(",") and len(text) > 22):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    lines = []
    for i, c in enumerate(cues):
        text = re.sub(r"\s+", " ", " ".join(x[0] for x in c)).strip()
        st = c[0][1]
        en = max(c[-1][2] + 0.25, st + 1.0)
        if i + 1 < len(cues):
            en = min(en, cues[i + 1][0][1] - 0.04)
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
    dst = work / "subs.ass"
    dst.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
    return dst, lines


def render_final(groups, overlays, subs, mix, total, dst, h, fast):
    inp = []
    for g in groups:
        inp += ["-i", g["file"]]
    for o in overlays:
        inp += ["-c:v", "libvpx-vp9", "-i", o["file"]]
    inp += ["-i", mix]
    n = len(groups)
    fc, last = [], "[0:v]"
    blur = max(4, round(19 * h / 1440))
    for i in range(1, n):
        off = groups[i]["t0"]
        fc.append(f"{last}[{i}:v]xfade=transition=smoothleft:duration={XF}:offset={off:.4f}[x{i}]")
        fc.append(f"[x{i}]dblur=angle=0:radius={blur}:enable='between(t,{off + 0.08:.3f},{off + XF - 0.08:.3f})'[b{i}]")
        last = f"[b{i}]"
    for k, o in enumerate(overlays):
        fc.append(f"[{n + k}:v]setpts=PTS-STARTPTS+{o['start']:.3f}/TB[o{k}]")
        fc.append(f"{last}[o{k}]overlay=0:0:eof_action=pass[v{k}]")
        last = f"[v{k}]"
    (subs.parent / "final_graph.txt").write_text(";".join(fc), encoding="utf-8")
    sp = subs.as_posix().replace(":", "\\:")
    fc.append(f"{last}subtitles=filename='{sp}',format=yuv420p[vout]")
    ff(*inp, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n + len(overlays)}:a",
       "-t", f"{total:.3f}", "-r", "30", "-c:v", "libx264",
       "-preset", "ultrafast" if fast else "fast", "-crf", "28" if fast else "16",
       "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-c:a", "aac", "-b:a", "160k" if fast else "320k", "-ar", "48000", "-movflags", "+faststart", dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=480, choices=[480, 1440])
    a = ap.parse_args()
    h = a.res
    w = 854 if h == 480 else 2560
    fast = h == 480
    work = PROJ / f"work_{h}"
    work.mkdir(exist_ok=True)
    tl = json.load(open(PROJ / "artifacts/timeline.json", encoding="utf-8"))
    total = layout(tl)
    groups = render_items(tl, work, w, h, fast)
    whooshes = [g["t0"] + XF / 2 - 0.45 for g in groups[1:]]
    overlays = render_overlays(tl, work, h)
    mix, clips = build_audio(tl, work, total, overlays, whooshes)
    subs, lines = build_subs(tl, clips, work, total)
    (PROJ / "renders").mkdir(exist_ok=True)
    dst = PROJ / "renders" / ("preview_480p.mp4" if fast else "final_2k.mp4")
    render_final(groups, overlays, subs, mix, total, dst, h, fast)
    chapters = ["0:00 Intro"] + [f"{int(s['at'] // 60)}:{int(s['at'] % 60):02d} {s.get('chapter', s['title'])}" for s in tl["sections"]]
    (PROJ / "renders" / "chapters.txt").write_text("\n".join(chapters) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(dst), "duration": round(total, 2), "chapters": chapters,
                      "items": [(it["src"], it["in"], it["out"], it["t0"]) for it in tl["video"]]}, indent=1))


if __name__ == "__main__":
    main()





