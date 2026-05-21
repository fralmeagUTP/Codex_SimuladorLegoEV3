param(
    [int]$Port = 5050,
    [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$BaseUrl = "http://${HostAddress}:${Port}"

function Assert-StatusOk {
    param(
        [string]$Path,
        [string]$ExpectedContent = ""
    )

    $url = "$BaseUrl$Path"
    $response = Invoke-WebRequest -UseBasicParsing $url
    if ($response.StatusCode -ne 200) {
        throw "GET $Path retorno HTTP $($response.StatusCode)"
    }
    if ($ExpectedContent -and -not $response.Content.Contains($ExpectedContent)) {
        throw "GET $Path no contiene: $ExpectedContent"
    }
    Write-Host "OK GET $Path"
    return $response
}

Write-Host "Smoke test EV3 Web: $BaseUrl"

$health = Assert-StatusOk -Path "/healthz" -ExpectedContent '"status":"ok"'
Assert-StatusOk -Path "/" -ExpectedContent "simulation_app.js" | Out-Null
Assert-StatusOk -Path "/worlds" -ExpectedContent "world_editor_app.js" | Out-Null
Assert-StatusOk -Path "/help" -ExpectedContent "Ayuda" | Out-Null
Assert-StatusOk -Path "/static/js/api.js" -ExpectedContent "window.EV3Api" | Out-Null
Assert-StatusOk -Path "/static/js/simulation_app.js" -ExpectedContent "loadWorldFromUrl" | Out-Null
Assert-StatusOk -Path "/static/js/world_editor_app.js" -ExpectedContent "simulateSavedWorldLink" | Out-Null
Assert-StatusOk -Path "/static/css/app.css" -ExpectedContent "world-editor-workspace" | Out-Null

$sessionResponse = Invoke-WebRequest `
    -UseBasicParsing `
    -Method POST `
    -Uri "$BaseUrl/api/sessions" `
    -ContentType "application/json" `
    -Body "{}"

if ($sessionResponse.StatusCode -ne 201) {
    throw "POST /api/sessions retorno HTTP $($sessionResponse.StatusCode)"
}

$session = $sessionResponse.Content | ConvertFrom-Json
if (-not $session.session_id -or -not $session.owner_token) {
    throw "POST /api/sessions no retorno session_id y owner_token"
}
Write-Host "OK POST /api/sessions"

$headers = @{ "X-Session-Token" = $session.owner_token }
$snapshotResponse = Invoke-WebRequest `
    -UseBasicParsing `
    -Uri "$BaseUrl/api/sessions/$($session.session_id)/snapshot" `
    -Headers $headers

if ($snapshotResponse.StatusCode -ne 200) {
    throw "GET /api/sessions/<id>/snapshot retorno HTTP $($snapshotResponse.StatusCode)"
}
Write-Host "OK GET /api/sessions/<id>/snapshot"

$breakpointsResponse = Invoke-WebRequest `
    -UseBasicParsing `
    -Method POST `
    -Uri "$BaseUrl/api/sessions/$($session.session_id)/debug/breakpoints" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body '{"breakpoints":[2]}'

if ($breakpointsResponse.StatusCode -ne 200) {
    throw "POST /api/sessions/<id>/debug/breakpoints retorno HTTP $($breakpointsResponse.StatusCode)"
}
Write-Host "OK POST /api/sessions/<id>/debug/breakpoints"

$stepResponse = Invoke-WebRequest `
    -UseBasicParsing `
    -Method POST `
    -Uri "$BaseUrl/api/sessions/$($session.session_id)/debug/step" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body "{}"

if ($stepResponse.StatusCode -ne 200) {
    throw "POST /api/sessions/<id>/debug/step retorno HTTP $($stepResponse.StatusCode)"
}
Write-Host "OK POST /api/sessions/<id>/debug/step"

$continueResponse = Invoke-WebRequest `
    -UseBasicParsing `
    -Method POST `
    -Uri "$BaseUrl/api/sessions/$($session.session_id)/debug/continue" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body "{}"

if ($continueResponse.StatusCode -ne 200) {
    throw "POST /api/sessions/<id>/debug/continue retorno HTTP $($continueResponse.StatusCode)"
}
Write-Host "OK POST /api/sessions/<id>/debug/continue"

Invoke-WebRequest `
    -UseBasicParsing `
    -Method DELETE `
    -Uri "$BaseUrl/api/sessions/$($session.session_id)" `
    -Headers $headers | Out-Null
Write-Host "OK DELETE /api/sessions/<id>"

Write-Host "Smoke test completado correctamente."
