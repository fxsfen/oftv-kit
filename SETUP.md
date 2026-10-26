# Setup — OFTV editing kit (read this if a user asked you to install this repo)

The user is a video editor, not technical, and writes in Russian. They pasted the link to this repo and want
everything installed. Do it all yourself, answer in Russian, 1–2 short lines per step, no technical detail unless
something fails. Don't ask them to run commands or choose options.

1. If the repo isn't cloned yet: install git if missing (`winget install --id Git.Git -e --silent
   --accept-package-agreements --accept-source-agreements`), then clone the link EXACTLY as given (it carries a
   read-only access key — never print it back, never change the remote) into `%USERPROFILE%\OpenMontage`.
2. In the clone run `powershell -ExecutionPolicy Bypass -File oftv/install.ps1` in the background (15–40 min:
   Python, FFmpeg, Node, packages, AI models). Report progress in plain words. Windows may ask "Allow changes?" —
   tell them to press «Да». If a step fails, read the error, fix it, re-run (the script skips finished steps).
3. Run `.venv\Scripts\python.exe oftv\tools\doctor.py`. Fix every FAIL. WARN lines are fine — skip them.
4. Copy `oftv/claude-settings.json` to `.claude/settings.json` if that file doesn't exist (team permissions so
   editing commands don't ask for approval each time). If you aren't allowed to, tell them in one line to copy it.
5. Switch this session to the clone folder if you can (e.g. a change-directory tool); otherwise tell them:
   «Открой в Claude папку OpenMontage (в твоей домашней папке) и работай в ней».
6. Finish with the short guide from `oftv/README.md` section «Каждый день: монтаж» (the command table and where
   finished videos appear). Nothing else.
