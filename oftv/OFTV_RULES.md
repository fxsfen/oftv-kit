# OFTV submission rules (mandatory for every OFTV edit)

Check every video against this list before sending a final. Rules as given by the user (2026-10-19):

- Please shoot and export videos in the highest resolution possible for your device. Videos must be submitted in at
  least 1080p, but 4k is preferred.
- Videos must be shot horizontally (landscape) in standard widescreen format (16:9 aspect ratio). This is the standard
  size for most TVs, computer monitors, and online video players. We cannot accept videos shot vertically.
- Videos must be at least 2 minutes (2:00) long. OFTV does not have an upper limit on length, but video files cannot
  be more than 25 GB in size.
- Videos must have a clear beginning, middle, and end. Your video should tell a story, teach a lesson, or show a
  performance.
- Videos with significant camera or audio issues may be declined. Be mindful of good lighting so that your video isn't
  over- or under-exposed. Please standardize audio levels across your video so that no part is too loud or too soft.
  Audio levels should generally range between -16 to -6 decibels throughout your video. Please ensure that any
  background music is not louder than the dialogue.
- Take care not to compress or reduce the quality of your video file when exporting.
- Videos cannot contain copyrighted music.
- Videos with an advertisement or excessive product placement may be declined.
- If you feature a guest in your video, please be sure that you have their permission to record and post. Minors under
  the age of 18 cannot be featured in any OFTV video.
- Videos must be SFW, meaning there cannot be any nudity, implied nudity, or sexually explicit content.
- OFTV is exclusively for OnlyFans creators, so you must have an OnlyFans account to be featured on OFTV. The OnlyFans
  account associated with your OFTV channel must meet the same SFW standards, meaning the account does not contain
  nudity or explicit content.

## How we meet them (checklist before sending a final)

| Rule | What we do / check |
|---|---|
| ≥ 1080p, 4K preferred | Final 2560×1440 (user re-exports via CapCut); never upscale blurry sources without saying so |
| 16:9 landscape | Output always 16:9; crops keep 16:9 and stay ≥ 2560×1440 of real source pixels |
| ≥ 2:00, ≤ 25 GB | `qa.py` duration + file size |
| Beginning / middle / end | Intro (greeting + what's coming) → sections → closing / goodbye |
| Even audio, −16…−6 dB, music below voice | Per-line speech trims + voice compressor; 100 ms block peaks in the final mix: dialogue median ≈ −9 dBFS with p10 ≥ −12.5 (ceiling −6), music median ≈ −15.5 dBFS (ceiling −12, mild duck under voice), SFX ≈ −12 never above voice; true peak ≤ −1 dBFS. Default since 2026-10-24 (see both feedbacks below) |
| No quality loss on export | H.264 high CRF 14–16, AAC 320k, 30 fps CFR, bt709 SDR |
| No copyrighted music | Only the tracks the user supplies; never add other music without asking |
| No ads / excessive product placement | Cut brand-name plugs and product lists (e.g. power-station brands) and say so in the report |
| Guests / minors | Flag any other person on camera; never use footage with minors |
| SFW | Flag anything borderline; never include nudity / implied nudity |
| Cover, title, description | No OFTV / OnlyFans mentions; title ≤ 40 chars, description ≤ 700 chars, English |

See also `OFTV_EDIT_PLAYBOOK.md` (workflow) and the remix template `projects/oftv-remix-1017/scripts/`.

## OFTV reviewer feedback (2026-10-19, video `Downloads/112.mp4`) — music was rejected as too quiet

> "The background music in your video is too quiet in comparison to your dialogue.
> Suggested Mix Levels: Dialogue: −12 dB to −6 dB. Music: −16 dB to −10 dB."

These are **meter (peak) readings of each element in the final mix**: dialogue peaks should sit between −12 and
−6 dBFS, music peaks between −16 and −10 dBFS — i.e. music only ~4–6 dB under the voice, not ~10 LU under it.
The old recipe (music −14 LUFS → −16 dB ≈ −30 LUFS) is too quiet for OFTV. Check both stems with
`projects/112-audio-fix/scripts/fix_mix.py` style measurements (100 ms block peaks, p10–p95) before sending.

## OFTV reviewer feedback (2026-10-24, `projects/hessakhalifa-oftv`) — music rejected as too LOUD

> "The background music in your video is too loud in comparison to your dialogue.
> Suggested Mix Levels: Dialogue: −12 dB to −6 dB. Music: −16 dB to −10 dB."

That mix had voice median −10 / music median −14 / music p95 −10, but quiet words fell to −19 dB (p10) under the music.
Fix (now default): voice compressed and set to median −9 (−12.5…−6), music median −15.5 with ceiling −12 and a mild
duck under the voice — ≈ 6.5 dB between the stems. See `projects/hessakhalifa-oftv/scripts/render_timeline.py`.
