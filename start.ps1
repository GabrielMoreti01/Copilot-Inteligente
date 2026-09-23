$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (Test-Path -LiteralPath '.env') {
    Get-Content -LiteralPath '.env' | ForEach-Object {
        if ($_ -match '^\s*(COPILOTO_[A-Z_]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2].Trim(), 'Process')
        }
    }
}
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) { throw 'Crie o ambiente .venv conforme o README.' }
& .venv/Scripts/python.exe main.py
