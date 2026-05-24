param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1",
    [switch]$Foreground,
    [int]$HealthTimeoutSeconds = 20
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
    $healthUrl = "http://${HostAddress}:${Port}/healthz"
    try {
        $existing = Invoke-WebRequest -UseBasicParsing $healthUrl -TimeoutSec 2
        if ($existing.StatusCode -eq 200) {
            Write-Host "Servidor web EV3 ya estaba activo: http://${HostAddress}:${Port}/"
            Write-Host "Health: $($existing.StatusCode)"
            exit 0
        }
    } catch {
        throw "El puerto http://${HostAddress}:${Port}/ ya esta en uso por PID(s): $($listenPids -join ', '). Use .\\scripts\\restart_web.cmd o .\\scripts\\stop_web.cmd antes de iniciar."
    }
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

$healthUrl = "http://${HostAddress}:${Port}/healthz"
if ($HealthTimeoutSeconds -lt 3) {
    $HealthTimeoutSeconds = 3
}
$deadline = (Get-Date).AddSeconds($HealthTimeoutSeconds)
$response = $null
$lastError = $null
while ((Get-Date) -lt $deadline) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing $healthUrl -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            break
        }
    } catch {
        $lastError = $_
    }
    Start-Sleep -Milliseconds 500
}
if (-not $response -or $response.StatusCode -ne 200) {
    Write-Host "No se logro validar healthz en ${HealthTimeoutSeconds}s."
    if (Test-Path $ErrLog) {
        Write-Host "--- Ultimas lineas de error ---"
        Get-Content $ErrLog -Tail 40
    }
    if ($lastError) {
        throw "Fallo al iniciar servidor: $($lastError.Exception.Message)"
    }
    throw "Fallo al iniciar servidor: healthz no respondio HTTP 200."
}

Write-Host "Servidor web EV3 iniciado: http://${HostAddress}:${Port}/"
Write-Host "Health: $($response.StatusCode)"
Write-Host "Logs: $OutLog"
Write-Host "Errores: $ErrLog"
