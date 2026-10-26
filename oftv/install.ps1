# OFTV kit installer - run from the repo root:  powershell -ExecutionPolicy Bypass -File oftv/install.ps1
# Safe to re-run: every step skips what is already there.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Step($t) { Write-Host "`n=== $t" -ForegroundColor Cyan }
function Need-Winget($exe, $id) {
    Refresh-Path
    if (Get-Command $exe -ErrorAction SilentlyContinue) { Write-Host "$exe OK"; return }
    Write-Host "installing $id ..."
    winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements
    Refresh-Path
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { throw "$exe still not found after installing $id - restart the PC and run again" }
}

Step "1/6 System tools (winget)"
Need-Winget "git" "Git.Git"
Need-Winget "ffmpeg" "Gyan.FFmpeg"
Need-Winget "node" "OpenJS.NodeJS.LTS"
$py = $null
foreach ($c in @("py -3.11", "python")) {
    try { $v = & cmd /c "$c --version 2>&1"; if ($v -match "3\.11") { $py = $c; break } } catch {}
}
if (-not $py) {
    winget install --id Python.Python.3.11 -e --silent --accept-package-agreements --accept-source-agreements
    Refresh-Path
    $py = "py -3.11"
}
Write-Host "python: $py"

Step "2/6 Python venv"
if (-not (Test-Path ".venv\Scripts\python.exe")) { cmd /c "$py -m venv .venv"; if ($LASTEXITCODE) { throw "venv failed" } }
$vpy = Join-Path $Root ".venv\Scripts\python.exe"
& $vpy -m pip install --upgrade pip --quiet

Step "3/6 Python packages (10-15 min the first time)"
& $vpy -m pip install torch==2.14.1 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cpu --quiet
if ($LASTEXITCODE) { throw "torch install failed" }
& $vpy -m pip install -r oftv\requirements-oftv.txt --quiet
if ($LASTEXITCODE) { throw "pip install failed" }

Step "4/6 Remotion (plates, covers, pop-ups)"
Push-Location remotion-composer
if (-not (Test-Path "node_modules\remotion")) { npm install --no-audit --no-fund; if ($LASTEXITCODE) { Pop-Location; throw "npm install failed" } }
Pop-Location

Step "5/6 AI models: Whisper small / large-v3 / large-v3-turbo, Demucs, rembg, Remotion browser (~6 GB)"
& $vpy -c "from faster_whisper import WhisperModel as W; [W(m, device='cpu', compute_type='int8') for m in ('small', 'large-v3', 'large-v3-turbo')]; print('whisper OK')"
if ($LASTEXITCODE) { throw "whisper download failed (internet?)" }
& $vpy -c "from demucs.pretrained import get_model; get_model('htdemucs'); print('demucs OK')"
& $vpy -c "from rembg import new_session; new_session('isnet-general-use'); print('rembg OK')"
Push-Location remotion-composer
npx remotion browser ensure
Pop-Location

Step "6/6 Check"
& $vpy oftv\tools\doctor.py
