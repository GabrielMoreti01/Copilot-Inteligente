import io
import json
import wave
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from copiloto_app.api import create_app
from copiloto_app.decision import FEATURES, predict
from copiloto_app.domain import summary
from copiloto_app.perception import decode_audio, decode_image
from copiloto_app.voice import extrair_comando
from scripts.train import train


@pytest.fixture(scope='session')
def trained(tmp_path_factory):
    directory = tmp_path_factory.mktemp('model')
    path = directory / 'model.joblib'
    report = train(path, directory / 'data', directory / 'docs')
    return path, report


@pytest.fixture
def client(tmp_path, trained):
    return TestClient(create_app(tmp_path, trained[0]))


def start(client, mode='demo'):
    response = client.post('/api/trips', json={'nome':'Teste', 'modo': mode, 'palavra':'rota viva'})
    assert response.status_code == 201
    return response.json()['id']


def send(client, trip, **values):
    return client.post(f'/api/trips/{trip}/events', data={'payload': json.dumps({'texto':'Rota Viva, como está o trecho', **values})})


@pytest.mark.parametrize('command', ['registrar parada','marcar ponto turístico','preciso abastecer','como está o trecho'])
def test_commands(command):
    assert extrair_comando('ROTA VIVA, '+command, 'rota viva') == command
    assert extrair_comando(command,'rota viva') is None


def test_word_boundaries():
    assert extrair_comando('derrota viva como está o trecho','rota viva') is None
    assert extrair_comando('rota viva marcar ponto turistico','rota viva') == 'marcar ponto turístico'


def test_model_and_local_explanation(trained):
    row=dict(hora=12, tempo_viagem_min=160, distancia_km=190, confianca_emocao=.8, paradas=1,
             tempo_sem_parada_min=160, classe_imagem='posto de combustível', emocao='IRRITADO')
    result=predict(row,str(trained[0]))
    assert result['acao']=='DESCANSAR'
    assert set(result['entradas'])==set(FEATURES)
    explanation=result['explicacao']
    assert explanation['base']+sum(explanation['contribuicoes'].values())==pytest.approx(result['score'])
    assert trained[1]['group_overlap']==0
    assert len(trained[1]['classes'])>=3
    row['classe_imagem']='desconhecido'
    assert predict(row,str(trained[0]))['acao']


def test_trip_lifecycle_persistence_isolation(client,trained):
    a,b=start(client),start(client)
    first=send(client,a,cenario='descanso').json()
    assert first['recomendacao']['acao']=='DESCANSAR'
    assert first['parada_realizada'] is False
    assert first['imagem']['origem']=='simulado'
    assert send(client,a,parada_realizada=True).status_code==201
    detail=client.get('/api/trips/'+a).json()
    assert detail['resumo']['paradas']==1
    assert detail['resumo']['distancia_total_km']==165
    assert detail['resumo']['duracao_min']==180
    assert len(client.get('/api/trips/'+b).json()['registros'])==0
    reopened=TestClient(create_app(client.app.state.store.directory,trained[0]))
    assert len(reopened.get('/api/trips/'+a).json()['registros'])==2
    assert client.post('/api/trips/'+a+'/end').status_code==200
    assert send(client,a).status_code==409


def test_missing_camera_and_models(client):
    trip=start(client,'real')
    response=send(client,trip)
    assert response.status_code==201
    event=response.json()
    assert event['imagem']['valor']=='desconhecido'
    assert event['emocao']['score'] is None
    assert event['foto'] is None
    assert client.get('/api/trips/'+trip).json()['resumo']['distancia_total_km'] is None


def test_rejects_invalid_distance_and_json(client):
    trip=start(client,'real')
    assert send(client,trip,distancia_km=50).status_code==201
    assert send(client,trip,distancia_km=40).status_code==422
    assert send(client,trip,distancia_km=-1).status_code==422
    assert send(client,trip,distancia_km=float('nan')).status_code==422
    assert send(client,trip,local_origem='gps').status_code==422
    assert client.post('/api/trips/'+trip+'/events',data={'payload':'bad'}).status_code==422
    assert client.get('/api/trips/missing').status_code==404


