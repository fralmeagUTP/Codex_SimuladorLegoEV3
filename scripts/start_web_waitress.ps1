param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1",
    [int]$Threads = 8,
    [switch]$Foreground
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$OutLog = "C:\tmp\ev3_web_waitress_out.log"
$ErrLog = "C:\tmp\ev3_web_waitress_err.log"

if (-not (Test-Path $PythonExe)) {
    throw "No se encontro el interprete virtual: $PythonExe"
}

if (-not (Test-Path "C:\tmp")) {
    New-Item -ItemType Directory -Path "C:\tmp" | Out-Null
}

$env:EV3_WEB_HOST = $HostAddress
$env:EV3_WEB_PORT = "$Port"
$env:EV3_WEB_THREADS = "$Threads"

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

Write-Host "Servidor web EV3 con Waitress iniciado: http://${HostAddress}:${Port}/"
Write-Host "Health: $($response.StatusCode)"
Write-Host "Logs: $OutLog"
Write-Host "Errores: $ErrLog"
