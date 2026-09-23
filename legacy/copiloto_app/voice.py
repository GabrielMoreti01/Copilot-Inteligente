import speech_recognition as sr


def ouvir_microfone():
    reconhecedor = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n🎧 Aguardando comando...")
        print("Fale: 'Ok Siri' + seu comando.")
        reconhecedor.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = reconhecedor.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("⏱ Nenhuma fala detectada.")
            return ""

    try:
        frase = reconhecedor.recognize_google(audio, language="pt-BR").lower()
        print("🗣 Você disse:", frase)
        return frase
    except sr.UnknownValueError:
        print("⚠ Não consegui entender o áudio.")
        return ""
    except sr.RequestError:
        print("⚠ Erro no serviço de reconhecimento de voz.")
        return ""


def extrair_comando(frase):
    from copiloto_app.config import COMANDOS

    for texto_comando in COMANDOS.keys():
        if texto_comando in frase:
            return texto_comando
    return None


def analisar_emocao(frase):
    if "cansado" in frase or "cansada" in frase:
        return "CANSADO", 0.82
    if "animado" in frase or "animada" in frase:
        return "ANIMADO", 0.80
    if "tenso" in frase or "tensa" in frase:
        return "TENSO", 0.78
    if "estressado" in frase or "estressada" in frase:
        return "ESTRESSADO", 0.85
    return "NEUTRO", 0.65
