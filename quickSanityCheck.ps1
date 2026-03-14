$ErrorActionPreference = "Stop"

function Add-Result {
    param(
        [System.Collections.Generic.List[object]]$Results,
        [string]$Name,
        [bool]$Passed,
        [string]$Details
    )

    $Results.Add([PSCustomObject]@{
            Check   = $Name
            Status  = if ($Passed) { "PASS" } else { "FAIL" }
            Passed  = $Passed
            Details = $Details
        }) | Out-Null
}

function Test-HttpEndpoint {
    param(
        [string]$Name,
        [string]$Url,
        [int]$ExpectedStatus = 200,
        [string]$MustContain
    )

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 10
        $ok = ($response.StatusCode -eq $ExpectedStatus)

        if ($ok -and $MustContain) {
            if ($response.Content -is [byte[]]) {
                $content = [System.Text.Encoding]::UTF8.GetString([byte[]]$response.Content)
            }
            else {
                $content = [string]$response.Content
            }

            $ok = $content -match [Regex]::Escape($MustContain)
            if ($ok) {
                return @{ Passed = $true; Details = "HTTP $($response.StatusCode) + conteúdo OK" }
            }

            return @{ Passed = $false; Details = "HTTP $($response.StatusCode), mas conteúdo esperado não encontrado: $MustContain" }
        }

        if ($ok) {
            return @{ Passed = $true; Details = "HTTP $($response.StatusCode)" }
        }

        return @{ Passed = $false; Details = "HTTP $($response.StatusCode), esperado $ExpectedStatus" }
    }
    catch {
        return @{ Passed = $false; Details = $_.Exception.Message }
    }
}

$results = New-Object System.Collections.Generic.List[object]

$health = Test-HttpEndpoint -Name "Backend Health" -Url "http://127.0.0.1:8000/v1/health/"
Add-Result -Results $results -Name "Backend Health" -Passed $health.Passed -Details $health.Details

$swagger = Test-HttpEndpoint -Name "Swagger UI" -Url "http://127.0.0.1:8000/swagger/"
Add-Result -Results $results -Name "Swagger UI" -Passed $swagger.Passed -Details $swagger.Details

$schema = Test-HttpEndpoint -Name "Schema JSON" -Url "http://127.0.0.1:8000/api/schema.json" -MustContain "/v1/projects/{project_id}/rules"
Add-Result -Results $results -Name "Schema JSON" -Passed $schema.Passed -Details $schema.Details

$frontend = Test-HttpEndpoint -Name "Frontend" -Url "http://localhost:3000"
Add-Result -Results $results -Name "Frontend" -Passed $frontend.Passed -Details $frontend.Details

try {
    $celeryProcesses = Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -match "python|py" -and
            $_.CommandLine -and
            $_.CommandLine -match "celery" -and
            $_.CommandLine -match "worker"
        }

    $celeryOk = $null -ne $celeryProcesses -and $celeryProcesses.Count -gt 0
    if ($celeryOk) {
        Add-Result -Results $results -Name "Celery Worker" -Passed $true -Details "Processo worker encontrado"
    }
    else {
        Add-Result -Results $results -Name "Celery Worker" -Passed $false -Details "Nenhum processo celery worker ativo encontrado"
    }
}
catch {
    Add-Result -Results $results -Name "Celery Worker" -Passed $false -Details $_.Exception.Message
}

Write-Host ""
Write-Host "=== QUICK SANITY CHECK ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize

$failed = ($results | Where-Object { -not $_.Passed }).Count
if ($failed -gt 0) {
    Write-Host ""
    Write-Host "Resultado final: FAIL ($failed falhas)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Resultado final: PASS (ambiente saudável)" -ForegroundColor Green
exit 0
