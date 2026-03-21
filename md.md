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

**Mejora implementada B: Monitorización de Métricas de Uso.**
He incorporado un nuevo endpoint en el servidor Intermediario de Node.js: `GET /metrics`. Este endpoint recopila de forma viva la volumetría de uso del servidor y te devuelve un recuento de cuántas peticiones HTTP totales se han procesado, cuántas han acabado en éxito y cuántas han sido fallidas desde la última vez que se arrancó el servidor. Es muy útil como primer paso simulando monitorización con herramientas en la nube.

📝 *[AQUÍ AÑADIR CAPTURA HACIENDO UN GET A HTTP://LOCALHOST:3000/METRICS EN TU NAVEGADOR O POSTMAN]*

**Mejora implementada C: Endpoint de Información del Modelo.**
Para facilitar la escalabilidad ("¿oye, de qué era este contenedor de IA que subí ayer?"), he añadido un endpoint transparente al servicio de IA que devuelve los metadatos de qué modelo concreto está montado.
Si el usuario hace un `GET /model-info` hacia el proxy (que a su vez enruta a FastAPI), la API de Python te devuelve la descripción (en este caso indicando "MobileNetV2").

📝 *[AQUÍ AÑADIR CAPTURA HACIENDO GET A HTTP://LOCALHOST:3000/MODEL-INFO]*

## 5. Despliegue en Kubernetes (Punto 5 y 6)

Para llevar el proyecto a un entorno profesional y altamente escalable, he migrado toda la orquestación hacia Kubernetes (usando **Minikube** en mi entorno de desarrollo local).

Se ha creado una carpeta `/k8s` donde he definido los **manifestos YAML** correspondientes para ambos servicios. El despliegue incluye lo siguiente:

### Despliegues, Servicios y Comunicación
- **servicio-ia-deployment y servicio-ia (Service):**
  Este bloque despliega nuestro backend en Python de manera interna en el Clúster usando un servicio de tipo `ClusterIP`. Esto es importante por seguridad, ya que aísla las IAs del exterior. Solo el proxy puede comunicarse con él a través del nombre de host de DNS interno `servicio-ia`.
- **servicio-proxy-deployment y servicio-proxy (Service):**
  Nuestro gateway en Node.js que se encarga de dar la cara al público. Lo he expuesto como tipo `NodePort` (Puerto 30000) para poder acceder a la API desde Postman en mi red local de Windows. Además, en este archivo YAML se declaran explícitamente las *Environment Variables* para que Node sepa dónde encontrar la API de Python.

### Escalabilidad Horizontal y Réplicas
Para cumplir con las pruebas de autoescalado y soporte a múltiples peticiones simultáneas, he configurado el despliegue del **Servicio de IA con 2 Réplicas (`replicas: 2`)** dentro del YAML.
Esto significa que Kubernetes levanta activamente y mantiene vivos dos Pods paralelos con el modelo keras cargado. El *Service* interno se encarga automáticamente de actuar como balanceador de carga utilizando *Round Robin*, de forma que cada vez que el proxy manda una imagen nueva a procesar, el trabajo se reparte entre los dos pods, logrando así tolerancia a fallos y doble de velocidad de respuesta con múltiples usuarios.

📝 *[AQUÍ AÑADIR CAPTURA EN TERMINAL DESPUÉS DE EJECUTAR TUS YAML CON KUBECTL MOSTRANDO LOS DOS PODS DE LA IA ARRANCADOS Y RUNNING (`kubectl get pods` y `kubectl get services`).]*

**Comprobación de fallos:**
Como prueba final, con el clúster arrancado, he mandado una petición errónea a propósito para confirmar la robustez (se devuelve el error controlado pertinente), y peticiones válidas continuadas para validar el escalado entre los pods de Python.

📝 *[AQUÍ AÑADIR CAPTURA DE POSTMAN TIRANDO AL PUERTO: `http://localhost:30000/get-prediction` Y RECIBIENDO LA RESPUESTA CON ÉXITO.]*
