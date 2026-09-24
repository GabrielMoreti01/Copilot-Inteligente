"""Command parsing. Acoustic inference is in perception.py, never in keywords."""
import re
import unicodedata
from copiloto_app.config import COMANDOS

WAKE_ALIASES = {
    'rota viva': ['rota viva', 'rota vivo', 'roda viva', 'rota vida'],
}

COMMAND_ALIASES = {
    'registrar parada': ['registrar parada', 'registra parada', 'registrar uma parada', 'registrar a parada'],
    'marcar ponto turístico': ['marcar ponto turistico', 'marca ponto turistico', 'marcar ponto turístico', 'marca ponto turístico'],
    'preciso abastecer': ['preciso abastecer', 'precisa abastecer', 'preciso abastece', 'abastecer'],
    'como está o trecho': ['como esta o trecho', 'como esta trecho', 'como ta o trecho', 'como esta a estrada'],
}


def normalize(text):
    return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')).split())


def find_phrase(text, phrases):
    matches = []
    for phrase in phrases:
        match = re.search(r'(?:^| )' + re.escape(normalize(phrase)) + r'(?: |$)', text)
        if match:
            matches.append(match)
    return min(matches, key=lambda match: match.start()) if matches else None


def extrair_comando(frase, wake_word=None):
    text = normalize(frase)
    if wake_word:
        normalized_wake = normalize(wake_word)
        wake_options = WAKE_ALIASES.get(normalized_wake, [normalized_wake])
        match = find_phrase(text, wake_options)
        if not match:
            return None
        text = text[match.end():]
    found = []
    for command in COMANDOS:
        match = find_phrase(text, COMMAND_ALIASES.get(command, [command]))
        if match:
            found.append((match.start(), command))
    return min(found)[1] if found else None
