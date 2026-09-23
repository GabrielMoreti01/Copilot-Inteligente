import numpy as np
from sklearn.ensemble import RandomForestClassifier

from copiloto_app.config import CLASSES_IMAGEM

modelo_rf = RandomForestClassifier(n_estimators=100, random_state=42)
modelo_treinado = False


def decidir_acao(variaveis):
    if not modelo_treinado:
        tempo_viagem = variaveis[1]
        distancia = variaveis[2]
        emocao_conf = variaveis[4]

        if tempo_viagem > 150:
            return "DESCANSAR"
        if distancia > 200:
            return "ABASTECER"
        if emocao_conf > 0.85:
            return "VERIFICAR ESTADO DO MOTORISTA"
        return "CONTINUAR"

    entrada = np.array(variaveis).reshape(1, -1)
    return modelo_rf.predict(entrada)[0]


def montar_variaveis(hora_atual, tempo_viagem_min, distancia_percorrida, classe_img, confianca):
    indice_classe = CLASSES_IMAGEM.index(classe_img)
    return [hora_atual, tempo_viagem_min, distancia_percorrida, indice_classe, confianca]
