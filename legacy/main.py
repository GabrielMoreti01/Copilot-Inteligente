from datetime import datetime

from copiloto_app.config import PALAVRA_ATIVACAO, PONTOS_TURISTICOS
from copiloto_app.decision import decidir_acao, montar_variaveis
from copiloto_app.diary import diario, mostrar_resumo, registrar_diario
from copiloto_app.image_processing import capturar_imagem
from copiloto_app.location import identificar_ponto_turistico, obter_localizacao
from copiloto_app.voice import analisar_emocao, extrair_comando, ouvir_microfone


def mostrar_pontos_turisticos():
    print("\n")
    print("=" * 60)
    print("📍 PONTOS TURÍSTICOS DE INDAIATUBA")
    print("=" * 60)

    for nome, dados in PONTOS_TURISTICOS.items():
        print(f"• {dados['descricao']} → {dados['categoria']}")

    print("=" * 60)


def main():
    print("\n")
    print("=" * 60)
    print("🚗 COPILOTO INTELIGENTE DE VIAGEM")
    print("=" * 60)
    print(f"Palavra de ativação: \"{PALAVRA_ATIVACAO}\"")
    print("Cidade configurada: Indaiatuba - SP")
    print("\nExemplos de comandos:")
    print("• Ok Siri, registrar parada")
    print("• Ok Siri, marcar ponto turístico")
    print("• Ok Siri, preciso abastecer")
    print("• Ok Siri, como está o trecho")
    print("• encerrar viagem")
    mostrar_pontos_turisticos()

    try:
        while True:
            frase = ouvir_microfone()

            if not frase:
                continue

            if "encerrar viagem" in frase:
                mostrar_resumo()
                break

            if PALAVRA_ATIVACAO not in frase:
                print("🔇 Palavra de ativação não encontrada.")
                continue

            print("🔵 Palavra de ativação detectada!")
            comando_texto = extrair_comando(frase)

            if not comando_texto:
                print("⚠ Nenhum comando válido encontrado.")
                continue

            print(f"🗣 Comando reconhecido: {comando_texto}")

            lat, lon, nome_local = obter_localizacao()
            print(f"📍 Local atual: {nome_local}")

            foto, classe_img = capturar_imagem()
            emocao, confianca = analisar_emocao(frase)
            ponto_turistico = identificar_ponto_turistico(frase)

            hora_atual = datetime.now().hour
            tempo_viagem_min = len(diario) * 30
            distancia_percorrida = 150
            variaveis = montar_variaveis(hora_atual, tempo_viagem_min, distancia_percorrida, classe_img, confianca)
            decisao = decidir_acao(variaveis)

            registrar_diario(
                comando_texto=comando_texto,
                emocao=emocao,
                confianca=confianca,
                classe_img=classe_img,
                foto=foto,
                nome_local=nome_local,
                lat=lat,
                lon=lon,
                decisao=decisao,
                ponto_turistico=ponto_turistico,
            )

    except KeyboardInterrupt:
        print("\n\n🛑 Sistema encerrado pelo usuário.")
        mostrar_resumo()


if __name__ == "__main__":
    main()
