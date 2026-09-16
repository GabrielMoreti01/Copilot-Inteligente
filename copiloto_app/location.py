from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="copiloto_inteligente_indaiatuba")


def obter_localizacao():
    latitude = -23.0900
    longitude = -47.2180

    try:
        local = geolocator.reverse(f"{latitude}, {longitude}", language="pt-BR")
        if local:
            endereco = local.raw.get("address", {})
            cidade = endereco.get("city", endereco.get("town", "Indaiatuba"))
            nome_local = cidade
        else:
            nome_local = "Indaiatuba"
    except Exception:
        nome_local = "Indaiatuba"

    return latitude, longitude, nome_local


def identificar_ponto_turistico(frase):
    from copiloto_app.config import PONTOS_TURISTICOS

    frase = frase.lower()
    for nome, dados in PONTOS_TURISTICOS.items():
        if nome in frase:
            return dados["descricao"]
    return None
