import io
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlsplit
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError
from copiloto_app import perception
from copiloto_app.config import COMANDOS, PONTOS_TURISTICOS
from copiloto_app.decision import predict, load_model
from copiloto_app.domain import EventInput, TripInput, now, summary
from copiloto_app.settings import DATA_DIR, MODEL_PATH, ROOT, CITIES, SCENES, WAKE_WORD, MAX_AUDIO, MAX_IMAGE
from copiloto_app.storage import Store
from copiloto_app.voice import extrair_comando, normalize

logger = logging.getLogger(__name__)


class BodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        chunks, total = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            total += len(message.get('body', b''))
            if total > MAX_AUDIO + MAX_IMAGE + 65536:
                return await JSONResponse({'detail': 'Envio excede 8 MB.'}, status_code=413)(scope, receive, send)
            chunks.append(message)
            if not message.get('more_body'):
                break
        async def replay():
            return chunks.pop(0) if chunks else await receive()
        await self.app(scope, replay, send)


def create_app(data_dir=DATA_DIR, model_path=MODEL_PATH):
    app = FastAPI(title='Rota Viva · Copiloto Inteligente', version='1.0.0')
    store = Store(data_dir)
    app.state.store = store
    app.add_middleware(BodyLimit)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1', 'testserver'])

    @app.middleware('http')
    async def local_origin(request, call_next):
        origin = request.headers.get('origin')
        if origin and urlsplit(origin).netloc != request.headers.get('host'):
            return JSONResponse({'detail': 'Origem não autorizada.'}, status_code=403)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    def get_trip(db, trip_id):
        trip = store.trip(db, trip_id)
        if not trip:
            raise HTTPException(404, 'Viagem não encontrada.')
        return trip

    @app.get('/api/config')
    def config():
        try:
            model = {'disponivel': True, 'versao': load_model(str(model_path))['version']}
        except Exception:
            model = {'disponivel': False, 'versao': None}
        return {'palavra': WAKE_WORD, 'comandos': list(COMANDOS), 'classes': SCENES,
                'cidades': CITIES, 'pontos': PONTOS_TURISTICOS, 'modelos': perception.availability(),
                'random_forest': model, 'limites': {'imagem_mb': 5, 'audio_mb': 3},
                'aviso': 'RF treinado com cenários sintéticos. Uso acadêmico; escores não calibrados.'}

    @app.get('/api/trips')
    def trips():
        with store.transaction() as db:
            return sorted([json.loads(row[0]) for row in db.execute('SELECT data FROM trips')], key=lambda t: t['inicio'], reverse=True)

    @app.post('/api/trips', status_code=201)
    def start(body: TripInput):
        trip = {'id': str(uuid4()), **body.model_dump(), 'inicio': now(), 'fim': None}
        trip['palavra'] = normalize(body.palavra)
        if not trip['palavra']:
            raise HTTPException(422, 'A palavra de ativação precisa conter letras ou números.')
        with store.transaction() as db:
            store.save_trip(db, trip)
        return trip

    @app.get('/api/trips/{trip_id}')
    def get(trip_id: str):
        with store.transaction() as db:
            trip = get_trip(db, trip_id)
            events = store.events(db, trip_id)
            return {'viagem': trip, 'registros': events, 'resumo': summary(trip, events)}

    @app.post('/api/trips/{trip_id}/end')
    def end(trip_id: str):
        with store.transaction() as db:
            trip = get_trip(db, trip_id)
            if not trip['fim']:
                events = store.events(db, trip_id)
                trip['fim'] = max(now(), events[-1]['horario'] if events else trip['inicio'])
                store.save_trip(db, trip)
            return {'viagem': trip, 'resumo': summary(trip, store.events(db, trip_id))}

    @app.post('/api/trips/{trip_id}/events', status_code=201)
    def event(trip_id: str, payload: str = Form(...), image: UploadFile | None = File(None), audio: UploadFile | None = File(None)):
        try:
            body = EventInput.model_validate_json(payload)
        except ValidationError as exc:
            raise HTTPException(422, 'Dados inválidos: ' + str(exc)) from exc
        with store.transaction() as db:
            trip = get_trip(db, trip_id)
            if trip['fim']:
                raise HTTPException(409, 'Esta viagem já foi encerrada.')
        picture, samples, audio_bytes = None, None, None
        try:
            if image:
                content = image.file.read(MAX_IMAGE + 1)
                if len(content) > MAX_IMAGE:
                    raise HTTPException(413, 'Imagem excede 5 MB.')
                picture = perception.decode_image(content)
            if audio:
                audio_bytes = audio.file.read(MAX_AUDIO + 1)
                if len(audio_bytes) > MAX_AUDIO:
                    raise HTTPException(413, 'Áudio excede 3 MB.')
                samples = perception.decode_audio(audio_bytes)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        missing = {'valor': 'desconhecido', 'score': None, 'origem': 'indisponivel', 'modelo': None}
        text, text_origin = body.texto, 'digitado'
        emotion, scene = dict(missing), dict(missing)
        try:
            if samples is not None:
                transcription = perception.infer('speech', samples)
                if transcription['origem'] == 'indisponivel':
                    raise HTTPException(503, 'Modelo de transcrição indisponível. Instale os modelos locais ou use texto para teste.')
                text, text_origin = transcription['valor'], 'audio_modelo_local'
                emotion = perception.infer('emotion', samples)
            command = extrair_comando(text, trip['palavra'])
            if not command:
                return JSONResponse({'detail': 'Aguardando palavra de ativação e um dos quatro comandos.', 'ignorado': True, 'transcricao': text}, status_code=200)
            if picture is not None:
                scene = perception.infer('image', picture)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception('Falha na inferência local')
            raise HTTPException(503, 'Falha no modelo local. Verifique os pesos e dependências; nenhum resultado foi inventado.') from exc
        file_paths = []
        try:
            with store.transaction() as db:
                trip = get_trip(db, trip_id)
                if trip['fim']:
                    raise HTTPException(409, 'Esta viagem já foi encerrada.')
                events = store.events(db, trip_id)
                timestamp = now()
                distance = body.distancia_km
                source = 'manual' if distance is not None else 'indisponivel'
                if trip['modo'] == 'demo':
                    scenario = {'estrada': ('estrada', 'NEUTRO', 20, 15),
                                'descanso': ('posto de combustível', 'IRRITADO', 160, 150),
                                'turismo': ('ponto turístico', 'ANIMADO', 25, 20),
                                'abastecimento': ('posto de combustível', 'NEUTRO', 30, 160)}[body.cenario]
                    previous_time = events[-1]['horario'] if events else trip['inicio']
                    timestamp = (datetime.fromisoformat(previous_time) + timedelta(minutes=scenario[2])).isoformat()
                    if scene['origem'] != 'modelo_local':
                        scene = {'valor': scenario[0], 'score': None, 'origem': 'simulado', 'modelo': None}
                    if emotion['origem'] != 'modelo_local':
                        emotion = {'valor': scenario[1], 'score': .8, 'origem': 'simulado', 'modelo': None}
                    distance = (events[-1]['distancia_km'] if events else 0) + scenario[3]
                    source = 'simulado'
                known = [e['distancia_km'] for e in events if e['distancia_km'] is not None]
                if distance is not None and known and distance < known[-1]:
                    raise HTTPException(422, 'A distância acumulada não pode diminuir.')
                stops = [e for e in events if e['parada_realizada']]
                elapsed = (datetime.fromisoformat(timestamp) - datetime.fromisoformat(trip['inicio'])).total_seconds() / 60
                last_stop = stops[-1]['horario'] if stops else trip['inicio']
                features = dict(hora=(datetime.fromisoformat(timestamp) - timedelta(hours=3)).hour, tempo_viagem_min=elapsed,
                                distancia_km=distance if distance is not None else 0, confianca_emocao=emotion['score'] or 0,
                                paradas=len(stops), tempo_sem_parada_min=(datetime.fromisoformat(timestamp)-datetime.fromisoformat(last_stop)).total_seconds()/60,
                                classe_imagem=scene['valor'], emocao=emotion['valor'])
                try:
                    recommendation = predict(features, str(model_path))
                except Exception as exc:
                    raise HTTPException(503, 'Random Forest indisponível. Execute python -m scripts.train e reinicie.') from exc
                event_id = str(uuid4())
                photo_name = f'{event_id}.jpg' if picture is not None else None
                audio_name = f'{event_id}.wav' if audio_bytes is not None else None
                if photo_name:
                    path = store.directory / 'media' / photo_name
                    file_paths.append(path)
                    picture.save(path, 'JPEG', quality=88)  # strips uploaded metadata
                if audio_name:
                    path = store.directory / 'media' / audio_name
                    file_paths.append(path)
                    path.write_bytes(audio_bytes)
                coords = CITIES[body.cidade] if body.local_origem == 'simulado' else [body.latitude, body.longitude]
                point = next((v['descricao'] for k, v in PONTOS_TURISTICOS.items() if normalize(k) in normalize(text)), None)
                entry = {'id': event_id, 'viagem_id': trip_id, 'horario': timestamp, 'comando': command,
                         'transcricao': text, 'texto_origem': text_origin, 'emocao': emotion, 'imagem': scene,
                         'local': body.cidade if body.local_origem == 'simulado' else f'GPS {coords[0]:.5f}, {coords[1]:.5f}',
                         'coords': coords, 'local_origem': body.local_origem, 'distancia_km': distance,
                         'distancia_origem': source, 'tempo_origem': 'simulado' if trip['modo'] == 'demo' else 'relogio',
                         'ponto_turistico': point, 'parada_realizada': body.parada_realizada,
                         'foto': f'/api/media/{photo_name}' if photo_name else None,
                         'audio': f'/api/media/{audio_name}' if audio_name else None, 'recomendacao': recommendation,
                         'avisos': (['Distância ausente: modelo usa 0 como imputação; resumo mantém indisponível.'] if distance is None else [])}
                entry['fluxo_completo_real'] = bool(audio_bytes and picture is not None and
                                                   emotion['origem'] == 'modelo_local' and scene['origem'] == 'modelo_local')
                if not entry['fluxo_completo_real']:
                    entry['avisos'].append('Registro de demonstração/teste: o fluxo completo com áudio e imagem reais ainda não foi validado neste evento.')
                db.execute('INSERT INTO events VALUES (?,?,?)', (event_id, trip_id, json.dumps(entry, ensure_ascii=False)))
                return entry
        except BaseException:
            for path in file_paths:
                path.unlink(missing_ok=True)
            raise

    @app.get('/api/media/{filename}')
    def media(filename: str):
        from uuid import UUID
        path = Path(filename)
        try:
            UUID(path.stem)
        except ValueError:
            raise HTTPException(404)
        if path.suffix not in ['.jpg', '.wav'] or path.name != filename:
            raise HTTPException(404)
        file = store.directory / 'media' / filename
        if not file.is_file():
            raise HTTPException(404)
        return FileResponse(file)

    dist = ROOT / 'frontend/dist'
    if dist.exists():
        app.mount('/', StaticFiles(directory=dist, html=True), name='frontend')
    else:
        @app.get('/')
        def no_frontend():
            return {'mensagem': 'Faça o build do frontend. API disponível em /docs.'}
    return app


app = create_app()
