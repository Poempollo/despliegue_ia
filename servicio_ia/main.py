from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Configuración de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-service")

app = FastAPI()

# Validación de datos con Pydantic
class PredictRequest(BaseModel):
    data: list[float]

@app.get("/")
def read_root():
    return {"status": "AI Service Running"}

@app.post("/predict")
async def predict(request: PredictRequest):
    try:
        logger.info(f"Procesando datos: {request.data}")
        
        # Simulación del modelo de IA
        if not request.data:
            raise ValueError("La lista de datos está vacía")
        
        prediction = sum(request.data) / len(request.data) # Un promedio simple
        
        return {"prediction": prediction}
    
    except Exception as e:
        logger.error(f"Error en la predicción: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))