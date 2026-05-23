param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1",
    [switch]$Foreground
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$OutLog = "C:\tmp\ev3_web_out.log"
$ErrLog = "C:\tmp\ev3_web_err.log"

if (-not (Test-Path $PythonExe)) {
    throw "No se encontro el interprete virtual: $PythonExe"
}

if (-not (Test-Path "C:\tmp")) {
    New-Item -ItemType Directory -Path "C:\tmp" | Out-Null
}

$env:EV3_WEB_HOST = $HostAddress
$env:EV3_WEB_PORT = "$Port"

$pattern = "${HostAddress}:$Port"
$listenPids = @(
    netstat -ano |
        Select-String $pattern |
        Select-String "LISTENING" |
        ForEach-Object { ($_ -split "\s+")[-1] } |
        Sort-Object -Unique
)
if ($listenPids.Count -gt 0) {
    throw "El puerto http://${HostAddress}:${Port}/ ya esta en uso por PID(s): $($listenPids -join ', '). Use restart_web.cmd o stop_web.cmd antes de iniciar."
}

if ($Foreground) {
    Push-Location $ProjectRoot
    try {
        & $PythonExe -m simulador_ev3.web.waitress_server
    }
    finally {
        Pop-Location
    }
    exit $LASTEXITCODE
}

Start-Process `
    -FilePath $PythonExe `
    -ArgumentList "-m simulador_ev3.web.waitress_server" `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog

Start-Sleep -Seconds 2
$healthUrl = "http://${HostAddress}:${Port}/healthz"
$response = Invoke-WebRequest -UseBasicParsing $healthUrl

Write-Host "Servidor web EV3 iniciado: http://${HostAddress}:${Port}/"
Write-Host "Health: $($response.StatusCode)"
Write-Host "Logs: $OutLog"
Write-Host "Errores: $ErrLog"
