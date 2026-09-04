param(
    [string]$PythonExe = "python",
    [string]$BuildRoot = "build",
    [string]$DistRoot = "dist",
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SpecPath = Join-Path $ProjectRoot "SimuladorEV3.spec"
$BuildPath = if ([System.IO.Path]::IsPathRooted($BuildRoot)) { $BuildRoot } else { Join-Path $ProjectRoot $BuildRoot }
$DistPath = if ([System.IO.Path]::IsPathRooted($DistRoot)) { $DistRoot } else { Join-Path $ProjectRoot $DistRoot }

Set-Location $ProjectRoot
if (-not (Test-Path $SpecPath)) {
    throw "No se encontró la especificación de PyInstaller: $SpecPath"
}

Write-Host "[1/4] Limpiando artefactos previos..."
if (Test-Path -LiteralPath $BuildPath) { Remove-Item -Recurse -Force -LiteralPath $BuildPath }
if (Test-Path -LiteralPath $DistPath) { Remove-Item -Recurse -Force -LiteralPath $DistPath }

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
    --workpath $BuildPath `
    --distpath $DistPath `
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
$targetDocs = Join-Path (Join-Path $DistPath "SimuladorEV3") "Documentos"
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

$appDir = Join-Path $DistPath "SimuladorEV3"
$zipPath = Join-Path $DistPath "SimuladorEV3-1.5.0-Windows-x64.zip"
if (Test-Path -LiteralPath $zipPath) { Remove-Item -Force -LiteralPath $zipPath }
# ``tar`` devuelve un codigo de error fiable si un archivo queda bloqueado;
# Compress-Archive puede producir un ZIP parcial y aun continuar el script.
& tar -a -c -f $zipPath -C $DistPath "SimuladorEV3"
if ($LASTEXITCODE -ne 0) { throw "La creacion del ZIP fallo con codigo $LASTEXITCODE." }
$zipEntries = & tar -tf $zipPath
if ($LASTEXITCODE -ne 0 -or $zipEntries -notcontains "SimuladorEV3/SimuladorEV3.exe") {
    throw "El ZIP generado no contiene SimuladorEV3.exe."
}

if (-not $SkipInstaller) {
    $isccCandidates = @(
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )
    $iscc = $isccCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if ($null -eq $iscc) {
        throw "Inno Setup 6 no esta instalado. Instale JRSoftware.InnoSetup o use -SkipInstaller."
    }
    & $iscc (Join-Path $ProjectRoot "scripts\installer\SimuladorEV3.iss")
    if ($LASTEXITCODE -ne 0) { throw "La compilacion del instalador fallo con codigo $LASTEXITCODE." }
}

Write-Host "Ejecutable: $(Join-Path $appDir 'SimuladorEV3.exe')"
Write-Host "Paquete portable: $zipPath"
if (-not $SkipInstaller) {
    Write-Host "Instalador: $(Join-Path $DistPath 'installer\Setup-SimuladorEV3-1.5.0-Windows-x64.exe')"
}
