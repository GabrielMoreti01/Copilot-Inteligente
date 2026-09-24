$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$Python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$Model = Join-Path $PSScriptRoot 'models\decision.joblib'
$Frontend = Join-Path $PSScriptRoot 'frontend\dist\index.html'

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Ambiente Python nao encontrado. Rode primeiro: .\setup.ps1"
}

if (-not (Test-Path -LiteralPath $Model)) {
    throw "Modelo Random Forest nao encontrado. Rode primeiro: .\.venv\Scripts\python.exe -m scripts.train"
}

if (-not (Test-Path -LiteralPath $Frontend)) {
    throw "Build do frontend nao encontrado. Rode primeiro: cd frontend; pnpm build; cd .."
}

if (Test-Path -LiteralPath '.env') {
    Get-Content -LiteralPath '.env' | ForEach-Object {
        if ($_ -match '^\s*(COPILOTO_[A-Z_]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2].Trim(), 'Process')
        }
    }
}

Write-Host ''
Write-Host 'Rota Viva iniciado em http://127.0.0.1:8000'
Write-Host 'Pressione Ctrl+C para encerrar.'
Write-Host ''

& $Python main.py
