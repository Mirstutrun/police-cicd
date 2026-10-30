
param(
    [string]$DeployDir = 'C:\police-app',
    [int]$Port = 5000,
    [string]$Python = 'python'
)

$Source = $PSScriptRoot
Write-Host "== Deploy: $Source -> $DeployDir (port $Port)"


$oldPids = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
           Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $oldPids) {
    if ($p -gt 4) {
        Write-Host "Stopping old app, PID $p"
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
}
for ($i = 0; $i -lt 10; $i++) {
    if (-not (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Seconds 1
}


New-Item -ItemType Directory -Force -Path $DeployDir -ErrorAction Stop | Out-Null

robocopy $Source $DeployDir /MIR /XD .git venv instance logs __pycache__ .pytest_cache /XF *.pyc /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw "robocopy failed, exit code $LASTEXITCODE" }


$venvPython = Join-Path $DeployDir 'venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    & $Python -m venv (Join-Path $DeployDir 'venv')
    if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
}
& $venvPython -m pip install -q --disable-pip-version-check -r (Join-Path $DeployDir 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }


$logDir = Join-Path $DeployDir 'logs'
New-Item -ItemType Directory -Force -Path $logDir -ErrorAction Stop | Out-Null

$env:JENKINS_NODE_COOKIE = 'dontKillMe'
$env:BUILD_ID = 'dontKillMe'
$cmdLine = "venv\Scripts\python.exe -m waitress --host=127.0.0.1 --port=$Port app:app > logs\app.log 2>&1"
$proc = Start-Process -FilePath 'cmd.exe' -ArgumentList "/c $cmdLine" `
                      -WorkingDirectory $DeployDir -WindowStyle Hidden -PassThru -ErrorAction Stop


$url = "http://127.0.0.1:$Port/"
$ok = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1
    if ($proc.HasExited) { break }
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch { }
}

if (-not $ok) {
    Write-Host "App did not start. Log ($logDir\app.log):"
    Get-Content (Join-Path $logDir 'app.log') -ErrorAction SilentlyContinue | Write-Host
    exit 1
}

Write-Host "App is running: http://localhost:$Port/"
exit 0