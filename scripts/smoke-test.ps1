param(
    [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"

function Show-DockerLogs {
    Write-Host "Docker smoke verification failed. Recent logs:"
    docker compose logs
}

try {
    docker compose build
    docker compose up -d

    $ready = $false
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        try {
            Invoke-WebRequest -Uri "$BaseUrl/healthz" -UseBasicParsing -TimeoutSec 2 | Out-Null
            $ready = $true
            break
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    if (-not $ready) {
        Show-DockerLogs
        throw "Timed out waiting for /healthz"
    }

    Invoke-WebRequest -Uri "$BaseUrl/healthz" -UseBasicParsing -TimeoutSec 5 | Out-Null
    Invoke-WebRequest -Uri "$BaseUrl/login" -UseBasicParsing -TimeoutSec 5 | Out-Null
    Invoke-WebRequest -Uri "$BaseUrl/register" -UseBasicParsing -TimeoutSec 5 | Out-Null

    try {
        $dashboard = Invoke-WebRequest -Uri "$BaseUrl/dashboard" -UseBasicParsing -MaximumRedirection 0
        $dashboardStatus = $dashboard.StatusCode
    }
    catch {
        $dashboardStatus = $_.Exception.Response.StatusCode.value__
    }

    if ($dashboardStatus -ne 303 -and $dashboardStatus -ne 302) {
        throw "Expected /dashboard to redirect unauthenticated users"
    }

    docker compose ps
    docker compose logs
}
catch {
    Show-DockerLogs
    throw
}
finally {
    docker compose down
}
