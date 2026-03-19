const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

const IA_URL = process.env.IA_URL || 'servicio_ia';
const IA_PORT = process.env.IA_PORT || '8000';

app.use(express.json());

// Logging básico (Pedido en la práctica)
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

app.post('/get-prediction', async (req, res) => {
    try {
        // "ai-service" será el nombre del contenedor en la red de Docker
        const aiResponse = await axios.post(`http://${IA_URL}:${IA_PORT}/predict`, req.body);
        
        res.json({
            source: 'Intermediary Service',
            prediction: aiResponse.data.prediction
        });
    } catch (error) {
        // Manejo de excepciones (Pedido en la práctica)
        console.error("Error contactando con el servicio de IA:", error.message);
        res.status(500).json({ error: 'Error en la comunicación con IA', detail: error.message });
    }
});

app.listen(port, () => {
    console.log(`Intermediario escuchando en http://localhost:${port}`);
});