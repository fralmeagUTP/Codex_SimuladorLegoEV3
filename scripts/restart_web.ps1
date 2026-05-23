param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "stop_web.ps1") -Port $Port -HostAddress $HostAddress
for ($attempt = 0; $attempt -lt 20; $attempt += 1) {
    Start-Sleep -Milliseconds 250
    $pattern = "${HostAddress}:$Port"
    $listenPids = @(
        netstat -ano |
            Select-String $pattern |
            Select-String "LISTENING" |
            ForEach-Object { ($_ -split "\s+")[-1] } |
            Sort-Object -Unique
    )
    if ($listenPids.Count -eq 0) {
        break
    }
    if ($attempt -eq 19) {
        throw "No se pudo liberar http://${HostAddress}:${Port}/. PID(s) activos: $($listenPids -join ', ')"
    }
}
& (Join-Path $PSScriptRoot "start_web.ps1") -Port $Port -HostAddress $HostAddress
