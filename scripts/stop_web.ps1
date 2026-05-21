param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$pattern = "${HostAddress}:$Port"
$listenPids = @(
    netstat -ano |
        Select-String $pattern |
        Select-String "LISTENING" |
        ForEach-Object { ($_ -split "\s+")[-1] } |
        Sort-Object -Unique
)

if (-not $listenPids -or $listenPids.Count -eq 0) {
    Write-Host "No hay servidor escuchando en http://${HostAddress}:${Port}/"
    exit 0
}

foreach ($procId in $listenPids) {
    Stop-Process -Id ([int]$procId) -Force
    Write-Host "Proceso detenido: $procId"
}

Write-Host "Servidor web EV3 detenido en http://${HostAddress}:${Port}/"
