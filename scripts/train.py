"""Synthetic educational dataset; grouped split; real RF training."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import random
import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from copiloto_app.decision import FEATURES
from copiloto_app.settings import ROOT, SCENES, EMOTIONS


def label(row):
    if row['tempo_sem_parada_min'] >= 120 or (row['emocao'] == 'IRRITADO' and row['confianca_emocao'] >= .6):
        return 'DESCANSAR'
    if row['classe_imagem'] == 'posto de combustível' and row['distancia_km'] >= 120:
        return 'AVALIAR ABASTECIMENTO'
    if row['classe_imagem'] == 'restaurante' and 11 <= row['hora'] <= 14:
        return 'ALIMENTAR-SE'
    if row['classe_imagem'] in ['natureza', 'ponto turístico'] and row['emocao'] == 'ANIMADO':
        return 'REGISTRAR PONTO TURÍSTICO'
    return 'CONTINUAR'


def train(output=ROOT / 'models/decision.joblib', data_dir=ROOT / 'data', docs=ROOT / 'docs'):
    rng = random.Random(42)
    rows, groups = [], []
    for group in range(800):
        base = dict(hora=rng.randrange(24), tempo_viagem_min=rng.uniform(5, 360), distancia_km=rng.uniform(0, 400),
                    confianca_emocao=rng.uniform(.35, .95), paradas=rng.randrange(5),
                    classe_imagem=rng.choice(SCENES + ['desconhecido']), emocao=rng.choice(EMOTIONS))
        base['tempo_sem_parada_min'] = rng.uniform(0, base['tempo_viagem_min'])
        # Enrich rare contexts before splitting; labels still come from the same
        # explicit policy. No duplicated rows or shared groups across splits.
        if group % 5 == 0:
            base.update(hora=rng.randint(11, 14), classe_imagem='restaurante', emocao='NEUTRO',
                        tempo_sem_parada_min=min(base['tempo_viagem_min'], rng.uniform(0, 90)))
        elif group % 5 == 1:
            base.update(classe_imagem=rng.choice(['natureza', 'ponto turístico']), emocao='ANIMADO',
                        tempo_sem_parada_min=min(base['tempo_viagem_min'], rng.uniform(0, 90)))
        for variant in range(3):
            row = dict(base)
            row['distancia_km'] = round(max(0, base['distancia_km'] + rng.uniform(-5, 5)), 3)
            row['tempo_sem_parada_min'] = round(min(base['tempo_viagem_min'], max(0, base['tempo_sem_parada_min'] + rng.uniform(-5, 5))), 3)
            rows.append(row)
            groups.append(group)
    y = [label(r) for r in rows]
    train_ids, test_ids = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=42).split(rows, y, groups))
    vectorizer = DictVectorizer(sparse=False)
    x_train = vectorizer.fit_transform([rows[i] for i in train_ids])
    x_test = vectorizer.transform([rows[i] for i in test_ids])
    forest = RandomForestClassifier(n_estimators=120, min_samples_leaf=2, class_weight='balanced', random_state=42, n_jobs=1)
    forest.fit(x_train, [y[i] for i in train_ids])
    predictions = forest.predict(x_test)
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    version = 'rf-sintetico-v1-' + digest[:12]
    output, data_dir, docs = Path(output), Path(data_dir), Path(docs)
    for directory in [output.parent, data_dir, docs]:
        directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(dict(forest=forest, vectorizer=vectorizer, features=FEATURES, version=version), output)
    test_set = set(test_ids.tolist())
    with (data_dir / 'cenarios_sinteticos.csv').open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['grupo', 'split', *FEATURES, 'decisao', 'origem'])
        writer.writeheader()
        for i, row in enumerate(rows):
            writer.writerow(dict(grupo=groups[i], split='teste' if i in test_set else 'treino', **row, decisao=y[i], origem='sintetico'))
    report = dict(version=version, dataset_sha256=digest, seed=42, rows=len(rows), train=len(train_ids), test=len(test_ids),
                  group_overlap=len(set(groups[i] for i in train_ids) & set(groups[i] for i in test_ids)),
                  distribution=dict(Counter(y)), classes=forest.classes_.tolist(),
                  report=classification_report([y[i] for i in test_ids], predictions, output_dict=True, zero_division=0),
                  confusion_matrix=confusion_matrix([y[i] for i in test_ids], predictions, labels=forest.classes_).tolist(),
                  limitation='Cenários sintéticos rotulados por regras. Não comprova desempenho em viagens reais.')
    (docs / 'metricas.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'version': version, 'test_accuracy': report['report']['accuracy'], 'group_overlap': report['group_overlap']}))
    return report


if __name__ == '__main__':
    train()
