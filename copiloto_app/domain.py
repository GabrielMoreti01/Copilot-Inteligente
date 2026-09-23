from collections import Counter
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from copiloto_app.settings import WAKE_WORD, CITIES


def now():
    return datetime.now(timezone.utc).isoformat()


class TripInput(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    nome: str = Field(default='Minha viagem', min_length=1, max_length=80)
    modo: Literal['real', 'demo'] = 'demo'
    palavra: str = Field(default=WAKE_WORD, min_length=2, max_length=40, pattern=r'.*\S.*')


class EventInput(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    texto: str = Field(default='', max_length=500)
    cidade: str = Field(default='Indaiatuba — SP', max_length=120)
    local_origem: Literal['simulado', 'gps'] = 'simulado'
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    distancia_km: float | None = Field(default=None, ge=0, le=100000)
    parada_realizada: bool = False
    cenario: Literal['estrada', 'descanso', 'turismo', 'abastecimento'] = 'estrada'

    @model_validator(mode='after')
    def location(self):
        if self.local_origem == 'gps' and (self.latitude is None or self.longitude is None):
            raise ValueError('GPS exige latitude e longitude.')
        if self.local_origem == 'simulado' and self.cidade not in CITIES:
            raise ValueError('Selecione uma cidade cadastrada.')
        return self


def summary(trip, events):
    distances = [e['distancia_km'] for e in events if e['distancia_km'] is not None]
    last_stop = 0.0
    longest = 0.0
    incomplete = False
    for event in events:
        distance = event['distancia_km']
        if distance is not None and last_stop is not None:
            longest = max(longest, distance - last_stop)
        if event['parada_realizada']:
            last_stop = distance
            incomplete |= distance is None
    emotions = Counter(e['emocao']['valor'] for e in events if e['emocao']['valor'] != 'desconhecido')
    end = trip['fim'] or (events[-1]['horario'] if trip['modo'] == 'demo' and events else now())
    return {'distancia_total_km': distances[-1] if distances else None,
            'distancia_observacao': 'Última distância informada; não é rastreamento contínuo de GPS.',
            'paradas': sum(e['parada_realizada'] for e in events),
            'locais': len({e['ponto_turistico'] or (e['local'], tuple(e['coords'])) for e in events}),
            'emocao_predominante': emotions.most_common(1)[0][0] if emotions else 'indisponível',
            'maior_trecho_km': None if incomplete or not distances else round(longest, 3),
            'duracao_min': round((datetime.fromisoformat(end) - datetime.fromisoformat(trip['inicio'])).total_seconds() / 60, 2),
            'registros': len(events), 'fotos': [e for e in events if e['foto']], 'modo': trip['modo']}
