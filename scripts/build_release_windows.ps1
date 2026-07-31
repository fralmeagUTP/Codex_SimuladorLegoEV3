param(
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SpecPath = Join-Path $ProjectRoot "SimuladorEV3.spec"

Set-Location $ProjectRoot
if (-not (Test-Path $SpecPath)) {
    throw "No se encontró la especificación de PyInstaller: $SpecPath"
}

Write-Host "[1/4] Limpiando artefactos previos..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

Write-Host "[2/4] Verificando PyInstaller..."
& $PythonExe -m pip show pyinstaller | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller no encontrado. Instalando..."
    & $PythonExe -m pip install pyinstaller
}

Write-Host "[3/4] Construyendo ejecutable..."
& $PythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    $SpecPath

function Get-FirstExistingPath {
    param([string[]]$Candidates)
    foreach ($candidate in $Candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }
    return $null
}

Write-Host "[4/4] Copiando recursos estandarizados..."
$targetDocs = Join-Path "dist\SimuladorEV3" "Documentos"
New-Item -ItemType Directory -Path $targetDocs -Force | Out-Null

$examplesSource = Get-FirstExistingPath @("examples", "Documentos\Ejemplos")
$worldsSource = Get-FirstExistingPath @("worlds", "Documentos\Mundos")

if ($null -eq $examplesSource) {
    throw "No se encontro carpeta de ejemplos (examples o Documentos\Ejemplos)."
}
if ($null -eq $worldsSource) {
    throw "No se encontro carpeta de mundos (worlds o Documentos\Mundos)."
}

Copy-Item -Recurse -Force $examplesSource (Join-Path $targetDocs "Ejemplos")
Copy-Item -Recurse -Force $worldsSource (Join-Path $targetDocs "Mundos")

Write-Host "Release lista en dist\SimuladorEV3\SimuladorEV3.exe"
