from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
import io
import base64
import numpy as np
from pydantic import BaseModel
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions

# Configuración de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("servicio_ia")

app = FastAPI()

# --- CARGA DEL MODELO .KERAS ---
logger.info("Cargando modelo de clasificación de imágenes desde .keras...")
try:
    # Nos aseguramos de que el archivo del modelo esté en el mismo directorio (servicio_ia)
    modelo = load_model("modelo_clasificacion.keras")
    logger.info("Modelo .keras cargado y listo.")
except Exception as e:
    logger.error(f"Error al cargar el modelo: {e}")
    modelo = None

class ImageRequest(BaseModel):
    image_base64: str

@app.get("/")
def read_root():
    return {"status": "Servicio de IA en funcionamiento con modelo .keras"}

@app.post("/predict")
async def predict(request: ImageRequest):
    if modelo is None:
        raise HTTPException(status_code=500, detail="El modelo no está cargado en el servidor.")

    try:
        logger.info("Procesando imagen recibida...")
        
        # 1. Leer los bytes decodificados y cargar como imagen PIL
        try:
            image_data = base64.b64decode(request.image_base64)
            img = Image.open(io.BytesIO(image_data)).convert("RGB")
            img = img.resize((224, 224))
        except Exception as img_e:
            raise ValueError(f"No es una imagen base64 válida: {img_e}")

        # 2. Preprocesar la imagen
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) # Añadir dimensión batch
        img_preprocesada = preprocess_input(img_array)

        # 3. Predicción usando el modelo de Keras
        predicciones = modelo.predict(img_preprocesada)
        
        # Decodificar el top 3 de predicciones
        resultados_decodificados = decode_predictions(predicciones, top=3)[0]

        resultados_limpios = []
        for _, etiqueta, probabilidad in resultados_decodificados:
            resultados_limpios.append({
                "clase": etiqueta,
                "confianza": float(probabilidad)
            })

        return {
            "estado": "éxito",
            "predicciones": resultados_limpios
        }
    
    except Exception as e:
        logger.error(f"Error en la predicción: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))