from datetime import datetime


diario = []
fotos = []


def registrar_diario(
    comando_texto,
    emocao,
    confianca,
    classe_img,
    foto,
    nome_local,
    lat,
    lon,
    decisao,
    ponto_turistico=None,
):
    registro = {
        "horario": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "local": nome_local,
        "coords": (lat, lon),
        "comando": comando_texto,
        "emocao": emocao,
        "confianca_emocao": round(confianca * 100, 1),
        "classe_imagem": classe_img,
        "foto": foto,
        "decisao": decisao,
        "ponto_turistico": ponto_turistico,
    }

    diario.append(registro)

    print("\n")
    print("=" * 60)
    print(f"📘 DIÁRIO DE BORDO · Registro {len(diario):03d}")
    print("=" * 60)
    print(f"Horário: {registro['horario']}")
    print(f"Local: {registro['local']}")
    print(f"Coordenadas: {lat}, {lon}")
    print(f"Comando reconhecido: \"{registro['comando']}\"")
    print(f"Estado da voz: {registro['emocao']} — {registro['confianca_emocao']}%")
    print(f"Imagem classificada: {registro['classe_imagem']}")
    if ponto_turistico:
        print(f"📍 Ponto turístico: {ponto_turistico}")
    print(f"🤖 Decisão do sistema: {registro['decisao']}")
    print(f"📷 Foto associada: {registro['foto']}")
    print("=" * 60)


def mostrar_resumo():
    if not diario:
        print("\nNenhum registro foi realizado.")
        return

    import numpy as np

    distancia_total = np.random.randint(50, 400)
    paradas = len(diario)
    locais_registrados = len(set(d["local"] for d in diario))
    emocao_predominante = max(set(d["emocao"] for d in diario), key=[d["emocao"] for d in diario].count)
    maior_trecho_sem_parada = np.random.randint(30, 150)

    print("\n")
    print("=" * 60)
    print("🚗 RESUMO DA VIAGEM")
    print("=" * 60)
    print(f"Distância total: {distancia_total} km")
    print(f"Paradas realizadas: {paradas}")
    print(f"Locais registrados: {locais_registrados}")
    print(f"Emoção predominante: {emocao_predominante}")
    print(f"Maior trecho sem parada: {maior_trecho_sem_parada} km")
    print("\n📷 Fotos em ordem cronológica:")

    for registro in diario:
        print(f"- {registro['horario']} | {registro['local']} | {registro['foto']} | {registro['decisao']}")

    print("=" * 60)
