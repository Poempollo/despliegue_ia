import requests
import base64
import json

def test_prediction():
    # 1. Leemos la imagen y la pasamos a base64
    with open("diente.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 2. Preparamos el JSON
    payload = {
        "image_base64": encoded_string
    }

    # 3. Enviamos la petición AL PROXY (puerto 3000), el cual lo reenviará a la IA
    print("Enviando imagen al proxy...")
    response = requests.post(
        "http://localhost:3000/get-prediction",
        json=payload
    )

    print("Respuesta recibida:")
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    test_prediction()