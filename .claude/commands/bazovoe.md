---
description: Базовый монтаж OFTV — одна папка модели или папка-пачка с подпапками по тегам
argument-hint: <папка в Загрузках или путь> [пожелания]
---

Job type: **basic** OFTV edit. Input: `$ARGUMENTS`

1. Read `oftv/PLAYBOOK.md` fully and `oftv/OFTV_RULES.md` (skip if already read in this session).
2. Run `oftv/tools/intake.py` on the folder from the arguments (first word(s) = folder; the rest = wishes). It decides
   one video vs a batch of models. Set `"type": "basic"` in each new `job.json`.
3. Follow the playbook's "Step by step" for every project: quick pass in the background → look → ONE message with
   all questions for the whole batch → accurate pass → plan → render 1440 → QC → cover + texts → deliver.
4. Reply in Russian, short. After each delivered video: where the files are, length, title, doubtful spots.
