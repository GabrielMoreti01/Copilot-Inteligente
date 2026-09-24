#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -x ".venv/Scripts/python.exe" ]; then
  PYTHON=".venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  echo "Ambiente Python nao encontrado. Rode primeiro: bash setup.sh" >&2
  exit 1
fi

if [ ! -f "models/decision.joblib" ]; then
  echo "Modelo Random Forest nao encontrado. Rode primeiro: $PYTHON -m scripts.train" >&2
  exit 1
fi

if [ ! -f "frontend/dist/index.html" ]; then
  echo "Build do frontend nao encontrado. Rode primeiro: cd frontend && pnpm build && cd .." >&2
  exit 1
fi

if [ -f ".env" ]; then
  while IFS='=' read -r key value; do
    case "$key" in
      COPILOTO_*) export "$key=$value" ;;
    esac
  done < .env
fi

printf '\nRota Viva iniciado em http://127.0.0.1:8000\n'
printf 'Pressione Ctrl+C para encerrar.\n\n'

"$PYTHON" main.py
