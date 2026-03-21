const fs = require('fs');

async function check() {
    console.log("Leyendo imagen...");
    const imageBase64 = fs.readFileSync("coche.jpg", { encoding: 'base64' });

    console.log("Enviando petición al proxy (puerto 3000)...");
    const response = await fetch("http://localhost:30000/get-prediction", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "x-api-key": "secreto123" // Pasando la clave de la Mejora
        },
        body: JSON.stringify({ image_base64: imageBase64 })
    });

    const data = await response.json();
    console.log("Respuesta:");
    console.log(JSON.stringify(data, null, 2));
}

check();