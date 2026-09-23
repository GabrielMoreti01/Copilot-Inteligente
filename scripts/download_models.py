"""Explicit network action. Run manually on an appropriate computer."""
import os
from copiloto_app.settings import ROOT, PRETRAINED
os.environ['HF_HOME'] = str(ROOT / '.cache/huggingface')
from huggingface_hub import snapshot_download
from copiloto_app.perception import MODEL_IDS

if __name__ == '__main__':
    for name, repo in MODEL_IDS.items():
        print(f'Baixando {repo} para {PRETRAINED / name}')
        snapshot_download(repo, local_dir=PRETRAINED / name,
                          allow_patterns=['*.json', '*.txt', '*.safetensors', 'pytorch_model.bin', 'merges.txt', 'vocab.json'],
                          ignore_patterns=['onnx/*', 'tf_model*', 'flax_model*'])
