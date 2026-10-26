---
description: Установка и проверка всего, что нужно для монтажа OFTV на этом ПК
---

Set up this PC for OFTV editing. The user is not technical: do everything yourself, explain in Russian in 1–2 lines
per step, ask only when Windows needs them to click "Yes" (UAC) or when something can't be fixed.

1. Run `powershell -ExecutionPolicy Bypass -File oftv/install.ps1` (installs Python 3.11, FFmpeg, Node.js LTS via
   winget if missing, creates `.venv`, installs Python packages, `npm install` in `remotion-composer`, downloads the
   Whisper models). It is safe to re-run. It can take 15–30 min — run it in the background and report progress.
2. Run `.venv\Scripts\python.exe oftv/tools/doctor.py`. Fix every FAIL (re-run the failed part of install.ps1,
   PATH refresh, etc.). WARN lines: explain in plain words (e.g. no Quick Sync = renders slower, fine).
3. If `music_library/lofi` is empty, tell them the lead editor must share the lofi archive (see `oftv/README.md`).
4. Say «Готово, можно монтировать: /bazovoe <папка>» with the 3 commands from `oftv/README.md`.
