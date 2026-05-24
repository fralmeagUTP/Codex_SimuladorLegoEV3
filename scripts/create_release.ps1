param(
    [Parameter(Mandatory = $true)]
    [string]$Tag,

    [string]$Repo = "fralmeagUTP/Codex_SimuladorLegoEV3",

    [string]$Title = "",

    [string]$NotesFile = "",

    [switch]$Draft,

    [switch]$Prerelease,

    [switch]$PushTag,

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..")

Push-Location $repoRoot
try {
    Write-Host "[1/6] Verificando herramientas..."
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "No se encontro GitHub CLI (gh) en PATH. Instala gh y vuelve a intentar."
    }
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "No se encontro git en PATH."
    }

    Write-Host "[2/6] Resolviendo parametros..."
    if ([string]::IsNullOrWhiteSpace($Title)) {
        $Title = "v$Tag"
    }
    if ([string]::IsNullOrWhiteSpace($NotesFile)) {
        $NotesFile = Join-Path "Documentos" ("RELEASE_NOTES_v{0}.md" -f $Tag)
    }

    if (-not (Test-Path $NotesFile)) {
        throw "No existe el archivo de notas: $NotesFile"
    }

    Write-Host "[3/6] Validando tag local..."
    $localTag = (& git tag --list $Tag).Trim()
    if ([string]::IsNullOrWhiteSpace($localTag)) {
        throw "El tag local '$Tag' no existe. Crea el tag antes de publicar el release."
    }

    if ($PushTag) {
        Write-Host "[4/6] Publicando tag al remoto..."
        & git push origin $Tag
    } else {
        Write-Host "[4/6] Omitiendo push de tag (usa -PushTag si lo necesitas)..."
    }

    Write-Host "[5/6] Verificando si el release ya existe..."
    & gh release view $Tag --repo $Repo *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "El release '$Tag' ya existe en GitHub."
        exit 0
    }

    $releaseArgs = @(
        "release", "create", $Tag,
        "--repo", $Repo,
        "--title", $Title,
        "--notes-file", $NotesFile
    )

    if ($Draft) {
        $releaseArgs += "--draft"
    }
    if ($Prerelease) {
        $releaseArgs += "--prerelease"
    }

    if ($DryRun) {
        Write-Host "[6/6] Dry run activado. Comando a ejecutar:"
        Write-Host ("gh " + ($releaseArgs -join " "))
        exit 0
    }

    Write-Host "[6/6] Creando release en GitHub..."
    & gh @releaseArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Fallo al crear el release en GitHub."
    }

    Write-Host "Release creado correctamente: $Tag"
}
finally {
    Pop-Location
}
