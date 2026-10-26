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
import time
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
ROOT = PROJ.parents[1]
SHARED_SFX = ROOT / "projects/miya-moore-oftv/assets/sfx"
FPS = 30
XF = 0.5
SECTION_DUR = 4.8
TAG_DUR = 5.5


def run(cmd, **kw):
    line = "  $ " + " ".join(str(c) for c in cmd)[:200]
    # source folders can contain characters the console code page can't print (e.g. Thai)
    print(line.encode(sys.stdout.encoding or "utf-8", "replace").decode(sys.stdout.encoding or "utf-8"), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def ff(*args):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def nframes(it):
    # pad_tail / pad_head = frozen last / first frame, so a whip sits in silence
    return round((it["out"] - it["in"] + it.get("pad_tail", 0.0) + it.get("pad_head", 0.0)) * FPS)


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
        # iPhone HLG (bt2020) and SDR clips are mixed: convert the matrix and tag every segment bt709,
        # otherwise the colour params change mid-stream and xfade ends the video early.
        vf += (f",scale={w}:{h}:flags=lanczos:out_color_matrix=bt709:out_range=tv,setsar=1,format=yuv420p,"
               "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv")
        if it.get("pad_tail"):
            vf += f",tpad=stop_mode=clone:stop_duration={it['pad_tail']}"
        if it.get("pad_head"):
            vf += f",tpad=start_mode=clone:start_duration={it['pad_head']}"
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
            clips.append({"src": tl["sources"][it["src"]], "in": it["in"], "out": it["out"],
                          "at": it["t0"] + it.get("pad_head", 0.0),
                          "words": it["src"]})
    for vo in tl["vo"]:
        clips.append({"src": tl["sources"][vo["src"]], "in": vo["in"], "out": vo["out"], "at": vo["at"],
                      "words": vo["src"]})
    return clips


SRC_LUFS = {}


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
        # Pieces under ~2.5 s can't be measured reliably (EBU gating) — use the
        # loudness of their whole source recording instead.
        if d < 2.5:
            if c["src"] not in SRC_LUFS:
                full = work / f"src_{len(SRC_LUFS):02d}.wav"
                ff("-i", c["src"], "-vn", "-ac", "1", "-ar", "48000", "-af", "highpass=f=80", full)
                SRC_LUFS[c["src"]] = loudness(full)
            lufs = SRC_LUFS[c["src"]]
        else:
            lufs = loudness(raw)
        ff("-i", raw, "-af", f"volume={-16 - lufs:.2f}dB", "-ar", "48000", lev)
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

    # --- karaoke performance: her sung vocal (camera mic, headphones -> no backing in it)
    # and the karaoke backing placed with a constant offset so it lands on her beat.
    sg = tl["song"]
    it = tl["video"][sg["item"]]
    song_at = it["t0"] + it.get("pad_head", 0.0)
    vraw = work / "vocal_raw.wav"
    vd = it["out"] - it["in"]
    ff("-ss", f"{it['in']:.4f}", "-i", tl["sources"][it["src"]], "-t", f"{vd:.4f}", "-vn", "-ac", "1", "-ar", "48000",
       "-af", f"highpass=f=80,afftdn=nr=6:nf=-50:tn=1,acompressor=threshold=-24dB:ratio=2:attack=10:release=200,"
              f"afade=t=in:d=0.05,afade=t=out:st={vd - 0.3:.4f}:d=0.3", vraw)
    vocal = work / "vocal.wav"
    ff("-i", vraw, "-af", f"volume={-14 - loudness(vraw):.2f}dB", "-ar", "48000", vocal)
    kar = work / "karaoke.wav"
    ff("-i", sg["karaoke"], "-vn", "-ac", "2", "-ar", "48000", work / "kar_full.wav")
    kin = it["in"] + sg["offset"]  # karaoke time = camera time + offset
    ff("-ss", f"{kin:.4f}", "-i", work / "kar_full.wav", "-af",
       f"volume={-14 - loudness(work / 'kar_full.wav'):.2f}dB,afade=t=in:d=1.5", "-ar", "48000", kar)
    # lo-fi bed for the talking intro and outro only
    lofi = work / "lofi.wav"
    ff("-i", tl["lofi"], "-vn", "-ac", "2", "-ar", "48000", "-af",
       f"volume={-14 - loudness(tl['lofi']):.2f}dB", lofi)
    out_at = tl["video"][tl["outro_item"]]["t0"]
    li_end = song_at + 2.5
    lo_from = tl.get("lofi_outro_from", 30.0)
    music = work / "music.wav"
    ms_song, ms_out = int(song_at * 1000), int(max(0, out_at - 0.5) * 1000)
    ff("-i", lofi, "-i", kar, "-filter_complex",
       f"[0:a]atrim=0:{li_end:.3f},afade=t=in:d=1.5,afade=t=out:st={li_end - 3.5:.3f}:d=3.5,volume={tl['lofi_gain']}dB,apad[a];"
       f"[1:a]volume={sg['music_gain']}dB,adelay={ms_song}|{ms_song},apad[k];"
       f"[0:a]atrim={lo_from}:{lo_from + total - out_at + 1:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=3,"
       f"volume={tl['lofi_gain']}dB,adelay={ms_out}|{ms_out},apad[b];"
       f"[a][k][b]amix=inputs=3:normalize=0,atrim=0:{total:.3f}[m]", "-map", "[m]", "-ar", "48000", music)
    ff("-i", vocal, "-af", f"volume={sg['vocal_gain']}dB,adelay={ms_song}|{ms_song},apad,atrim=0:{total:.3f}",
       "-ar", "48000", work / "vocal_placed.wav")
    ff("-i", speech, "-i", work / "vocal_placed.wav", "-filter_complex",
       "[0:a]volume=-6dB[s];[1:a]anull[v];[s][v]amix=inputs=2:normalize=0,volume=6dB[o]", "-map", "[o]",
       "-ar", "48000", work / "voice_bed.wav")
    speech = work / "voice_bed.wav"
    whoosh = work / "whoosh.wav"
    ff("-i", SHARED_SFX / "whoosh.wav", "-af", f"volume={-14 - loudness(SHARED_SFX / 'whoosh.wav'):.2f}dB",
       "-ar", "48000", whoosh)
    train = work / "pop_train.wav"
    ff("-stream_loop", "6", "-i", SHARED_SFX / "pop.wav", train)
    pop = work / "pop.wav"
    ff("-i", SHARED_SFX / "pop.wav", "-af", f"volume={-14 - loudness(train):.2f}dB", "-ar", "48000", pop)

    fc = ["[0:a]volume=-6dB,aformat=channel_layouts=stereo[sp]",
          f"[1:a]atrim=0:{total:.3f},afade=t=out:st={total - 4:.3f}:d=4[mu]"]
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


PLATE_CACHE = ROOT / "projects" / "_plate_cache"


def remotion_render(comp, props, dst, h, rc):
    """Render one alpha plate; retries because a font fetch can stall Remotion forever."""
    pf = dst.with_suffix(".json")
    pf.write_text(json.dumps(props))
    tmp = dst.with_name(dst.stem + ".part.webm")
    for attempt in range(3):
        try:
            subprocess.run(["npx.cmd", "remotion", "render", "src/oftv/index.tsx", comp, str(tmp), f"--props={pf}",
                            "--codec=vp9", "--pixel-format=yuva420p", "--image-format=png",
                            f"--scale={h / 2160}", "--log=error"], cwd=rc, check=True, timeout=240)
            tmp.replace(dst)  # only a finished render lands in the cache
            return
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            print(f"  ! plate {dst.name} attempt {attempt + 1} failed: {type(e).__name__}", flush=True)
            subprocess.run(["taskkill", "/F", "/IM", "chrome-headless-shell.exe"], capture_output=True)
    raise RuntimeError(f"plate render failed: {dst.name}")


def render_overlays(tl, work, h):
    """Tag + section plates. Identical plates (same component, props, height) are
    rendered once and shared by every project through PLATE_CACHE."""
    import hashlib
    rc = ROOT / "remotion-composer"
    PLATE_CACHE.mkdir(exist_ok=True)
    jobs = [("TagPlate", {"tag": tl["tag"]}, tl.get("tag_at", 0.8))]
    for s in tl["sections"]:
        jobs.append(("SectionPlate", {"index": s["index"], "title": s["title"], "label": s.get("label", "Part")}, s["at"]))
    out = []
    for comp, props, start in jobs:
        key = hashlib.sha1(json.dumps([comp, props, h], sort_keys=True).encode()).hexdigest()[:12]
        dst = PLATE_CACHE / f"{comp}_{key}_{h}.webm"
        if not dst.exists():
            t = time.time()
            remotion_render(comp, props, dst, h, rc)
            print(f"  plate {comp} {props} rendered in {time.time() - t:.0f}s", flush=True)
        out.append({"file": dst, "start": start})
    # Same tag plate again (e.g. when she mentions OnlyFans / says goodbye).
    for rep in tl.get("tag_repeats", []):
        out.append({"file": out[0]["file"], "start": rep["at"]})
    return out


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def wrap2(text, limit=40):
    """At most two lines: break at the space nearest the middle when the cue is long."""
    if len(text) <= limit:
        return text
    mid = len(text) // 2
    spaces = [i for i, ch in enumerate(text) if ch == " "]
    cut = min(spaces, key=lambda i: abs(i - mid))
    return text[:cut] + r"\N" + text[cut + 1:]


def build_subs(tl, clips, work, total):
    # English translation cues in clip-local source time (timed from the Spanish
    # word timestamps): {"IMG_8001": [[start, end, "English text"], ...]}.
    cues_db = json.load(open(PROJ / "assets/analysis/subs_en.json", encoding="utf-8"))
    mapped = []
    for c in clips:
        for st, en, text in cues_db.get(c["words"], []):
            if en <= c["in"] + 0.05 or st >= c["out"] - 0.05:
                continue
            mapped.append([text, c["at"] + max(st, c["in"]) - c["in"], c["at"] + min(en, c["out"]) - c["in"]])
    mapped.sort(key=lambda x: x[1])
    lines = []
    for i, (text, st, en) in enumerate(mapped):
        en = max(en + 0.25, st + 1.0)
        if i + 1 < len(mapped):
            en = min(en, mapped[i + 1][1] - 0.04)
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
    common = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
              "-c:a", "aac", "-b:a", "160k" if fast else "320k", "-ar", "48000", "-movflags", "+faststart"]
    head = [*inp, "-filter_complex", None, "-map", "[vout]", "-map", f"{n + len(overlays)}:a", "-t", f"{total:.3f}", "-r", "30"]
    # Intel Quick Sync encodes the 2K master ~3.5x faster than libx264 -preset fast at the
    # same measured quality (PSNR within 0.1 dB); H.264 High, yuv420p/nv12, bt709 -> OFTV spec.
    qsv = ["-c:v", "h264_qsv", "-preset", "slow", "-global_quality", "24" if fast else "17",
           "-profile:v", "high", "-g", "60"]
    x264 = ["-c:v", "libx264", "-preset", "ultrafast" if fast else "fast", "-crf", "28" if fast else "16",
            "-pix_fmt", "yuv420p"]
    for name, enc, tail in (("h264_qsv", qsv, ",format=nv12"), ("libx264", x264, "")):
        graph = ";".join(fc[:-1] + [fc[-1].replace("[vout]", f"{tail}[vout]")])
        args = [graph if a is None else a for a in head]
        try:
            t = time.time()
            ff(*args, *enc, *common, dst)
            print(f"  final encoded with {name} in {time.time() - t:.0f}s", flush=True)
            return name
        except subprocess.CalledProcessError:
            print(f"  ! {name} failed, falling back", flush=True)
    raise RuntimeError("final encode failed")


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
    T = {"t0": time.time()}
    groups = render_items(tl, work, w, h, fast)
    T["items"] = time.time() - T["t0"]
    whooshes = [g["t0"] + XF / 2 - 0.45 for g in groups[1:]]
    t = time.time()
    overlays = render_overlays(tl, work, h)
    T["plates"] = time.time() - t
    t = time.time()
    mix, clips = build_audio(tl, work, total, overlays, whooshes)
    subs, lines = build_subs(tl, clips, work, total)
    T["audio"] = time.time() - t
    T["t_final"] = time.time()
    (PROJ / "renders").mkdir(exist_ok=True)
    dst = PROJ / "renders" / ("preview_480p.mp4" if fast else "final_2k.mp4")
    enc = render_final(groups, overlays, subs, mix, total, dst, h, fast)
    if not fast:  # the preview is just a downscale of the master: seconds, not a second render
        ff("-i", dst, "-vf", "scale=854:480:flags=bicubic,format=nv12" if enc == "h264_qsv" else "scale=854:480",
           *(["-c:v", "h264_qsv", "-global_quality", "26"] if enc == "h264_qsv" else ["-c:v", "libx264", "-crf", "26"]),
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", PROJ / "renders" / "preview_480p.mp4")
    print(f"STAGES items={T['items']:.0f}s plates={T['plates']:.0f}s audio={T['audio']:.0f}s "
          f"final+preview={time.time() - T['t_final']:.0f}s total={time.time() - T['t0']:.0f}s", flush=True)
    chapters = ["0:00 Intro"] + [f"{int(s['at'] // 60)}:{int(s['at'] % 60):02d} {s.get('chapter', s['title'])}" for s in tl["sections"]]
    (PROJ / "renders" / "chapters.txt").write_text("\n".join(chapters) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(dst), "duration": round(total, 2), "chapters": chapters,
                      "items": [(it["src"], it["in"], it["out"], it["t0"]) for it in tl["video"]]}, indent=1))


if __name__ == "__main__":
    main()







