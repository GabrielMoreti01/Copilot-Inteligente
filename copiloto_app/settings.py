import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / os.getenv('COPILOTO_DATA_DIR', 'runtime')
MODEL_PATH = ROOT / os.getenv('COPILOTO_MODEL', 'models/decision.joblib')
PRETRAINED = ROOT / os.getenv('COPILOTO_PRETRAINED', 'models/pretrained')
WAKE_WORD = os.getenv('COPILOTO_WAKE_WORD', 'rota viva').strip().lower()
MAX_IMAGE = 5 * 1024 * 1024
MAX_AUDIO = 3 * 1024 * 1024
CITIES = {'Indaiatuba — SP': [-23.09, -47.218], 'Serra Negra — SP': [-22.612, -46.701], 'Campinas — SP': [-22.905, -47.061]}
SCENES = ['estrada', 'posto de combustível', 'restaurante', 'natureza', 'ponto turístico']
EMOTIONS = ['NEUTRO', 'ANIMADO', 'TRISTE', 'IRRITADO', 'desconhecido']
