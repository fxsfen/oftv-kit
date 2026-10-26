---
description: Перемонтаж — объединить два похожих видео в одно новое (одна папка или пачка)
argument-hint: <папка в Загрузках или путь> [пожелания]
---

Job type: **remix** — two similar source videos of one model → ONE restructured OFTV video. Input: `$ARGUMENTS`

1. Read `oftv/PLAYBOOK.md` fully (especially "Remix (two videos → one)" and the lesson "Two video remix") and
   `oftv/OFTV_RULES.md` (skip if already read in this session).
2. Run `oftv/tools/intake.py` on the folder (one model = one folder with the two videos + optional music; a batch =
   one sub-folder per model). Set `"type": "remix"` in each new `job.json`. If a folder holds more or fewer than two
   main videos, ask.
3. Scripts: copy `oftv/templates_remix/*.py` into the project's `scripts/` (keep existing files) and follow the
   remix steps: Demucs `separate.py` BEFORE Whisper → `transcribe.py` on the vocal stems → scan for burned subs /
   tags / flash frames (`scan_burned.py`) → write `artifacts/edit_map.json` (see `edit_map_example.json`:
   sources A/B, music, tag, segments interleaving A and B sentence by sentence, removed, sub_edits) →
   `render_remix.py --res 1440` → `check_joins.py` + `qa.py` → cover + texts → `oftv/tools/deliver.py`.
4. Never invent words; cut repeats and filler; original music is replaced (folder track or lofi); tag plate at the
   start + on the OnlyFans word; subtitles one line, uppercase.
5. Reply in Russian, short: where the files are, length, what was cut, doubtful spots.
