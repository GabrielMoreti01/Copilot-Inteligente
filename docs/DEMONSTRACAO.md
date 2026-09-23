# Roteiro de demonstração

1. Rodar `start.ps1` e abrir http://127.0.0.1:8000. Mostrar Configurações: RF disponível e estado honesto de voz/imagem.
2. Criar viagem em Demonstração com palavra “rota viva”. Explicar que tempo, distância e percepção são simulados neste modo; a previsão do RF é real.
3. Enviar “rota viva, como está o trecho” no cenário estrada. Conferir diário, entradas e recomendação.
4. Selecionar longo trecho. Enviar “rota viva, registrar parada” sem confirmar parada. Explicar recomendação vs. ação realizada.
5. Enviar novo registro com parada confirmada. Conferir contagem e tempo desde a última parada no evento seguinte.
6. Testar turismo e posto, usando os quatro comandos. O cenário anterior influencia o próximo: após um trecho longo, confirmar parada antes de esperar recomendação de turismo.
7. Anexar uma foto de teste autorizada. Em ausência de CLIP, a cena continuará explicitamente simulada no modo demo; não afirmar que a foto foi classificada.
8. Abrir “Por que o modelo recomendou isso?” e mostrar valores e contribuições locais. Explicar que a soma com a base corresponde ao score, sem garantia probabilística.
9. Encerrar viagem. Mostrar distância informada, paradas, locais, emoção, maior trecho e fotos cronológicas. Exportar JSON.
10. Recarregar a página e selecionar a viagem salva. Os dados sobrevivem ao reinício do servidor.

Para a demonstração acadêmica completa, repetir o fluxo em modo real com modelos instalados e câmera/microfone autorizados. Texto, screenshots e dados simulados são recursos de apoio, não substituem o teste físico pedido nos slides.

## Perguntas esperadas

- **Quem decide?** A floresta carregada de `models/decision.joblib`, treinada por `scripts/train.py`. Não existe fallback silencioso por regras.
- **De onde vêm os dados?** O CSV inicial é sintético; os rótulos seguem hipóteses explicitadas em DATASET.md.
- **Como avaliar?** Grupos separados, métricas por classe e matriz de confusão em metricas.json. Não confundir avaliação sintética com desempenho real.
- **É detector de cansaço?** Não. O adaptador acústico estima quatro categorias emocionais e não foi validado em português nesta máquina.
- **O que ocorre sem hardware?** UI oferece texto/uploads, deixa a indisponibilidade visível e conserva as medidas desconhecidas como ausentes no resumo.
- **Onde ficam os dados?** SQLite e mídia dentro de runtime, somente neste computador, com servidor em loopback.
