# Validação desta entrega

Ambiente: Windows, Python 3.12 em `.venv`, Node 24 fornecido pelo ambiente Codex. Dependências instaladas apenas no projeto, com autorização para os downloads. Nada foi instalado globalmente; não foram alterados firewall, registro, políticas de execução, inicialização ou configurações do Windows.

## Verificações executadas

- Treinamento real de RandomForestClassifier e avaliação sintética: métricas em metricas.json.
- Backend: 16 testes pytest cobrindo quatro comandos, limites de palavra, RF/explicação local, reinício de persistência, isolamento por viagem, encerramento, ausência de hardware, distância inválida, JSON inválido, mídia inválida/grande, UUID de fotos, galeria cronológica, contrato do mesmo áudio, cálculos de paradas/resumo e bloqueio de origem externa.
- Frontend: TypeScript e build Vite de produção concluídos; três testes Vitest para PCM/WAV e contrato do cliente HTTP, incluindo erros.
- Navegador: criação de viagem demo, envio de comando, registro persistido, cenário de trecho longo, recomendação de descanso e confirmação de parada. Encerramento e resumo conferidos após reinício do backend e recarga do navegador. Interface inspecionada em desktop e viewport de 390×844; nenhum erro/warning de console no teste.
- Exemplo do diário e resumo gerado por `python -m scripts.demo`, usando a API real e contextos sintéticos: `docs/exemplo_viagem.json`. Não contém gravações ou fotos reais.

Os testes de inferência acústica usam stub **apenas no teste de contrato** e não validam a qualidade ou execução dos modelos neurais reais. O RF testado é treinado de fato. As imagens dos testes automatizados são pequenos arquivos sintéticos que validam upload e armazenamento, não acurácia visual.

## Não executado

- Downloads/execução de PyTorch e pesos Whisper, Wav2Vec2 e CLIP.
- Captura de câmera/microfone/GPS deste computador.
- Avaliação emocional em português, acurácia de cenas, latência neural e demonstração real de ponta a ponta.
- Teste físico em celular. O servidor permanece restrito a 127.0.0.1, sem exposição na rede da empresa.

Há um aviso de depreciação do adaptador httpx do TestClient da versão instalada de Starlette. Não afetou a execução dos testes. Migrar o adaptador quando estabilizar as versões, sem ocultar falhas.
