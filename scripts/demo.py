"""Generate an honest example through the application API without any hardware."""
import json
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from copiloto_app.api import create_app
from copiloto_app.settings import ROOT


def main():
    (ROOT / '.cache').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='demo-', dir=ROOT / '.cache') as directory:
        client = TestClient(create_app(Path(directory)))
        response = client.post('/api/trips', json={'nome': 'Exemplo sintético da documentação', 'modo': 'demo', 'palavra': 'rota viva'})
        response.raise_for_status()
        trip = response.json()['id']
        for command, scenario, stopped in [('como está o trecho', 'estrada', False),
                                           ('registrar parada', 'descanso', True),
                                           ('marcar ponto turístico', 'turismo', False),
                                           ('preciso abastecer', 'abastecimento', False)]:
            response = client.post(f'/api/trips/{trip}/events', data={'payload': json.dumps({
                'texto': 'rota viva, ' + command, 'cenario': scenario, 'parada_realizada': stopped})})
            response.raise_for_status()
        client.post(f'/api/trips/{trip}/end').raise_for_status()
        detail = client.get(f'/api/trips/{trip}').json()
        (ROOT / 'docs/exemplo_viagem.json').write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Exemplo salvo. Contexto e percepção sintéticos, previsão RF real, sem fotos ou gravações.')


if __name__ == '__main__':
    main()
