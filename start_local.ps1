param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1",
    [switch]$Foreground,
    [switch]$Background,
    [int]$HealthTimeoutSeconds = 20
)

$ErrorActionPreference = "Stop"

if (-not $Foreground -and -not $Background) {
    $Foreground = $true
}

& (Join-Path $PSScriptRoot "scripts\start_web.ps1") `
    -Port $Port `
    -HostAddress $HostAddress `
    -HealthTimeoutSeconds $HealthTimeoutSeconds `
    -Foreground:$Foreground
