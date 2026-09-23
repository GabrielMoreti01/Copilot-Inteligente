"""Command parsing. Acoustic inference is in perception.py, never in keywords."""
import re
import unicodedata
from copiloto_app.config import COMANDOS


def normalize(text):
    return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')).split())


def extrair_comando(frase, wake_word=None):
    text = normalize(frase)
    if wake_word:
        match = re.search(r'(?:^| )' + re.escape(normalize(wake_word)) + r'(?: |$)', text)
        if not match:
            return None
        text = text[match.end():]
    for command in COMANDOS:
        if re.search(r'(?:^| )' + re.escape(normalize(command)) + r'(?: |$)', text):
            return command
    return None
