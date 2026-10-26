---
description: Обновить kit — забрать новые правила и шаблоны от команды
---

Sync the OFTV kit with the team repository.

1. `git status --short` — local changes to `oftv/PLAYBOOK.md` (new lessons) or other kit files?
2. If there are local kit changes: commit them (`oftv: lessons from <user> <date>` + attribution) and
   `git pull --rebase`, then `git push`. If the push is refused (no write access), keep the commit and tell the user
   to send the new lesson text to the lead editor.
3. If there are none: `git pull --rebase`.
4. Never touch `projects/` (not in git). Summarize in Russian what came in (new lessons / changed templates) in
   2–4 lines, from `git log --oneline` of the pulled range.
