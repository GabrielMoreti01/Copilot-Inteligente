"""One feature contract shared by training and inference."""
from functools import lru_cache
import joblib
import numpy as np
from copiloto_app.settings import MODEL_PATH

NUMERIC = ['hora', 'tempo_viagem_min', 'distancia_km', 'confianca_emocao', 'paradas', 'tempo_sem_parada_min']
CATEGORICAL = ['classe_imagem', 'emocao']
FEATURES = NUMERIC + CATEGORICAL


@lru_cache(maxsize=4)
def load_model(path=str(MODEL_PATH)):
    artifact = joblib.load(path)  # Only locally trained, trusted artifacts.
    if artifact['features'] != FEATURES:
        raise ValueError('Contrato incompatível. Treine novamente.')
    return artifact


def predict(features, path=str(MODEL_PATH)):
    artifact = load_model(path)
    row = {k: features.get(k, 'desconhecido' if k in CATEGORICAL else 0) for k in FEATURES}
    vector = artifact['vectorizer'].transform([row])
    forest = artifact['forest']
    probabilities = forest.predict_proba(vector)[0]
    index = int(np.argmax(probabilities))
    names = artifact['vectorizer'].get_feature_names_out()
    contributions = np.zeros(vector.shape[1])
    baseline = 0.0
    for estimator in forest.estimators_:
        tree = estimator.tree_
        values = tree.value[:, 0, :]
        values = values / values.sum(axis=1, keepdims=True)
        baseline += values[0, index] / len(forest.estimators_)
        node = 0
        while tree.children_left[node] != tree.children_right[node]:
            feature = tree.feature[node]
            child = tree.children_left[node] if vector[0, feature] <= tree.threshold[node] else tree.children_right[node]
            contributions[feature] += (values[child, index] - values[node, index]) / len(forest.estimators_)
            node = child
    grouped = {}
    for name, value in zip(names, contributions):
        key = name.split('=')[0]
        grouped[key] = grouped.get(key, 0.0) + float(value)
    return {'acao': str(forest.classes_[index]), 'score': float(probabilities[index]), 'origem': 'random_forest',
            'modelo': artifact['version'], 'entradas': row,
            'explicacao': {'base': baseline, 'contribuicoes': grouped,
                          'metodo': 'Decomposição local dos caminhos das árvores: base + contribuições = score. Não representa causalidade ou probabilidade calibrada.'}}
