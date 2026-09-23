"""Local, opt-in neural inference. Missing weights are reported, never invented."""
import importlib.util
import io
import wave
from functools import lru_cache
import numpy as np
from PIL import Image, UnidentifiedImageError
from copiloto_app.settings import PRETRAINED, SCENES

MODEL_IDS = {'image': 'openai/clip-vit-base-patch32', 'speech': 'openai/whisper-tiny', 'emotion': 'superb/wav2vec2-base-superb-er'}
PROMPTS = ['a road or highway', 'a gas station', 'a restaurant', 'a natural landscape with trees', 'a tourist landmark or scenic viewpoint']


def availability():
    installed = all(importlib.util.find_spec(m) for m in ['torch', 'transformers'])
    return {key: {'disponivel': bool(installed and (PRETRAINED / key / 'config.json').exists()), 'modelo': model,
                  'estado': 'pesos locais presentes; inferência exige validação' if installed and (PRETRAINED / key / 'config.json').exists() else 'indisponível: dependências ou pesos ausentes'} for key, model in MODEL_IDS.items()}


def decode_image(data):
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ('JPEG', 'PNG', 'WEBP') or image.width * image.height > 12_000_000:
                raise ValueError('Use JPEG, PNG ou WEBP de até 12 megapixels.')
            image.load()
            return image.convert('RGB')
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError('Imagem inválida.') from exc


def decode_audio(data):
    try:
        with wave.open(io.BytesIO(data), 'rb') as wav:
            rate, channels, width, frames = wav.getframerate(), wav.getnchannels(), wav.getsampwidth(), wav.getnframes()
            if width != 2 or channels != 1 or not 8000 <= rate <= 48000 or not .25 <= frames / rate <= 30:
                raise ValueError('Use WAV PCM mono 16 bits, 8–48 kHz e duração de 0,25–30 segundos.')
            raw = wav.readframes(frames)
            if len(raw) != frames * 2:
                raise ValueError('Áudio incompleto.')
            samples = np.frombuffer(raw, dtype='<i2').astype(np.float32) / 32768
        if rate != 16000:
            from scipy.signal import resample_poly
            from math import gcd
            divisor = gcd(rate, 16000)
            samples = resample_poly(samples, 16000 // divisor, rate // divisor).astype(np.float32)
        return samples
    except (wave.Error, EOFError) as exc:
        raise ValueError('Áudio inválido. Use WAV PCM mono 16 bits.') from exc


@lru_cache(maxsize=3)
def model_bundle(kind):
    from transformers import (AutoProcessor, AutoFeatureExtractor, AutoModelForAudioClassification,
                              CLIPModel, WhisperForConditionalGeneration)
    path = str(PRETRAINED / kind)
    if kind == 'image':
        return AutoProcessor.from_pretrained(path, local_files_only=True), CLIPModel.from_pretrained(path, local_files_only=True).eval()
    if kind == 'speech':
        return AutoProcessor.from_pretrained(path, local_files_only=True), WhisperForConditionalGeneration.from_pretrained(path, local_files_only=True).eval()
    return AutoFeatureExtractor.from_pretrained(path, local_files_only=True), AutoModelForAudioClassification.from_pretrained(path, local_files_only=True).eval()


def infer(kind, data):
    if not availability()[kind]['disponivel']:
        return {'valor': 'desconhecido', 'score': None, 'origem': 'indisponivel', 'modelo': MODEL_IDS[kind]}
    import torch
    processor, model = model_bundle(kind)
    with torch.inference_mode():
        if kind == 'image':
            inputs = processor(text=PROMPTS, images=data, return_tensors='pt', padding=True)
            scores = model(**inputs).logits_per_image[0].softmax(dim=-1)
            index = int(scores.argmax())
            value, score = SCENES[index], float(scores[index])
        elif kind == 'speech':
            inputs = processor(data, sampling_rate=16000, return_tensors='pt')
            ids = model.generate(inputs.input_features, language='portuguese', task='transcribe', max_new_tokens=120)
            value, score = processor.batch_decode(ids, skip_special_tokens=True)[0].strip(), None
        else:
            inputs = processor(data, sampling_rate=16000, return_tensors='pt', padding=True)
            scores = model(**inputs).logits[0].softmax(dim=-1)
            index = int(scores.argmax())
            original = model.config.id2label[index]
            value = {'neu': 'NEUTRO', 'hap': 'ANIMADO', 'sad': 'TRISTE', 'ang': 'IRRITADO'}.get(original, 'desconhecido')
            score = float(scores[index])
    return {'valor': value, 'score': score, 'origem': 'modelo_local', 'modelo': MODEL_IDS[kind]}
