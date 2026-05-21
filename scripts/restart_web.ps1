param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "stop_web.ps1") -Port $Port -HostAddress $HostAddress
Start-Sleep -Seconds 1
& (Join-Path $PSScriptRoot "start_web.ps1") -Port $Port -HostAddress $HostAddress
