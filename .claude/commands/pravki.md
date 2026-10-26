---
description: Правки готового видео по фидбеку OFTV или модели
argument-hint: <модель/проект> <что не так — текст фидбека>
---

Job type: **fix** of an already edited video. Input: `$ARGUMENTS`

1. Read `oftv/PLAYBOOK.md` (skip if already read in this session).
2. Find the project: match the first word against `projects/*/job.json` tags and project names (newest first).
   If several match or none, list the candidates in one short question. If the project is not on this PC
   (edited by someone else), ask for the source folder and run a fresh intake with the feedback as wishes.
3. Read its plan (`scripts/plan_timeline.py` or `artifacts/edit_map.json` for a remix), `job.json` and the feedback.
   Change only what the feedback asks (audio levels → OFTV_RULES targets; a bad shot → replace it; a subtitle →
   `word_edits` / cue text). Delete stale `work_*` intermediates the change affects (playbook gotchas), re-render 1440.
4. QC the changed spots plus the full checklist, deliver with `oftv/tools/deliver.py`.
5. If the feedback is a general rule (e.g. "music too loud"), add it to **Lessons from past jobs** in
   `oftv/PLAYBOOK.md` with the date. Reply in Russian: what changed, where the new files are.
