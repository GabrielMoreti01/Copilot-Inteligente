# Rota Viva - Copiloto Inteligente de Viagem

Projeto academico de um copiloto de viagem com **FastAPI**, **SQLite**, **React/TypeScript** e **Random Forest**.

Ele registra comandos de viagem, localizacao, imagem, emocao estimada, recomendacao do modelo e um diario de bordo com resumo final.

## Situacao real da pasta

Ao baixar ou copiar este projeto, ele pode ainda nao estar pronto para rodar. Os itens abaixo sao gerados localmente e ficam fora do Git:

- `.venv/`: ambiente Python.
- `models/decision.joblib`: modelo Random Forest treinado.
- `frontend/node_modules/`: dependencias do frontend.
- `frontend/dist/`: build final da interface.
- `runtime/`: banco SQLite e midias salvas durante o uso.

Por isso, rode o preparo uma vez antes de iniciar o sistema.

## Requisitos

Instale ou tenha disponivel:

- Python 3.11 ou 3.12.
- Node.js 20.19+ ou 22.12+.
- pnpm, recomendado para usar o `pnpm-lock.yaml`.

Se nao tiver `pnpm`, da para usar `npm`, mas o caminho principal do projeto usa `pnpm`.

## Preparo rapido no PowerShell

Na pasta do projeto:

```powershell
cd "C:\Users\Mateus Lago\Copilot-Inteligente"
.\setup.ps1
```

Se o PowerShell bloquear a execucao de script, rode:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Depois inicie:

```powershell
.\start.ps1
```

Se o `start.ps1` tambem for bloqueado:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Abra no navegador:

```text
http://127.0.0.1:8000
```

Para encerrar, pressione `Ctrl+C` no terminal.

## Preparo rapido no Bash

Na pasta do projeto:

```bash
cd "/c/Users/Mateus Lago/Copilot-Inteligente"
bash setup.sh
```

Depois inicie:

```bash
bash start.sh
```

Abra:

```text
http://127.0.0.1:8000
```

## Passo a passo manual no PowerShell

Use esta parte se preferir fazer comando por comando.

```powershell
cd "C:\Users\Mateus Lago\Copilot-Inteligente"

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m scripts.train

cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..

.\.venv\Scripts\python.exe main.py
```

Se o comando `py -3.12` nao existir no seu Windows, tente Python 3.11:

```powershell
py -3.11 -m venv .venv
```

Se o `py` nao existir, use um Python instalado:

```powershell
python -m venv .venv
```

Se o `python` abrir a Microsoft Store ou der erro, instale o Python 3.12 ou 3.11 pelo site oficial, ou use o caminho completo do executavel Python.

## Passo a passo manual no Bash

```bash
cd "/c/Users/Mateus Lago/Copilot-Inteligente"

python3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m scripts.train

cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..

./.venv/Scripts/python.exe main.py
```

Em Linux/macOS, o caminho do Python do ambiente virtual costuma ser:

```bash
./.venv/bin/python
```

## Como usar a aplicacao

1. Abra `http://127.0.0.1:8000`.
2. Comece pela aba **Minha viagem**.
3. Crie uma viagem em modo **Demonstração**.
4. Use a palavra de ativacao padrao `rota viva`.
5. Clique nos comandos prontos ou digite frases como:

```text
rota viva, como está o trecho
rota viva, registrar parada
rota viva, marcar ponto turístico
rota viva, preciso abastecer
```

No modo demonstracao, tempo, distancia, cena e emocao podem ser simulados de forma identificada. A recomendacao vem do Random Forest treinado.

## O que o sistema faz

- Cria e lista viagens.
- Espera uma palavra de ativacao configuravel.
- Interpreta quatro comandos de viagem.
- Registra horario, local, distancia e paradas.
- Salva foto e audio quando enviados.
- Usa Random Forest para recomendar uma acao.
- Explica a recomendacao com as entradas e contribuicoes do modelo.
- Mantem diario de bordo em SQLite.
- Mostra resumo final com distancia, paradas, locais, emocao predominante e fotos.
- Exporta diario e resumo em JSON.

