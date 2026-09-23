# Modelos locais e validação pendente

Os modelos grandes **não foram baixados ou executados neste computador corporativo**. A aplicação funciona em demonstração com RF real e identifica percepção simulada/indisponível. No modo real, texto e imagem podem gerar registros parciais; cada registro mostra o aviso. Sem transcrição instalada, enviar áudio resulta em 503, sem substituir o áudio pelo texto digitado.

## Abordagens implementadas

| Função | Modelo | Uso |
|---|---|---|
| Transcrição pt-BR | openai/whisper-tiny | O PCM capturado é transcrito com idioma português |
| Emoção acústica | superb/wav2vec2-base-superb-er | O mesmo array de áudio da transcrição alimenta o classificador |
| Cena | openai/clip-vit-base-patch32 | Compara a imagem com cinco descrições em inglês, convertendo o resultado para as classes em português |

As classes de cena são estrada, posto de combustível, restaurante, natureza e ponto turístico. A classificação é zero-shot: o grupo ainda precisa medir o desempenho com fotos próprias. Os candidatos em inglês estão em `perception.py`. CLIP sempre escolhe entre esses candidatos; uma imagem fora do contexto pode receber classe incorreta. Fotos inválidas são rejeitadas e falta de câmera é representada como desconhecido.

SUPERB foi treinado com fala em inglês/IEMOCAP. Mapeamento: neu→NEUTRO, hap→ANIMADO, sad→TRISTE, ang→IRRITADO. **Não confundir tristeza com cansaço.** O modelo não detecta fadiga. Sua transferência para português e para ruído de viagem permanece sem avaliação. Os slides dão estados emocionais como exemplos, não exigem especificamente “cansado”.

## Origem, licença e limitações

- [Whisper tiny — model card](https://huggingface.co/openai/whisper-tiny). A distribuição Hugging Face declara Apache-2.0. O [repositório original Whisper](https://github.com/openai/whisper) publica código/pesos sob MIT. Verificar a licença da distribuição exata usada.
- [SUPERB — model card](https://huggingface.co/superb/wav2vec2-base-superb-er), Apache-2.0. Entrada mono 16 kHz; o backend reamostra PCM quando necessário.
- [CLIP — model card](https://huggingface.co/openai/clip-vit-base-patch32) e [repositório original](https://github.com/openai/CLIP), MIT no repositório original. O model card exige avaliação específica do contexto e aponta limitações de generalização.

Os escores softmax são relativos às classes candidatas. Não significam confiança clínica, causalidade, garantia de segurança ou probabilidade calibrada.

## Instalação opcional em computador apropriado

Com a `.venv` criada, execute explicitamente:

```powershell
.venv\Scripts\python.exe -m pip install --cache-dir .cache/pip -r requirements-ml.txt
.venv\Scripts\python.exe -m scripts.download_models
.venv\Scripts\python.exe main.py
```

Reserve vários GB de disco/RAM para PyTorch, pesos e caches; o desempenho em CPU varia. As versões opcionais são faixas de compatibilidade, ainda não validadas nesta máquina. O script baixa somente mediante execução explícita para `models/pretrained`; o cache fica em `.cache/huggingface`. O servidor usa `local_files_only=True`. Não usa API paga nem envia áudio/imagem a serviços externos. Após validar uma instalação, registre as versões exatas e revisões dos pesos utilizados.

## Teste físico pendente

Em computador autorizado: iniciar modo real, ativar câmera e microfone, falar cada um dos quatro comandos com a palavra de ativação, conferir a transcrição e salvar as saídas. Avaliar pelo menos quatro classes de imagem e as emoções com amostras rotuladas, incluindo erros e indisponibilidade de hardware. Não considerar a integração neural validada só porque os arquivos de pesos existem.

O navegador grava WAV PCM mono em blocos de 8 segundos e pausa a coleta enquanto processa o bloco. Palavra e comando precisam caber no mesmo bloco; fronteiras podem cortar uma frase. A página deve permanecer aberta. ScriptProcessor é uma API legada e precisa ser testada no navegador da apresentação; migrar para AudioWorklet é uma melhoria futura. Permissões de câmera/microfone exigem localhost ou HTTPS. Não foi configurada exposição em rede para testar no celular.
