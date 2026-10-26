# OFTV editing playbook (team edition)

This file is the whole brain of the OFTV editing job. Read it fully before any OFTV work. The official rules are in
`oftv/OFTV_RULES.md` — every final must pass its checklist.

**Who you work for:** editors who write in Russian and are NOT technical. Answer in Russian, short and plain (no code,
no file internals unless asked). Ask only what is really missing — all questions for a job in ONE message — then work
fast and on your own: run long steps in the background, keep the PC awake (`request_keep_awake`) before renders,
fix errors yourself. Never ask them to run commands; you run everything.

## The three job types (slash commands in `.claude/commands/`, plain Russian works too)

| They write | Job | What it means |
|---|---|---|
| `/bazovoe <папка>`, «смонтируй», «базовое видео» | **basic** | standard OFTV edit: tag plate, PART plates, subtitles, music, whips, cover, title, description |
| `/pervoe <папка>`, «первое видео» | **first** | the model's FIRST video on the channel = show-level edit: same as basic **plus** pop-up graphics (`ShowGraphics.tsx` / `HalloweenGraphics.tsx`, face-safe placement), a title card, a stronger cover; extra-strict QC |
| `/peremontazh <папка>`, «перемонтаж», «объедини два видео» | **remix** | two similar finished/raw videos of one model → ONE new restructured video (see "Remix" below) |
| `/pravki <модель> <что не так>`, «правки», «OFTV отклонил» | **fix** | revise an existing project from feedback (OFTV rejection, model's nitpicks) — change only what was asked |

A **folder** can be (auto-detected by `oftv/tools/intake.py`, override with `--single` / `--batch`):
- **one video** — a folder named by the model's tag with the footage inside (nested camera folders are fine);
- **a batch** — e.g. `Downloads\монтаж пн\` with one sub-folder per model, each named by her tag
  (`daisyyyli`, `lia_life`, `karisha.x` …) and optionally a `music` sub-folder shared by all.
One model folder may still hold TWO videos (two shoots / outfits / topics, e.g. `mia\1` + `mia\Halloween`) —
intake warns about sub-folders; split into `<slug>` and `<slug>b` after looking at the sheets.

## Step by step (every job)

All commands from the repo root with the venv python: `.venv\Scripts\python.exe`. In PowerShell refresh PATH first:
`$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine")+";"+[Environment]::GetEnvironmentVariable("Path","User")`

1. **Intake** — `python oftv/tools/intake.py "<папка>"` → creates `projects/<tag>-<MMDD>/` per video (job.json,
   sources.json, probe.json, template scripts in `scripts/`) and prints warnings. Batch list → `projects/_batches/`.
2. **Quick pass** (background) — `python oftv/tools/quick_pass.py <project>` or `batch:<batch-name>` (audio, sheets,
   VAD, small Whisper only where there is speech). Add `blur` for b-roll heavy videos.
3. **Look and ask** — read the sheets (`assets/analysis/sheets/*.jpg`) and quick transcripts → figure out talking
   clips vs voice notes vs b-roll, the story, sections, which audio files are music vs voice memos (ALWAYS
   transcribe any audio before using it as music). Then ONE message with all questions for the whole batch, e.g.:
   tag spelling (folder name → `@name`, confirm once, set `tag_confirmed` in job.json), music (folder track / lofi
   pick), one video or two, vertical clips, anything doubtful. Don't ask what the playbook already decides.
4. **Accurate pass** — `oftv/tools/accurate_words.py <project> <lang> <keys…>` (talking clips, voice notes) or
   `oftv/tools/accurate_phrases.py <project> <lang> <keys…> vo:<key>` for voice notes full of retakes.
5. **Plan** — write `scripts/plan_timeline.py` (see `scripts/plan_timeline_example.py` + `plan_common.py`
   docstring; older planners for special cases are in `oftv/reference/<old project>/`), run it →
   `artifacts/timeline.json` + `subs_en.json`.
6. **Render** — `python scripts/render_timeline.py --res 1440` (in background) → `renders/final_2k.mp4` +
   `renders/preview_480p.mp4`. One render / one Remotion job at a time on the PC.
7. **QC** — video vs audio stream duration equal; audio levels (dialogue p10/p50/p95, music) per OFTV_RULES;
   12-frame QA grid; `oftv/tools/check_preview.py renders/preview_480p.mp4 <lang>` → no doubled / clipped words at
   splices; length ≥ 2:00; tag at start + at the OnlyFans word; SFW. Fix and re-render until clean.
8. **Cover + texts** — 2 covers (1920×1080 + 3840×2160 JPG), title ≤ 40 chars, English description with chapters
   → `renders/title_description.txt`, `renders/chapters.txt`.
9. **Deliver** — `python oftv/tools/deliver.py <project>` copies final + covers + texts to
   `Desktop\OFTV готово\<tag> <date>\`. Tell the editor in 3–5 lines: where the files are, length, title, anything
   doubtful (subtitle guesses, missing lines). Set job.json `status` to `delivered`.

In a batch: intake + quick pass for all first, ask once, then edit the videos one after another (2K render of one
while planning the next is fine; never two renders at once) and deliver each as soon as it is ready.

## Remix (two videos → one) — `/peremontazh`

Scripts: `oftv/templates_remix/` (from remix-p1022, mix updated to the 2026-10-24 levels). Order: intake →
`separate.py` (Demucs vocals / no_vocals — original music removed; run BEFORE Whisper, it loops on music) →
`transcribe.py A B` (large-v3-turbo on the vocal stems) → `scan_burned.py` (burned subs / tags / white flash
transitions → `crop` / `cover` / `prefilter` in the edit map) → `artifacts/edit_map.json` by hand: sentence-level
segments alternating A and B (no A-then-B), intro and outro built from both, repeats and filler cut, never invented
words → `render_remix.py --res 1440` → `check_joins.py` (re-transcribe every join) + `qa.py` → cover + texts → deliver.
Full brief and pitfalls: Lessons → "Two video remix".

## New lessons

When an editor gives a new standing rule, a model's preference or a rejection reason, add it to **Lessons from past
jobs** at the bottom of this file (date, what happened, the rule) — this file is shared with the whole team through
git (`/obnovit` syncs it). Don't keep team knowledge only in personal memory.

---

## Standing rules (don't re-ask)
- **Tag plate twice**: at the start (0.8 s) and again on the moment she says "OnlyFans" near the end
  (if she never says it — while she says goodbye). Tag exactly as given; add `@` if missing.
- **Export**: final 2560×1440, 30 fps, H.264 (CRF 16, preset `fast`) + AAC 320k. Previews at 480p only.
  The user re-exports through CapCut, so 2K is wanted even from 1080p sources.
- **Length ≥ 2:00** (OFTV). Trimming b-roll / try-on footage is fine.
- **Audio recipe (current, 2026-10-24)**: voice levelled per line + compressed, median −9 dBFS (p10 ≥ −12.5, ceiling −6);
  music median −15.5, ceiling −12, mild duck; whoosh/pop ≈ −12; limiter −1 dBFS. Measured by 100 ms block peaks per stem.
  OFTV rejected both 'music too quiet' (2026-10-19) and 'music too loud' (2026-10-24) — see Lessons → audio levels.
- **B-roll / store audio fully muted** when there is voice-over; only VO + on-camera speech + music + SFX.
- **Never put VO over shots where she visibly talks** (moderation rejects it), turns to someone off-camera,
  leaves the frame or the camera is in a close-up. Pick b-roll ranges from (a) Silero VAD on the camera audio
  (`faster_whisper.vad.get_speech_timestamps`) — silent stretches only — and (b) face-crop contact sheets every
  3–4 s (`crop=iw*0.32:ih*0.5:iw*0.3:ih*0.02`) checked by eye; quiet mics can hide talking, so (b) is mandatory.
- **Subtitles one line** (≤ 32 chars, balanced splits, no dangling "the/to/my/and…"; no 2-line wrap).
- Music: use the track(s) in the folder; if none — pick from `music_library/lofi` (CC0) and say which.
  Two tracks → chain with a 6 s crossfade. No copyrighted / generated music without asking.
- Never modify/delete the user's source files. Never generate video/images/voice.
- Cover + title + description: no OFTV / OnlyFans mentions, just the video topic.

## Approved look
- Tag plate top-right (`TagPlate`), section plates bottom-left "PART 0N / Title" (`SectionPlate`, `label`
  can be "Skirt" etc.), ~4.8 s; a soft "pop" on every plate appearance.
- 4–6 sections + "Final Thoughts". Whip transitions ("вжух": xfade smoothleft 0.5 s + motion blur + whoosh)
  only intro→main and main→outro, and only inside silence (never over words).
- Subtitles: UPPERCASE, Segoe UI Semibold, at the very bottom (ASS PlayRes 3840×2160, size 84, MarginV 55).
  Fix Whisper mishears in subtitles via `word_edits` (e.g. "nail streaks"→"new skirts"); flag doubtful ones.
- Chapters file `renders/chapters.txt` (0:00 Intro + sections).

## Tools / environment
- Repo = this folder, venv `.venv` (Python 3.11): faster-whisper large-v3 (CPU int8), FFmpeg 9
  (winget; refresh PATH in each PowerShell call:
  `$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine")+";"+[Environment]::GetEnvironmentVariable("Path","User")`).
- Remotion overlays + covers: `remotion-composer/src/oftv/` (`OftvOverlays.tsx` = TagPlate, SectionPlate;
  `CoverTitle.tsx` = photo + title block, `side` left/right, `top`; `CoverSplit.tsx` = photo left + cream panel).
  Fonts load from Google → **needs internet**; if a plate render fails, check the connection and re-run (cache keeps progress).
- (Numbers below are from the lead editor's PC: Intel Core 5 220H, no NVIDIA; `oftv/tools/doctor.py` checks yours.) **Intel Quick Sync (h264_qsv) works** (tested 2026-10-17):
  the 2K master is encoded with `h264_qsv -preset slow -global_quality 17 -profile:v high` (same PSNR as
  libx264 crf16, ~3.5× faster encoder; libx264 is the automatic fallback). Whisper stays CPU ≈ 2–3× realtime.
- **Talking-head-only edits (many short single-sentence takes, no b-roll)**: `oftv/reference/shelly-moss-oftv/`
  (plan_timeline.py: one row per clip with clean text + section titles, 1.08 punch-in alternating on jump cuts;
  render_timeline.py = the renderer below with the 2026-10-19 OFTV mix levels built in + SectionPlate). ~10 min total.
- **Current renderer template: `oftv/reference/mia-bluebird-oftv/render_timeline.py`** (old −14 LUFS mix — take
  `build_audio` from `projects/shelly-moss-oftv` or `ki-oftv` for the new levels) — QSV master, 480p preview
  is a downscale of the master (no second full pass: render `--res 1440` only), section/tag plates cached across
  projects in `projects/_plate_cache/` (hash of component+props+height), Remotion calls have a 240 s timeout +
  retry (a font fetch hung a plate forever after the PC slept), per-stage timings printed (`STAGES ...`).
  Measured 2:30 video: items 7 s (cached) · plates ~48 s each · audio 47 s · final+preview 151 s.
- Don't decode with `-hwaccel qsv` + `-ss`: frames come out a few frames late (breaks VO/VAD sync). CPU decode only.
- Ask the app to keep the PC awake (`request_keep_awake`) before long renders — it slept 2 h mid-render.
- Never run two Remotion jobs at once (covers + plates) — the plate render crashed.
- **Disk fills up**: each project's `work_*` cache is 2–6 GB (C: hit 0 GB on 2026-10-19 → "No space left on device"
  mid-concat). Check free space before a render (`Get-PSDrive C`); `work_*` dirs of delivered projects are safe to
  delete (regenerable from sources; user OK'd it) — never touch `renders/`, `assets/`, `_plate_cache`.
- Whisper on short phrases can stall for minutes in temperature-fallback loops: always pass `temperature=0.0,
  max_new_tokens=120` in phrase-level passes and watch the log for a stalled line.
- Pause squeezing must use word timestamps, not energy: quiet word onsets ("You can…") read as silence and got cut.

## Workflow (multi-source VO projects — use `projects/emilyix-vlog` as the template)
1. Probe folder (ffprobe: res, fps, rotation, color_range, audio). `init_project('<slug>', ...)`.
2. Contact sheets per clip (`fps=1/(dur/6), tile=6x1`, use `fontfile='C\:/Windows/Fonts/arial.ttf'` for drawtext)
   + quick `small` whisper of all clips/VO → figure out talking clips vs b-roll and the story. Ask questions.
3. Accurate pass: faster-whisper **large-v3, `vad_filter=False`**, `word_timestamps=True`,
   `condition_on_previous_text=False` (the VAD in `tools/analysis/transcriber.py` drops retakes — don't use it)
   → `assets/analysis/transcripts.json`. Energy-based speech bounds → `speech_bounds.json`.
4. Copy `scripts/plan_timeline.py` + `scripts/render_timeline.py` from the template project, edit the plan:
   talking items (`speech: true`, trimmed to speech ±0.3/0.45 s), VO topics → b-roll lists (lengths fitted to
   narration), sections, `tag_repeats` (offset to the OnlyFans word), `word_edits`, music list.
   Groups `intro` / `main` / `outro`; each group boundary needs ≥ 0.5 s of non-speech for the whip: `pad_tail`
   freeze on the outgoing clip and/or `pad_head` freeze (first frame) on the incoming one. **Never a short b-roll
   head** after a whip — the user flagged it as "wrong frame, then it changes" (aisha-noor-oftv).
5. `python scripts/render_timeline.py --res 1440` (writes final_2k.mp4 + preview_480p.mp4) → check: video stream
   duration == audio duration, ebur128, a 12-frame QA sheet. Send preview + covers. Whisper only voice notes and
   clips that VAD says contain speech — never the silent b-roll.
6. Cover: 2 variants from the user's photo (or best 4K frame), export 1920×1080 + 3840×2160 JPG.
   Title ≤ 40 chars + English description with chapters → `renders/title_description.txt`.

## Gotchas already solved (keep these fixes)
- Mixed full-range (yuvj420p/pc) and limited-range iPhone clips break the concat/filter graph → every segment is
  scaled with `out_range=tv`, `-color_range tv`.
- **iPhone HLG (bt2020, 10-bit) mixed with SDR clips** (mia-pixel-oftv) → the colour params change mid-stream and
  `xfade` silently ends the video early (video 84 s, audio 197 s). Every segment: `scale=...:out_color_matrix=bt709`
  + `setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv`. Don't tonemap (hable looked orange).
  Always compare video vs audio stream duration after a render.
- Russian/other-language models: keep the original voice, subtitles = hand translation to English (`subs_en.json`
  cues, DP split into one-line ≤ 32-char cues), all plates/titles English only.
- `-t` must be an **input** option (before `-i`) or it cuts the `tpad` freeze-frame tail.
- Rotated sources (rot=90/−90/180) are auto-rotated by ffmpeg; 60 fps → `fps=30`.
- Phone voice notes are ~10 dB hotter than the camera mic → per-line levelling is mandatory for an even voice.
- **One long VO recording full of retakes** (amane-misa-oftv): the normal large-v3 pass merges repeats and its
  word times stretch over hidden takes. Split the VO by energy into phrases (≥0.35 s silence) and transcribe each
  phrase separately; pick the last clean take per line; fine-split messy phrases with a 0.12 s silence threshold.
  Then transcribe the **rendered preview audio** again to catch leaked words at splices. Subtitles for such VO come
  from the chosen clean text (`scripts/make_subs.py` → `subs_en.json`), not from Whisper words.
- Non-English chatter on camera: use only the English lines; camera audio under VO is muted anyway.
- VO pieces < 2.5 s can't be loudness-measured (EBU gating) → use the whole recording's loudness for them.
- Killing a render mid-way leaves half-written `ov_*.webm` / `v_*.mkv` that the cache then trusts → delete the
  partial files (and `v_*` whenever clip trims change) before re-running.
- Folder names with Thai/other scripts crash `print` under `python -I` (cp1251 console; `-I` ignores
  `PYTHONIOENCODING`) → the renderer encodes printed commands with `errors="replace"`.
- **Segment cache is content-addressed** in `oftv/reference/mall-trip/render_timeline.py` (`seg_key` = hash of
  source+in+out+zoom+pads+size): inserting intro/outro or re-trimming one topic no longer re-renders everything.
  Prefer this renderer as the template (older ones name segments by index → stale after any insert).
- Vertical (portrait) talking clips can't go into a 16:9 OFTV video as-is — ask the user for a horizontal export
  (they re-exported `ыв.mp4` 2560×1440) before improvising blurred side-fills.
- One-frame glitches (hand over the lens, red flash) show up on the QA grid; locate them per frame with a tiny
  `scale=32:18` RGB scan and split the clip range around them.
- Cutout covers (`CoverDreamy` / `CoverShop`): rembg `isnet-general-use` + alpha matting on the user's photo, blurred
  frame of her own footage behind, neon title + doodles. Never point a doodle arrow at her body.
- **Not enough silent b-roll for the VO** (latina-ana-oftv27: 127 s footage / 186 s narration): run the b-roll as
  one continuous stream in story order with a uniform slow-mo (`speed` per item in the renderer, setpts; kept
  ≥ 0.68) and anchor section plates to the first VO line of each section. Squeeze > 0.5 s pauses inside VO
  pieces by word timestamps first.
- Talking-clip out-points must be clamped to the file duration (VAD end + 0.3 can run past the last frame →
  the segment comes out short and the audio drifts).
- **Voice on one channel only** (bela-cruz-29/30: external mic on the RIGHT channel, left silent): check
  `pan=mono|c0=c0` vs `c1` volumedetect; set `"speech_channel": 1` in the timeline — the renderer
  (`oftv/reference/bela-cruz-29/render_timeline.py`) then takes that channel for every speech piece and the
  mono voice goes to both ears; music stays stereo. Verify L/R mean volume match in the final.
- **"Guion NN" folders** (ESC 1 intro, ESC 2-6 takes + VOZ EN OFF/ESC n voice note, ESC 7 outro, FOTOS): one
  folder per video; `oftv/reference/bela-cruz-29/plan_common.py` builds it from a small config. Some takes come
  without the .MOV extension (e.g. "ESC 3 TOMA 3.1") — the user OK'd renaming them (add `.MOV`).
- Single talking-head (one long take with retakes): see `oftv/reference/miya-moore-oftv/` (plan_edit.py:
  retakes/pauses via no-VAD transcript + energy; punch-in 1.08 on visible jump cuts).

- **Pre-assembled source with pillarboxed vertical inserts** (hessakhalifa-oftv): find them with a black-border scan
  (`crop=200:1080:0:0,scale=8:8` luma < 8), then rebuild the middle as VO sentences over horizontal footage only.
- **VO much longer than b-roll** (karisha-x-oftv): keep key sentences + `stretch: 1.2` on 25 fps clips (every source
  frame lands on one 30 fps frame = smooth 0.83x). Renderer: `oftv/reference/karisha-x-oftv/render_timeline.py`.
- Voice-note file names can be NFD-normalised (`c` + U+0301): look them up by suffix in Python, never by typed name.
- VO recordings with spoken notes-to-self ("the third part") / retakes: per-phrase pass
  (`oftv/reference/zoey-bee-pumpkin/phrase_pass.py`), then pick lines by hand. Per-clip `fixed` b-roll ranges keep
  a key action (lid lifted off) whole while the rest is compressed.
- Generic batch helpers: `oftv/tools/quick_pass.py` (audio/sheets/VAD-gated small whisper) and
  `oftv/tools/accurate_words.py` (large-v3 words). Several sessions share the PC: large-v3 can fail with
  `mkl_malloc` when RAM is short — just re-run (it resumes).

- **One long on-camera script take full of retakes + crew chatter** (lana-bunny-oftv C0001, Sony 4K): per-phrase pass
  (`oftv/tools/accurate_phrases.py <proj> en vo:C0001`), keep the last clean take of each line; intro/goodbye stay on
  camera, recipe lines play as VO over the process footage; `plan_common.py` scenes take a 6th value `extra` (s of
  music-only process after the voice) to reach 2:00. Cues that straddle two takes show twice — put a sentence break
  at the splice in the subtitle text.
- **Talking costume/GRWM with long quiet stretches and no VO recordings** (zoey-bee-leeloo): keep her speech pieces,
  fast-forward the silent stretches (`speed` 2-2.5, muted), 1.08 punch-in on jump cuts inside one clip.
- HEIC photos: ffmpeg decodes them as a tile grid — convert without `-vf` first, scale in a second pass.
- `oftv/tools/intake.py` + `oftv/tools/quick_pass.py` = batch quick pass for any Downloads folder
  (recursive, so nested camera folders work).

## Typical timing
Analysis + questions ~10 min → transcription ~5–10 min → plan + 480p preview ~10 min → 2K ~10 min. ≈ 30–40 min/video.

---

# Lessons from past jobs

(Older projects' scripts are kept as reference in `oftv/reference/<project>/` — a path like `oftv/reference/X/y.py` below means `oftv/reference/X/y.py` on a fresh PC.)

## Audio levels
_OFTV mix levels (since 2026-10-24): voice median -9 evened to -12..-6, music median -15.5 ceiling -12 (~6.5 dB under voice); both 'too quiet' and 'too loud' rejections_

OFTV has rejected music in both directions, always quoting "Dialogue −12…−6 dB, Music −16…−10 dB":
- 2026-10-19 `Downloads/112.mp4`: music **too quiet** (music ~10 LU under the voice).
- 2026-10-24 `projects/hessakhalifa-oftv`: music **too loud** with voice median −10 / music median −14 / music p95 −10
  — the voice's quiet words dropped to −19 dB (p10), below the music.

Current recipe (100 ms block peaks of each stem in the final mix, `oftv/reference/hessakhalifa-oftv/render_timeline.py`):
voice → per-line levelling, then `acompressor threshold=-30dB ratio=4 attack=5 release=150 makeup=3`, median **−9**,
ceiling −6 → p10 ≥ −12.5. Music median **−15.5** (pre-duck target −14.5), ceiling **−12**, mild sidechain duck under the
voice (`sidechaincompress threshold=0.12 ratio=1.4`). Result on Hessa: dialogue p10/p50/p95 −12.3/−9/−6, music
−20/−15.5/−12.5, ≈ −16 LUFS. A strong duck (threshold 0.02 ratio 3) pushed music to −28 under the voice — too quiet again.

**Why:** both extremes were rejected; the reviewer wants both stems inside their ranges with the voice clearly on top
and no quiet words sinking under the music.
**How to apply:** use these targets for every new OFTV mix; report dialogue p10/p50/p95 and music (incl. under-voice)
with every final. Full rules: rules file; see also edit playbook.

## Strict qc
_Picky models (zoey_bee, lana-bunny) — per-cut QC: no reaching/leaning to the lens, no repeated words at splices, no soft/shaky b-roll, no clipped word endings, keep the goodbye wave_

2026-10-23 the user sent back zoey_bee (Leeloo) and lana-bunny: "the model nitpicks a lot, everything must be perfect".
Complaints: shots where she says something while reaching/leaning toward the camera (start/stop recording),
lines said twice at a splice ("so hard to / to wear", "and of course this thing / of course..."), an off-topic
scene (pumpkin delivery guy), soft/shaky b-roll (lana 1:48), clipped word endings, video ending before her wave.

**Why:** these get the video rejected by the model, not by OFTV.
**How to apply:** for every talking edit build a per-item review sheet (frames every 1 s + the words in range,
`oftv/reference/zoey-bee-leeloo/review.py`) and trim before any lean/reach to the lens; re-transcribe the rendered
preview and search splices for doubled words (Whisper word ends are early — check energy, cut in the dip);
pick b-roll windows by blurdetect (`oftv/reference/lana-bunny-oftv/sharpness.py`, keep per-second blur ≲ 8.5);
extend speech spans to the real energy fall-off (`refine_span` in lana's plan_common.py); end on her wave.
Related: edit playbook, domontazh batch.

## Cover rules
_OFTV cover feedback — title text must never overlap the model; pick lively frames (eye contact, smile, eating/drinking)_

Cover text (CoverTitle eyebrow/headline/script/sub) must never touch the model or what she holds. If she is on the
left, use `"side": "right"`; reframe with a 16:9 crop so she fills ~0.05–0.6 of the width and the text block has
clear space; shorten the sub line if it reaches her. Check the rendered PNG before sending. Don't mirror frames that
show printed text (packaging/shirt letters read backwards). Good frames: eye contact + smile, sipping/biting, holding
the dish — not mid-word, eyes closed or wide shots with baked-in pop-ups; verify the exact timestamp at full res
(contact-sheet index → time mix-ups happened).

**Why:** 2026-10-22 the user rejected the first cover set as "неудачные кадры" and asked to move the "Sweet like art"
text right and to always keep text off the model.
**How to apply:** every OFTV cover; see edit playbook.

## Spanish model
_OFTV edits of Spanish-speaking models — keep Spanish voice, English subtitles + all on-screen text in English_

When the model speaks Spanish: keep her original Spanish audio (no dub/TTS), subtitles = English translation
of the Spanish speech (transcribe with whisper language="es", translate by hand naturally, never whisper task=translate
as final), all plates/pop-ups/titles in English, never Spanish or bilingual text on screen. Everything else per
OFTV_EDIT_PLAYBOOK.md (UPPERCASE subs, ≤2 lines, tag plate, audio recipe, 2K export). Talk to the user in Russian.

**Why:** user's standing brief for Spanish-speaking models (pasted 2026-10-16).
**How to apply:** any OFTV project where the source speech is Spanish; see edit playbook, audio levels.

Spanish remix (2026-10-19, `projects/oftv-remix-1019`): sources had burned-in English subs at the bottom, English
section titles at the left edge and a burned tag top-right — a 16:9 crop can't drop the subs without cutting those,
so the sub strip is blurred + darkened into a caption bar (`prefilter` in edit_map) and our subs come from a hand
translation file `artifacts/subs_en.json` (`subs_en` key). If the sources already show the tag at the start and on
the OnlyFans line, skip our own TagPlate (it would double up).

## Daisy style
_Daisy (@daisyyyli, picky model) — her own pop-up look + SFX copied from her reference edit Downloads/d.mp4_

Daisy (tag @daisyyyli; reference edit `Downloads/d.mp4` shows her older handle @daisyparadisee) is a picky
model ("модель с доебами") — every edit must copy her reference style, not our default plates.
Project 2026-10-20: `projects/daisyyyli-outfit` (basic outfit → stylish look, 4:46).

Look (`remotion-composer/src/oftv/DaisyGraphics.tsx`): `DaisyTag` = light-grey pill top-left, OnlyFans-blue
logo bubble pops, pill stretches, handle types in (blue Nunito 900). `DaisyTitle` = top-left two-line
section title, Fredoka 700 lavender fill #D8A4F0 + white rim + dark 3D drop, on a white dry-brush swipe,
big sparkle flash first, letters pop one by one, twinkle stars below. Subs: standard small white uppercase.
SFX cut from d.mp4 with Demucs (`oftv/assets/sfx/pop_daisy.wav` from drums stem @1.76 s, `oftv/assets/sfx/sparkle.wav` = chime from
other stem @34.93 s, highpass 1.5 kHz); renderer `scripts/render_timeline.py` plays pop on the tag and
sparkle on each title (`DAISY_SFX`, `POP_LEAD/SPARKLE_LEAD`). Reuse these files for her next videos.

User feedback 2026-10-21: tag plate = our usual TagPlate (top-right, usual pop), NOT DaisyTag; keep
DaisyTitle + sparkle for sections. Music: "Sound Of Freedom - Jazzy Rhodes Deep House" (Downloads/ее).
Gotcha: an .m4a in her folder named after a place ("Campetto di rovascio.m4a") was an iPhone VOICE MEMO
with extra lines, not music — I looped it as music and the voice ran over her on-camera speech.
Always transcribe any audio file before using it as music.

Cover: `CoverDaisy.tsx` (variant "split" before|after photos with Basic/Stylish bubble labels + arrow,
or "single" photo + bubble title + pill sub). Her PNG screenshots are only ~1120 px — take the same
moments from the 4K clips instead.

Her footage: short handheld-mic lines per step + silent try-on shots; split talk clips into speech item +
silent item. The person "at the window" on the left is her mirror reflection, not a guest.

**Why:** user asked for her special style + pop-up sounds exactly like d.mp4.
**How to apply:** copy `projects/daisyyyli-outfit/scripts` + `assets/sfx` for any new Daisy edit; see
edit playbook, audio levels.

## Show graphics
_Show-level OFTV edits (semantic pop-ups): components + renderer template from ki-oftv_

When the user asks for a "show-level" OFTV edit with semantic pop-ups (2026-10-18, project `projects/ki-oftv`,
cat-tree video), use `remotion-composer/src/oftv/ShowGraphics.tsx` (ShowTitle, PopSticker, NameTag, Checklist,
StepHud, Stamp, Punch, ChapterCard; length via `dur` prop) and `oftv/reference/ki-oftv/` (plan_timeline.py with
SEGMENTS talk/vo/cut + graphics anchored to source times; render_timeline.py with `--export-speech` → raw dialogue
bed for Adobe Podcast Enhance and `--enhanced <wav>` to swap the cleaned bed back in, music optional).

**Why:** the user's platform rejected plain edits; they clean speech themselves in Adobe Podcast Enhance.
**How to apply:** plates at 480 take ~30 s each (58 ≈ 55 min) and need internet for fonts. See edit playbook.

## Collab popups
_Two-model collab edit with 'cool pop-ups that never cover faces' (vitya-oftv-1, Eva x Lily): Halloween graphics set, face-safe auto placement, split-screen finale_

2026-10-26 the user asked for a "cool" first video with pop-ups that must not cover faces. Folder `Downloads/витя 1ви`
held TWO shoots of a collab (Eva 4K / Lily phone) + a script in a Google Doc (read via the built-in browser:
`fetch('/document/d/<id>/export?format=txt&tab=t.0')` in the doc tab — the Drive connector was not authenticated).
Models record VO lines inside their clips, several takes each; pick the last clean take per script line.

Built: `remotion-composer/src/oftv/HalloweenGraphics.tsx` (HwTitle, HwName, HwList, HwStep, HwSticker, HwStamp,
HwScene, HwSplit — positions via props), `CoverDuo.tsx` (two photo panels + title column so text never touches either
model), `oftv/reference/vitya-oftv-1/place_graphics.py` (isnet person mask on 3 frames per pop-up, head zone x5,
picks the free corner/side, avoids subtitle strip and other visible pop-ups), renderer with `crop_y` (16:9 band from
vertical overhead clips — looks native for top-down hand shots) and `split` items (side-by-side finale with freeze pads).

**Why:** reusable pattern for show-style edits and collabs.
**How to apply:** for pop-up requests reuse these components/placement; for collabs follow the script scene order and
alternate models. See show graphics, edit playbook, cover rules.

## Two videos one folder
_When one Downloads folder holds footage for two OFTV videos — split by shoot, edit as two projects_

2026-10-20 (`Downloads/ее`, @aisha_noor): one folder = two separate videos ("разобрать и сделать их 2"),
not a remix. Split by set/outfit on contact sheets + creation_time: makeup-bag talk (IMG_80xx, beige wall) →
`projects/aisha-noor-2a`; orange-bread cooking (IMG_89xx b-roll + talking) → `projects/aisha-noor-2b`.
Black portrait IMG_96xx clips were voice notes = VO for the cooking steps. Analysis files live in 2a and 2b
reads them; `2a/scripts/subs_util.py` has `timed_cues_xl` (times English cues from Spanish words by char fraction).
Her photos of the finished dish → 5 s push-in clips used as b-roll under "look how pretty it is".

**Why:** first two-in-one folder; recipe is repeatable.
**How to apply:** check whether a big folder is one video or several before planning; see edit playbook,
spanish model. Other chats run renders in parallel — never kill processes by command-line pattern
(I killed another chat's quick_pass that way).

## Two video remix
_User's standing brief for merging two similar videos into one restructured OFTV edit_

As of 2026-10-12 the user has a detailed brief for re-editing two similar source videos into one OFTV video: interleave sentence-level segments from both (no A-then-B), build the intro and outro from both, cut repeats and filler, never invent words. Strip the original music (use source separation such as Demucs if speech and music share one track, and check for artifacts), replace it with the user's supplied music file (loop or trim it, fade in and out, duck it under speech), add SFX only where they help, and match color between the sources. Work in stages: analysis, then an edit map with timecodes, then picture, audio, mix, QC. Report the output file, duration, export settings, how speech was processed, which music was used, and any issues left unfixed. Never claim a stage was done when it wasn't.

**How to apply:** follow this brief whenever the user asks to combine two videos. Use the levels in audio levels.

Template for a remix: `oftv/reference/oftv-remix-1017/render_remix.py` (edit_map.json: segments with in_fix/out_fix,
music list, `tag` plates, `sub_edits`; balanced one-line UPPERCASE subs) + `qa.py`. Verify every join by
re-transcribing the speech bed with large-v3.

Newest template (2026-10-19): `oftv/reference/ellie-remix-1019/render_remix.py` — adds `crop` (cut burned subs
away when sources are 4K), `cover` [[from,to,src,start(,"freeze")]] to hide stock inserts / jump cuts / the sources'
white flash transitions, `v_in_fix`, content-addressed segment cache, QSV final encode. Lessons: run Demucs BEFORE
Whisper (Whisper on music+speech looped for 27 min); Whisper word times can be ~0.3 s late — set cut points from the
vocal-stem energy, then check joins by transcribing ±3 s windows; scan sources for flash frames (luma spike vs 1 s
median); B-roll stock with other people gets cut (user wants it gone), covered with her own silent footage.

Newest template (2026-10-20): `oftv/reference/remix-1020/render_remix.py` — per-source `crop` dict, final mix on the
new block-peak levels (audio levels: dialogue p50 −10 / ceiling −6, music p50 −14 / ceiling −10, SFX −12, no
ducking). Pitfalls fixed there: mono→stereo via `aformat` loses 3 dB (use `pan=stereo|c0=c0|c1=c0`); don't normalize
the speech bed to −14 LUFS + limiter before the mix (it flattened the peaks to −13). Other chats often load the CPU
to 100% — Demucs/Whisper then take 3-5x longer; never kill their processes. On 2026-10-17 the user asked to add subtitles and the tag plate
(@tag at 0.8 s + at the goodbye) to a remix — include both by default from now on.

## Karaoke cover
_How to edit an OFTV karaoke-cover video (sync karaoke backing to her singing, lo-fi for intro/outro)_

Karaoke cover edit (2026-10-19, `projects/mia-tesh-karaoke`, tag @mia_tesh): folder = intro clip + song clip + outro
clip + a karaoke video (backing + lyrics) + a lo-fi track. User wants the karaoke backing "in time with the song"
under her singing and the lo-fi only for intro/outro.

She sings with headphones → camera audio has NO backing (Demucs no_vocals ≈ −82 dB), so xcorr against the track fails.
Sync = vocal-stem phrase onsets vs the karaoke video's lyric-highlight times (1 fps contact sheets) → constant offset
(here camera and karaoke started together, offset −0.39 s, no drift), then fine-tune with onset xcorr ±1 s (beat-spaced
peaks; take the one consistent across windows). Renderer: `scripts/render_timeline.py` with `song` block
(offset, vocal_gain −6, music_gain −9 = backing ~3 LU under voice; −12 sounded like a cappella). Check peak ≤ −6 dBFS.

**Why:** first karaoke job; repeatable recipe.
**How to apply:** reuse this project's scripts for the next karaoke video; see edit playbook, audio levels.
Disk C: was full (0 B) after the render — check free space before renders.

## Lofi library
_61 CC0 lofi tracks (HoliznaCC0, FMA) in OpenMontage\music_library\lofi — copyright-free music pool for OFTV edits_

2026-10-21 the user asked for copyright-free lofi "that fits every video, with some variety". Downloaded 61 tracks
(2–4 min, 320 kbps) by HoliznaCC0 from Free Music Archive, CC0 public domain → `music_library/lofi/` (gitignored),
license + source in `LICENSE.txt` there. Mood is in the file name (Happy / Chill / Nostalgic / Sad …).
Pixabay music scraping returns 403 (Cloudflare); FMA album pages embed `"fileUrl"` JSON → direct mp3 download works.

**Why:** OFTV forbids copyrighted music; user wants a ready pool instead of hunting tracks per video.
**How to apply:** when a video folder has no track, offer a pick from this library (still say which one) instead of
asking for new music; vary tracks between videos. Levels per audio levels, rules in rules file.

## Domontazh batch
_Downloads\\домонтаж batch (emilyix, mia_tesh, zoey_bee) — VO scripts written 2026-10-22, waiting for models' voice recordings_

2026-10-22: the user asked to edit three folders in `Downloads\домонтаж` where voice-over/greeting was missing.
I wrote English VO scripts (no brand names, OnlyFans mention in the goodbye) in
`OpenMontage\projects\domontazh\` (`emilyix_VO_script.txt` 3 videos × 22–30 lines, `mia_tesh_VO_script.txt` 21 lines,
`zoey_bee_VO_script.txt` 12 lines). The user sends them to the models; the models record voice notes. Edit only after
the recordings arrive.

- emilyix: 51 clips, no speech at all. The user wants AS MANY UNIQUE VIDEOS as possible from one shoot (no shared shots),
  each with its own hello/VO/goodbye → 3 videos, each ≥ 2:00 (only ~7:17 of footage):
  V1 GRWM + taxi + mall + aquarium (8093–8135, ~174 s), V2 3 sweaters pink/cream/red (8137–8174, ~121 s),
  V3 loungewear grey/white/black velour (8183–8210, ~121 s). IMG_8174 has her talking → no VO over it.
  V4 (added at the user's request) "How I Choose Clothes" — 7 tips, REUSES shots from V1–V3 (OK'd); when cutting,
  prefer moments of each clip not used in V1–V3 and a different order so the repeats are less obvious.
- mia_tesh DONE 2026-10-23: `projects/mia-tesh-halloween` (lana-bunny plan_common template, 2:54, covers a/b).
  Her VO = 6 voice notes vo1..vo6 (vo6 starts after she read my stage direction aloud). Her look is a SPIDERWEB
  under the eye, not "tears" (script was wrong) and she says "pure old Halloween" — subs say "tears"/"Hollywood";
  offered a re-record of those two lines.
- emilyix V1 DONE 2026-10-26: `projects/emilyix-grwm-mall` (3:00). She filmed hello/goodbye on camera
  (IMG_8461/8464/8466, 8468/8472/8473) + 19 VO notes in `emilyix\get ready\` (gr01..gr19). Custom beat planner
  (one beat = note(s) + hand-picked shots, trim or slow-mo ≥0.75) + hessakhalifa 10-24 levels renderer with slow-mo
  patched in — reuse both for V2-V4. V2-V4 recordings not received yet.
  NOTE: mia-tesh-halloween was mixed with the OLD −10/−14 levels (before the 10-24 rule) — offered a remix.
- zoey_bee script expanded to 20 lines (~4.5 min of quiet stretches next to ~4.5 min of her own speech).
- mia_tesh: Halloween makeup; intro IMG_6754 + outro IMG_6761 (says OnlyFans) on camera, ~13 min of makeup with no talking (6757/6758), close-ups 6759/6762.
- zoey_bee: Leeloo costume, she talks herself; VO only for the quiet dressing/wig stretches. IMG_1372 = Russian blooper, skip.
  2026-10-23: the same footage came again in `Downloads\монтаж вт\zoey_bee` with "смонтируй" and no recordings →
  edited without VO (`projects/zoey-bee-leeloo`, 5:54, quiet stretches fast-forwarded). If recordings arrive later,
  add them there.
- Tags: @emilyix, @zoey_bee (earlier projects), @mia_tesh assumed from the folder name. No music in the folders → lofi library.

**Why:** a new chat must know the scripts exist and that recordings are what it's waiting for.
**How to apply:** when voice notes arrive, match them to the numbered lines, then follow edit playbook.

## Montazh pnd batch
_Downloads\\монтаж пнд (2026-10-26): daisyyyli mulled wine, lia_life Queen of Hearts, mia (@miapixel) = TWO videos (autumn habits + Saw makeup) — projects *-1026, shared helper scripts_

2026-10-26 batch, folder names = model tags (mia → @miapixel). Four videos:
- `projects/daisyyyli-1026` — Halloween mulled wine (4:08). `Глинтвейн.m4a` = her VO memo (NFD name), not music.
  DaisyTitle + sparkle via `title_style: "daisy"` in the renderer. Doubtful sub: "blue dream" → "bloody rim".
- `projects/lia-life-1026` — Queen of Hearts makeup (2:33). Black portrait IMG_0153..0166 = voice notes.
- `projects/mia-pixel-1026` (autumn habits, mia/1, 3:29) and `mia-pixel-1026b` (Saw makeup, Halloween subfolder, 3:00).
  Mia speaks Russian, VO notes full of retakes/swearing → phrase pass, English hand translation per span.

Renderer for all four = mia-tesh plan_common renderer + Hessa mix levels (compressor, music re-measure, duck).
plan_common now accepts a list of texts per span (cues never straddle a cut retake). Helpers in projects/:
`_sources_1026.py` (sources + blur), `_accurate_words_1026.py` (NFC/NFD-safe), `_vad_1026.py`, `_check_preview_1026.py`.
CoverDaisy got `side` / `size` / `x` props. Mia 4204 14–31 s (top change) excluded for SFW.

**Why:** next chat may get revisions for these four.
**How to apply:** edit the project's plan_timeline.py, re-run plan + render; see edit playbook, daisy style.
