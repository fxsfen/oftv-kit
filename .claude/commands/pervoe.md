---
description: Первое видео модели — монтаж шоу-уровня с поп-апами (одна папка или пачка)
argument-hint: <папка в Загрузках или путь> [пожелания]
---

Job type: **first** — the model's first video on her OFTV channel. Input: `$ARGUMENTS`

1. Read `oftv/PLAYBOOK.md` fully and `oftv/OFTV_RULES.md` (skip if already read in this session). Pay extra
   attention to the lessons "Show graphics", "Collab popups", "Strict qc", "Cover rules".
2. Run `oftv/tools/intake.py` on the folder; set `"type": "first"` in each new `job.json`.
3. Everything from the basic edit, plus: a title card at the start, semantic pop-ups from
   `remotion-composer/src/oftv/ShowGraphics.tsx` (or the Halloween set when it fits) anchored to what she says,
   placed off her face (`oftv/reference/vitya-oftv-1/place_graphics.py`), 2 strong covers. Confirm the tag
   spelling with the editor — a new model has no history.
4. Strict QC: per-item review sheet, no lean-to-lens shots, no doubled words, sharp b-roll, end on her wave.
5. Reply in Russian, short; deliver with `oftv/tools/deliver.py`.