def test_ignored_command_not_saved(client):
    trip=start(client)
    assert send(client,trip,texto='registrar parada').json()['ignorado']
    assert client.get('/api/trips/'+trip).json()['resumo']['registros']==0


def image_bytes():
    data=io.BytesIO();Image.new('RGB',(20,20),'green').save(data,'PNG');return data.getvalue()


def audio_bytes():
    data=io.BytesIO()
    with wave.open(data,'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(16000);wav.writeframes(b'\x00\x00'*16000)
    return data.getvalue()


def test_media_validation(client):
    trip=start(client)
    endpoint='/api/trips/'+trip+'/events'
    payload={'payload':json.dumps({'texto':'rota viva registrar parada'})}
    assert client.post(endpoint,data=payload,files={'image':('a.png',b'invalid')}).status_code==422
    assert client.post(endpoint,data=payload,files={'audio':('a.wav',b'invalid')}).status_code==422
    assert client.post(endpoint,data=payload,files={'image':('a.png',b'x'*(5*1024*1024+1))}).status_code==413
    assert client.post(endpoint,data=payload,files={'audio':('a.wav',audio_bytes())}).status_code==503
    entries=[client.post(endpoint,data=payload,files={'image':('a.png',image_bytes())}).json() for _ in range(2)]
    assert entries[0]['foto']!=entries[1]['foto']
    assert client.get(entries[0]['foto']).headers['content-type']=='image/jpeg'
    assert client.get('/api/media/not-a-uuid.jpg').status_code==404
    gallery=client.get('/api/trips/'+trip).json()['resumo']['fotos']
    assert [e['id'] for e in gallery]==[e['id'] for e in entries]


def test_same_audio_drives_transcription_and_emotion(client,monkeypatch):
    received=[]
    def infer(kind,data):
        received.append((kind,id(data)))
        return {'valor':'rota viva preciso abastecer' if kind=='speech' else 'NEUTRO', 'score':.7,'origem':'modelo_local','modelo':'stub-for-contract-test'}
    monkeypatch.setattr('copiloto_app.perception.infer',infer)
    trip=start(client,'real')
    result=client.post('/api/trips/'+trip+'/events',data={'payload':'{}'},files={'audio':('a.wav',audio_bytes())})
    assert result.status_code==201
    assert received[0][1]==received[1][1]
    assert result.json()['texto_origem']=='audio_modelo_local'
    assert result.json()['audio']


def test_summary_stop_distances():
    start_time=datetime.now(timezone.utc)
    trip={'inicio':start_time.isoformat(),'fim':(start_time+timedelta(hours=3)).isoformat(),'modo':'real'}
    entries=[dict(distancia_km=d,parada_realizada=s,emocao={'valor':'NEUTRO'},local='A',coords=[0,0],ponto_turistico=None,foto=None) for d,s in [(20,False),(50,True),(90,False),(110,True),(150,False)]]
    result=summary(trip,entries)
    assert result['maior_trecho_km']==60
    assert result['paradas']==2
    assert result['duracao_min']==180
    entries[1]['distancia_km']=None
    assert summary(trip,entries)['maior_trecho_km'] is None


def test_origin_protection(client):
    assert client.post('/api/trips',json={},headers={'Origin':'https://example.com'}).status_code==403


def test_missing_rf(tmp_path):
    client=TestClient(create_app(tmp_path,tmp_path/'missing.joblib'))
    assert client.get('/api/config').json()['random_forest']['disponivel'] is False
    assert send(client,start(client)).status_code==503


def test_audio_decode():
    assert len(decode_audio(audio_bytes()))==16000
    with pytest.raises(ValueError):decode_image(b'bad')
