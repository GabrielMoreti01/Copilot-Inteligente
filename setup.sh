#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

step() {
  printf '\n==> %s\n' "$1"
}

python_in_venv() {
  if [ -x ".venv/Scripts/python.exe" ]; then
    printf '%s\n' ".venv/Scripts/python.exe"
  elif [ -x ".venv/bin/python" ]; then
    printf '%s\n' ".venv/bin/python"
  else
    return 1
  fi
}

valid_python() {
  "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1
}

step "Criando ambiente Python"
if ! python_in_venv >/dev/null 2>&1; then
  if command -v python3.12 >/dev/null 2>&1 && valid_python python3.12; then
    python3.12 -m venv .venv
  elif command -v python3.11 >/dev/null 2>&1 && valid_python python3.11; then
    python3.11 -m venv .venv
  elif command -v python3 >/dev/null 2>&1 && valid_python python3; then
    python3 -m venv .venv
  elif command -v python >/dev/null 2>&1 && valid_python python; then
    python -m venv .venv
  else
    echo "Python 3.11+ nao encontrado. Instale Python 3.12 ou 3.11 e tente novamente." >&2
    exit 1
  fi
else
  echo "Ambiente .venv ja existe."
fi

PYTHON="$(python_in_venv)"
if ! "$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
  echo "O .venv usa Python antigo demais. Apague a pasta .venv, instale Python 3.11+ e rode bash setup.sh novamente." >&2
  exit 1
fi

step "Atualizando pip"
"$PYTHON" -m pip install --upgrade pip

step "Instalando dependencias Python"
"$PYTHON" -m pip install -r requirements.txt

step "Treinando Random Forest"
"$PYTHON" -m scripts.train

step "Instalando dependencias do frontend"
cd frontend
if command -v pnpm >/dev/null 2>&1; then
  pnpm install --frozen-lockfile
elif command -v npm >/dev/null 2>&1; then
  npm install
else
  echo "pnpm ou npm nao encontrado. Instale Node.js e pnpm." >&2
  exit 1
fi

step "Gerando build do frontend"
if command -v pnpm >/dev/null 2>&1; then
  pnpm build
else
  npm run build
fi
cd ..

printf '\nTudo pronto.\n'
printf 'Para iniciar: bash start.sh\n'
printf 'Depois abra: http://127.0.0.1:8000\n'