## Comandos de teste

Backend:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Frontend:

```powershell
cd frontend
pnpm test
pnpm build
cd ..
```

Treinar novamente o Random Forest:

```powershell
.\.venv\Scripts\python.exe -m scripts.train
```

## Modelos reais de voz e imagem

O projeto tem adaptadores para modelos locais, mas eles sao opcionais e pesados:

- Whisper tiny para transcricao de voz.
- Wav2Vec2/SUPERB para emocao acustica.
- CLIP para classificacao de imagem.

Instalacao opcional:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
.\.venv\Scripts\python.exe -m scripts.download_models
```

Sem esses pesos, o modo demo continua funcionando, mas o fluxo real completo com microfone, emocao e imagem ainda precisa ser validado em uma maquina autorizada.

## Relacao com o PowerPoint

O projeto atende a estrutura pedida no enunciado:

- Sistema integrado.
- Palavra de ativacao.
- Pelo menos quatro comandos.
- Localizacao ou cidade simulada.
- Classificacao de imagem com pelo menos quatro classes.
- Random Forest com mais de cinco variaveis.
- Mais de tres decisoes possiveis.
- Diario de bordo.
- Resumo final.
- Explicacao da decisao.

Para declarar a entrega como 100% validada, ainda e necessario testar o fluxo real com microfone, camera, GPS e modelos locais instalados.

## Estrutura do projeto

- `main.py`: inicia o servidor local.
- `start.ps1` / `start.sh`: iniciam o projeto depois do preparo.
- `setup.ps1` / `setup.sh`: criam ambiente, instalam dependencias, treinam modelo e geram frontend.
- `copiloto_app/api.py`: API e fluxo principal.
- `copiloto_app/decision.py`: Random Forest e explicacao.
- `copiloto_app/perception.py`: audio, imagem e adaptadores de IA local.
- `copiloto_app/voice.py`: palavra de ativacao e comandos.
- `frontend/src`: interface web.
- `scripts/train.py`: gera dataset, metricas e modelo.
- `docs/`: documentacao academica.
- `legacy/`: prototipo antigo preservado.

## Problemas comuns

### `py -3.12` deu erro

O Windows pode nao ter o lancador `py`, ou voce pode ter apenas Python 3.11. Tente:

```powershell
py -3.11 -m venv .venv
```

Ou:

```powershell
python -m venv .venv
```

Se tambem falhar, instale Python 3.12 ou 3.11, ou use o caminho completo do executavel.

### `numpy==2.5.3` deu erro no Python 3.11

Atualize o projeto para a versao atual deste README. O `requirements.txt` agora usa NumPy 2.4.x no Python 3.11 e NumPy 2.5.3 no Python 3.12+.

Se o erro continuar, apague o ambiente quebrado e rode de novo:

```powershell
Remove-Item -Recurse -Force .venv
.\setup.ps1
```

### `pip install` falhou

Verifique se a internet esta liberada. Sem baixar as dependencias, o backend nao roda.

### `pnpm` nao existe

Instale pnpm ou use npm:

```powershell
cd frontend
npm install
npm run build
cd ..
```

Usar npm pode gerar outro lockfile. Para entrega final, prefira pnpm.

### Abriu a API, mas nao abriu a interface

Falta gerar `frontend/dist`:

```powershell
cd frontend
pnpm build
cd ..
```

### O Random Forest esta indisponivel

Falta gerar `models/decision.joblib`:

```powershell
.\.venv\Scripts\python.exe -m scripts.train
```

## Observacao importante

O dataset atual e sintetico e serve como base academica. Ele nao prova desempenho em viagens reais. Antes da apresentacao final, revise as regras, personalize com o grupo e faca uma demonstracao real ou deixe claro quando estiver usando modo demonstracao.
