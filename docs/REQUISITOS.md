# Matriz de atendimento ao PowerPoint

Base: 19 slides do arquivo Copiloto_Inteligente_de_Viagem.pptx fornecido pelo usuário. O frontend web foi pedido pelo usuário; FastAPI/SQLite/React são escolhas de implementação, não exigências do professor.

| Exigência | Implementação / evidência | Estado |
|---|---|---|
| Programa integrado | API processa áudio, foto, contexto, RF e diário no mesmo evento; UI consome API | Fluxo demo validado; real completo pendente |
| Execução contínua e palavra própria | Escuta em blocos no navegador, parser com limites de palavras; padrão “rota viva” configurável por viagem | Código e parser testados; microfone pendente |
| Quatro comandos | Configuração original preservada, normalização de acentos, botões de teste | Parser e API testados; fala ao vivo pendente |
| Emoção do mesmo áudio | Adaptador Wav2Vec2; teste verifica mesmo array usado no ASR e na emoção | Contrato testado com stub; inferência real pendente |
| Local e horário | Cidades simuladas ou coordenadas do navegador; UTC persistido; exibição local | Simulação validada; GPS físico pendente |
| Pelo menos quatro classes de imagem | CLIP compara cinco classes; upload, validação e persistência de foto | Upload testado; pesos/inferência/câmera pendentes |
| RF com ≥5 entradas e ≥3 ações | Oito entradas e cinco classes; artefato treinado; testes de previsão e explicação | Concluído em dataset sintético |
| Dataset próprio construído | Gerador e CSV sintético, rotulagem explícita e grupos separados | Implementado; grupo deve revisar/personalizar |
| Decisão explicável | Entradas/versionamento e decomposição local com soma verificada | Testado |
| Diário completo | SQLite, UUID, mídia local; foto/áudio podem estar ausentes com aviso | Persistência testada; exemplo completo real pendente |
| Resumo e fotos cronológicas | Distância informada, paradas confirmadas, locais, emoção, maior trecho e galeria | Testado com mídias de teste |
| Personalização | Palavra, quatro comandos originais, cinco cenas, oito entradas, cinco ações, Indaiatuba | Documentado; exclusividade com outras equipes não verificada |
| Demonstração ao vivo | Modo demo e roteiro | Fluxo de texto validado no navegador; demonstração física pendente |

## Personalização atual

- Nome: Rota Viva, com padrão de ativação “rota viva”. Não há garantia de que outra equipe não use o nome.
- Comandos: registrar parada; marcar ponto turístico; preciso abastecer; como está o trecho. Cada um aciona o mesmo pipeline e é salvo no diário. A recomendação depende do contexto inferido, não é forçada a repetir o comando.
- Pontos turísticos de Indaiatuba preservados do protótipo. A correspondência textual do nome não é reconhecimento visual do monumento.
- Ações realizadas são confirmadas separadamente. Falar “registrar parada” sem confirmar a caixa não incrementa paradas.
- Não há login, pagamentos, rastreamento contínuo ou serviços externos de geocodificação. GPS guarda coordenadas legíveis; seleção de cidade indica explicitamente simulação.

## Critério para declarar entrega completa

Além dos testes automáticos, instalar os modelos em ambiente apropriado, validar voz/câmera de ponta a ponta e registrar evidências reais. Revisar o dataset e as personalizações com o grupo, incluindo erros de classificação. Até isso ocorrer, esta entrega é uma aplicação integrada com demonstração funcional e integrações neurais ainda pendentes de validação.
