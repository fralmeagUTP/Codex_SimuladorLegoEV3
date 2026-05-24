param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "scripts\restart_web.ps1") `
    -Port $Port `
    -HostAddress $HostAddress
