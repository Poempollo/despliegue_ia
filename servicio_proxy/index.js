const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

const IA_URL = process.env.IA_URL || 'servicio_ia';
const IA_PORT = process.env.IA_PORT || '8000';
const API_KEY = process.env.API_KEY || 'secreto123'; // Mejora: Clave para la API

// Variables para la Mejora de Métricas de Monitorización
let metrics = {
    total_peticiones_recibidas: 0,
    predicciones_exitosas: 0,
    predicciones_fallidas: 0,
    fecha_inicio_servidor: new Date().toISOString()
};

app.use(express.json({ limit: '50mb' }));

// Logging básico y Tracker de métricas
app.use((req, res, next) => {
    metrics.total_peticiones_recibidas++;
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

// Autenticación básica
app.use((req, res, next) => {
    // Solo protegemos la ruta de predicción
    if (req.url === '/get-prediction') {
        const key = req.headers['x-api-key'];
        if (!key || key !== API_KEY) {
            console.warn("Intento de acceso bloqueado: API Key inválida o faltante.");
            return res.status(401).json({ error: 'Acceso denegado. Proporciona una API Key válida en el header x-api-key.' });
        }
    }
    next();
});

app.post('/get-prediction', async (req, res) => {
    try {
        const aiResponse = await axios.post(`http://${IA_URL}:${IA_PORT}/predict`, req.body);
        metrics.predicciones_exitosas++; // Registrar éxito
        
        res.json({
            source: 'Intermediary Service',
            data: aiResponse.data
        });
    } catch (error) {
        metrics.predicciones_fallidas++; // Registrar fallo
        console.error("Error contactando con el servicio de IA:", error.message);
        res.status(500).json({ error: 'Error en la comunicación con IA', detail: error.message });
    }
});

// Endpoint para consultar las métricas (Mejora)
app.get('/metrics', (req, res) => {
    res.json(metrics);
});

// Endpoint para consultar información del modelo IA subyacente (Mejora)
app.get('/model-info', async (req, res) => {
    try {
        const aiResponse = await axios.get(`http://${IA_URL}:${IA_PORT}/model-info`);
        res.json({
            origen: "Gateway Express",
            datos_modelo: aiResponse.data
        });
    } catch (error) {
        res.status(500).json({ error: "No se pudo obtener información del modelo en el backend." });
    }
});

app.listen(port, () => {
    console.log(`Intermediario escuchando en http://localhost:${port}`);
});