# Rota Viva · Copiloto Inteligente de Viagem

Aplicação acadêmica integrada com **FastAPI + SQLite + React/TypeScript**, diário persistente e Random Forest treinado. O protótipo original foi preservado em `legacy/`.

**Estado da entrega:** demonstração integrada funcional. Voz, emoção acústica e classificação de imagem possuem adaptadores locais, mas os pesos grandes não foram baixados nem validados neste computador corporativo. Não considerar o projeto acadêmico totalmente concluído antes de executar o fluxo real e revisar o dataset com o grupo. Consulte [matriz de requisitos](docs/REQUISITOS.md).

## Abrir neste computador

O ambiente `.venv`, o modelo RF e o build do frontend já foram preparados nesta pasta. No PowerShell, dentro do projeto:

```powershell
.venv\Scripts\python.exe main.py
```

Abra **http://127.0.0.1:8000**. Encerre com **Ctrl+C** no terminal. Não precisa executar como administrador ou mudar a política de execução. `start.ps1` é uma alternativa que também carrega variáveis `COPILOTO_*` do `.env`.

Comece por **Demonstração** e use os botões de comando. Nenhum dispositivo é ativado automaticamente. Tempo/distância/percepção simulados têm origem visível; a recomendação vem do RF treinado. Marque a confirmação de parada somente quando quiser registrar uma ação realizada.

## Instalação reproduzível em outro computador

Requer Python 3.12 e Node.js 20.19+ ou 22.12+ disponíveis em ambiente autorizado. Não há instaladores globais automáticos, serviço do Windows, tarefas agendadas ou abertura de firewall.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --cache-dir .cache/pip -r requirements.txt
.venv\Scripts\python.exe -m scripts.train
cd frontend
pnpm install --frozen-lockfile --store-dir ../.cache/pnpm --ignore-scripts
pnpm build
cd ..
.venv\Scripts\python.exe main.py
```

`pnpm-lock.yaml` fixa as dependências do frontend; `requirements-lock.txt` registra todas as versões Python testadas (pode ser usado no lugar de requirements.txt). O comando `pnpm` precisa estar disponível; no ambiente Codex desta máquina foi usado o runtime já fornecido pela aplicação, sem instalação global. Para usar npm em outro ambiente, `npm install --ignore-scripts` e `npm run build` funcionam com package.json, mas geram outro lockfile e exigem nova validação.

O servidor serve o build de produção e a API na mesma origem. Em desenvolvimento: `pnpm dev` no frontend e `python main.py` no backend; o proxy Vite encaminha `/api` sem habilitar CORS amplo.

## Testar e treinar

```powershell
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.venv\Scripts\python.exe -m scripts.train
cd frontend
pnpm test
pnpm build
```

São 16 testes de backend e três de frontend. Treinamento atual: 2.400 exemplos sintéticos, oito entradas, cinco decisões, 600 exemplos de teste em grupos separados. Acurácia sintética: 96,0%, F1 macro: 0,9482. Isso não mede qualidade de voz/imagem nem desempenho em estrada.

## Modelos de voz e imagem

Veja [MODELOS.md](docs/MODELOS.md) para instalação **opcional e explícita** dos modelos locais, licenças, formatos de áudio, limitações e roteiro de validação. Não há downloads de pesos quando o servidor inicia. Nenhum áudio ou imagem é enviado a serviços de IA externos.

O navegador captura WAV PCM mono e imagem mediante permissão. A mesma amostra de áudio alimenta transcrição e emoção. A câmera do servidor nunca é acessada. Sem modelos, Configurações mostra indisponibilidade e os registros de teste ficam identificados como incompletos. O modo real permite cidade simulada, conforme o enunciado; GPS registra coordenadas, sem rastreamento contínuo. A distância real é informada manualmente, desde o início da viagem.

## Organização

- `copiloto_app/api.py`: contratos HTTP e orquestração dos eventos.
- `storage.py` / `domain.py`: persistência transacional, validação e resumo.
- `voice.py` / `perception.py`: interpretação dos comandos e adaptadores neurais.
- `decision.py`: inferência RF e explicação local.
- `scripts/train.py`: dados sintéticos, treino, avaliação e artefato.
- `frontend/src`: interface responsiva e captura no navegador.
- `runtime/`: SQLite e mídia local, ignorados no Git.
- `data/cenarios_sinteticos.csv`: dados construídos e identificação do split.
- `docs/`: dataset, modelos, requisitos, validação e apresentação.

## Contratos principais

Documentação interativa: http://127.0.0.1:8000/docs

| Método | Rota | Função |
|---|---|---|
| GET | /api/config | Comandos, cidades, classes e disponibilidade |
| POST / GET | /api/trips | Criar / listar viagens |
| GET | /api/trips/{id} | Viagem, registros e resumo |
| POST | /api/trips/{id}/events | Multipart: payload JSON, image opcional e audio opcional |
| POST | /api/trips/{id}/end | Encerrar sem apagar o histórico |
| GET | /api/media/{uuid.ext} | Consultar foto/áudio persistido |

Um comando sem ativação é ignorado e não cria entrada. JSON/mídia inválida retornam 422, tamanho excedido 413, viagem encerrada 409, modelo obrigatório ausente 503. Imagem até 5 MB/12 MP, áudio WAV mono PCM16 de 0,25 a 30 segundos até 3 MB, requisição inteira até aproximadamente 8 MB.

Recomendações não incrementam paradas. O resumo calcula maior trecho a partir das distâncias acumuladas informadas e paradas confirmadas, incluindo o trecho final observado. Se faltar distância em uma parada, esse indicador fica indisponível. “Distância total” é a última medida registrada, não uma estimativa do percurso após o último registro.

## Documentação acadêmica

- [Dataset, rotulagem, resultados e explicação](docs/DATASET.md)
- [Modelos e instalação opcional](docs/MODELOS.md)
- [Matriz de requisitos e personalização](docs/REQUISITOS.md)
- [Roteiro de apresentação](docs/DEMONSTRACAO.md)
- [Verificações e limitações](docs/VALIDACAO.md)
- [Exemplo de diário gerado pela API em modo demo](docs/exemplo_viagem.json)

O grupo deve adaptar/validar a base sintética, confirmar a palavra de ativação com as outras equipes e coletar evidências reais de demonstração. Não há publicação, envio de dados da empresa ou acesso a documentos corporativos nesta implementação.
