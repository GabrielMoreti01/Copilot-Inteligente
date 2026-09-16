import os

import cv2

from copiloto_app.diary import fotos


def capturar_imagem():
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("⚠ Não foi possível acessar a câmera.")
        return None, "desconhecido"

    ret, frame = cam.read()
    cam.release()

    if not ret:
        print("⚠ Erro ao capturar imagem.")
        return None, "desconhecido"

    if not os.path.exists("fotos"):
        os.makedirs("fotos")

    caminho = os.path.join("fotos", f"registro_{len(fotos) + 1:03d}.jpg")
    cv2.imwrite(caminho, frame)
    fotos.append(caminho)

    classe = "natureza"
    return caminho, classe
