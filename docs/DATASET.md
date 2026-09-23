# Dataset e Random Forest

O dataset desta entrega foi **construído sinteticamente por código**, como ponto de partida para o grupo. Não foi coletado em viagens, não contém dados da empresa e não deve ser apresentado como coleta própria de campo. O grupo precisa revisar, adaptar e assumir as decisões de construção antes da entrega acadêmica.

## Reprodução

`python -m scripts.train` gera `data/cenarios_sinteticos.csv`, `models/decision.joblib` e `docs/metricas.json`.

São 800 grupos, cada um com três variações próximas de distância/tempo: 2.400 exemplos. O gerador usa seed 42. GroupShuffleSplit separa 75% dos grupos para treino e 25% para teste, mantendo as variações do mesmo cenário no mesmo conjunto. DictVectorizer aprende o vocabulário somente no treino. A floresta usa 120 árvores, min_samples_leaf=2 e ponderação balanceada das classes. O processamento usa um núcleo.

As variáveis são horário de São Paulo (UTC−3), duração em minutos, distância acumulada em km, score da emoção, número de paradas anteriores, minutos desde a última parada, classe da imagem e categoria emocional. Categóricas recebem codificação one-hot. Ausência de distância/score usa 0 apenas na inferência, com aviso no registro; o resumo conserva distância ausente como indisponível. Cena/emoção ausentes usam a categoria `desconhecido`.

## Rotulagem explícita dos cenários

As regras são usadas **para construir os rótulos de treinamento**, não como fallback de inferência:

1. Tempo desde a última parada ≥120 minutos ou irritação com score ≥0,6: DESCANSAR.
2. Posto e distância acumulada ≥120 km: AVALIAR ABASTECIMENTO.
3. Restaurante entre 11h e 14h: ALIMENTAR-SE.
4. Natureza/ponto turístico e emoção ANIMADO: REGISTRAR PONTO TURÍSTICO.
5. Demais contextos: CONTINUAR.

Essa prioridade é uma hipótese didática, não uma regra de segurança viária. A distância acumulada não mede combustível restante. O sistema recomenda **avaliar** abastecimento e não afirma que o tanque está vazio. Não há detecção de fadiga. As classes emocionais são exemplos escolhidos pelo projeto, não diagnósticos.

O sorteio é enriquecido com contextos de alimentação e turismo (um quinto dos grupos para cada contexto) para evitar classes raras demais. Os demais grupos mantêm variedade de horários, estados e cenas. Há 504 exemplos de alimentação, 559 de turismo, 700 de continuar, 541 de descansar e 96 de avaliar abastecimento. Ainda existe desbalanceamento.

## Resultados medidos

Versão `rf-sintetico-v1-149b87a451fb`: 1.800 exemplos de treino, 600 de teste; interseção de grupos = 0. Acurácia = **96,0%**, F1 macro = **0,9482**.

| Classe | Precisão | Recall | F1 | Exemplos de teste |
|---|---:|---:|---:|---:|
| ALIMENTAR-SE | 0,9556 | 0,9556 | 0,9556 | 135 |
| AVALIAR ABASTECIMENTO | 0,8889 | 0,8889 | 0,8889 | 27 |
| CONTINUAR | 0,9618 | 0,9096 | 0,9350 | 166 |
| DESCANSAR | 0,9262 | 1,0000 | 0,9617 | 113 |
| REGISTRAR PONTO TURÍSTICO | 1,0000 | 1,0000 | 1,0000 | 159 |

`metricas.json` contém matriz de confusão (linhas = classe verdadeira; colunas = prevista, na ordem de `classes`), distribuição, hash e métricas completas. Não interpretar 96% como precisão do sistema inteiro: voz e visão não foram avaliadas aqui. Não comprova generalização real, pois treino e teste vêm do mesmo gerador. O teste foi consultado durante o desenvolvimento; uma avaliação final rigorosa precisa de novos cenários independentes e dados de campo rotulados pelo grupo.

## Explicação de uma recomendação

Para a classe escolhida, o código percorre o caminho de cada árvore e acumula a mudança do score entre pai e filho, atribuída à variável usada naquela divisão. Faz a média entre árvores e agrupa dimensões one-hot pela variável original. A base na raiz mais todas as contribuições é igual ao score final da classe, dentro de tolerância numérica (ver teste).

Contribuição positiva apoia a classe escolhida, negativa a reduz. Não são percentuais de causalidade nem a importância global das variáveis. O score da floresta e os escores neurais não estão calibrados. O registro salva versão, entradas, base e contribuições.

## Próxima coleta do grupo

Criar cenários revisados por participantes, registrar o critério de rotulagem e a origem de cada linha. Separar pessoas/viagens inteiras entre treino e teste. Avaliar discordância de rótulos e classes raras. Guardar um conjunto final independente, sem adaptar o modelo após olhar seus resultados. Não carregar arquivos joblib obtidos de fontes desconhecidas.
