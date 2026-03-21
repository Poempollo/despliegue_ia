# Memoria: Despliegue de un modelo de IA como servicio

## 1. Diseño y Descripción de la Tarea (Punto 2)

Para esta práctica he diseñado un ecosistema basado en microservicios compuesto por dos partes principales:

### Servicio de IA (Python)
He utilizado **FastAPI** para crear este servicio porque es un framework rápido y robusto. Este servicio es el corazón de la aplicación, ya que se encarga de cargar nuestro modelo de IA pre-entrenado (directamente desde el archivo `modelo_clasificacion.keras`) y procesar las imágenes que le pasamos para devolver el Top 3 de predicciones.
Además, le he añadido:
- **Validación de datos:** He implementado **Pydantic** para obligar a que el JSON de entrada tenga el campo correcto (`image_base64`).
- **Manejo de excepciones:** Todo el código principal está protegido con bloques `try/except`. Si, por ejemplo, la imagen subida está corrupta, el servidor no casca, sino que devuelve de forma limpia un error HTTP (Status 400 o 500).
- **Logging:** He puesto logs clave (`logger.info` y `logger.error`) para que en la terminal del contenedor quede guardado cada vez que el modelo se carga y cada vez que llega una imagen a procesar.

📝 *[AQUÍ AÑADIR CAPTURA DEL CÓDIGO DE FASTAPI / MAIN.PY Y OTRA CAPTURA DONDE SE VEA EL ARCHIVO MODELO_CLASIFICACION.KERAS EN LA CARPETA]*

### Servicio Intermediario / Proxy (Node.js)
El proxy actúa como la puerta de entrada para el cliente, aislando así el servicio principal de Python de internet. Lo he creado usando **Express.js**. 
Su función es sencilla: escuchar en los puertos externos, y reenviar el paquete a nuestra IA interna.
- **Logging:** Cuenta con un middleware que imprime por consola cada petición HTTP que entra.
- **Manejo de excepciones:** Utiliza `try/catch`. Si el servicio de IA devolviese un fallo, el proxy no se rompe, sino que se captura e imprime el log internamente y avisa al cliente de que hubo un problema.

📝 *[AQUÍ AÑADIR CAPTURA DEL CÓDIGO DE NODE.JS / INDEX.JS]*

## 2. Comunicación entre servicios (Punto 3)

Ambos microservicios se comunican de forma síncrona mediante una API REST usando el formato **JSON**. El funcionamiento y flujo es el siguiente:
1. **Cliente:** El usuario hace una petición `POST` mandando un JSON con la imagen codificada en formato Base64.
2. **Proxy:** El servidor en Node.js recibe la petición en el puerto `3000`. Registra el acceso mediante el logging, y reenvía el JSON completo al contenedor del backend haciendo uso de `axios`. (Utiliza variables de entorno para encontrar automáticamente a la IP y puerto de la IA).
3. **Servicio de IA:** FastAPI en el puerto `8000` intercepta este texto Base64, lo verifica, lo decodifica de vuelta a la imagen original en memoria viva y se lo pasa a nuestro modelo Keras para realizar las predicciones.
4. **Respuesta:** La IA devuelve al Node.js un JSON final. Node.js le introduce la firma `"source": "Intermediary Service"` y se lo devuelve al usuario.

📝 *[AQUÍ METER OTRA CAPTURA DE POSTMAN, O DE TU SCRIPT DE NODE, MOSTRANDO LA RESPUESTA CORRECTA CON EL "Source"]*

## 3. Contenerización (Punto 4)

El sistema está empaquetado al 100% utilizando Docker.
He creado dos **Dockerfiles** y un archivo principal **docker-compose.yaml**.
- El contenedor del proxy usa una imagen muy pequeña (`node:18-slim`).
- El servicio de IA está basado en `python:3.10-slim`. Ojo, para la IA ha hecho falta añadir el peso de *TensorFlow* a las requirements.
- El archivo `docker-compose.yaml` es el director de orquesta: se encarga de que ambos contenedores se levanten simultáneamente, les reasigna puertos y, lo más importante, crea por debajo una red interna virtual de Docker permitiendo que el contenedor proxy se comunique mediante DNS (usando el nombre de host `servicio_ia`) de forma mucho más limpia.

📝 *[AQUÍ AÑADIR CAPTURA DEL DOCKER-COMPOSE.YAML O UNA TERMINAL HACIENDO `docker ps`]*

## 4. Mejora Adicional (Punto 7)

**Mejora implementada: Autenticación.**

Para completar la práctica, he mejorado la seguridad del servicio intermediario (el proxy) añadiéndole un control de autenticación mediante un *Token API Key*. 
En el archivo de proxy he añadido un middleware que intercepta cada una de las peticiones a la ruta `/get-prediction` y comprueba obligatoriamente si el usuario ha entregado en los *Headers (cabeceras)* la clave `x-api-key: secreto123`.

- Si el usuario **no** la provee, o es errónea, el proxy rechaza inmediatamente con un error 401 Unauthorized sin llegar siquiera a despertar al servicio de Python.
- Si el usuario aporta la cabecera correcta, la petición pasa, la imagen se envía al servicio de IA, y de ahí al flujo normal finalizado. 

📝 *[AQUÍ AÑADIR CAPTURA EN POSTMAN U OTRO TERMINAL QUE DEMUESTRE UNA RESPUESTA AUTORIZADA, Y LUEGO OTRA DONDE DE EL ERROR 401 POR NO LLEVAR LA KEY CORRECTA]*

## 5. Despliegue en Kubernetes (Punto 5 y 6)

*(A completar...)*
