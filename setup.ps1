$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Run-Step {
    param(
        [string] $Title,
        [scriptblock] $Command
    )
    Write-Host ''
    Write-Host "==> $Title"
    & $Command
}

function Test-PythonVersion {
    param(
        [string] $Command,
        [string[]] $Arguments = @()
    )
    & $Command @Arguments -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
    return $LASTEXITCODE -eq 0
}

function New-Venv {
    if (Test-Path -LiteralPath '.venv\Scripts\python.exe') {
        Write-Host 'Ambiente .venv ja existe.'
        return
    }

    if (Get-Command py -ErrorAction SilentlyContinue) {
        if (Test-PythonVersion 'py' @('-3.12')) {
            & py -3.12 -m venv .venv
            return
        }
        if (Test-PythonVersion 'py' @('-3.11')) {
            & py -3.11 -m venv .venv
            return
        }
    }

    if ((Get-Command python -ErrorAction SilentlyContinue) -and (Test-PythonVersion 'python')) {
        & python -m venv .venv
        return
    }

    throw 'Python 3.11+ nao encontrado. Instale Python 3.12 ou 3.11 e tente novamente.'
}

Run-Step 'Criando ambiente Python' {
    New-Venv
}

$Python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Nao foi possivel criar .venv. Verifique sua instalacao do Python.'
}

& $Python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) {
    throw 'O .venv usa Python antigo demais. Apague a pasta .venv, instale Python 3.11+ e rode .\setup.ps1 novamente.'
}

Run-Step 'Atualizando pip' {
    & $Python -m pip install --upgrade pip
}

Run-Step 'Instalando dependencias Python' {
    & $Python -m pip install -r requirements.txt
}

Run-Step 'Treinando Random Forest' {
    & $Python -m scripts.train
}

Run-Step 'Instalando dependencias do frontend' {
    Push-Location frontend
    try {
        if (Get-Command pnpm -ErrorAction SilentlyContinue) {
            pnpm install --frozen-lockfile
        } elseif (Get-Command npm -ErrorAction SilentlyContinue) {
            npm install
        } else {
            throw 'pnpm ou npm nao encontrado. Instale Node.js e pnpm.'
        }
    } finally {
        Pop-Location
    }
}

Run-Step 'Gerando build do frontend' {
    Push-Location frontend
    try {
        if (Get-Command pnpm -ErrorAction SilentlyContinue) {
            pnpm build
        } else {
            npm run build
        }
    } finally {
        Pop-Location
    }
}

Write-Host ''
Write-Host 'Tudo pronto.'
Write-Host 'Para iniciar: .\start.ps1'
Write-Host 'Depois abra: http://127.0.0.1:8000'
