# Memoria: Despliegue de un modelo de IA como servicio

## 1. Diseño de los Servicios (Punto 2)

Para esta práctica he diseñado un sistema basado en microservicios compuesto por dos partes principales:

### Servicio de IA (Python)
He utilizado **FastAPI** para crear este servicio porque es rápido y bastante sencillo de configurar. Este servicio es el corazón de la aplicación, ya que se encarga de cargar nuestro modelo de IA pre-entrenado (en formato `.keras`) y procesar las imágenes que le pasamos para devolver las predicciones.
También le he añadido validación de los datos de entrada usando **Pydantic**, y he implementado bloques `try/except` y `logging` para poder registrar cuándo se hacen las peticiones o si ha habido algún fallo (devolviendo el código HTTP correspondiente).

📝 *[AQUÍ AÑADIR CAPTURA DEL CÓDIGO DE FASTAPI / MAIN.PY]*

### Servicio Intermediario / Proxy (Node.js)
El proxy actúa como la puerta de entrada para el cliente, aislando así el servicio principal de Python. Lo he creado usando **Express** con Node.js. 
Este servidor es el que recibe todas las peticiones desde el exterior y se las pasa a la IA. Le he añadido su propio logging para registrar el método HTTP y las rutas, y también bloque `try/catch` para que, si el servicio de IA se colgara por algún motivo, el proxy siga respondiendo con un error HTTP 500 en lugar de romperse.

📝 *[AQUÍ AÑADIR CAPTURA DEL CÓDIGO DE NODE.JS / INDEX.JS]*

## 2. Comunicación entre servicios (Punto 3)

Ambos microservicios se comunican mediante una API REST usando el formato JSON. El funcionamiento es el siguiente:
1. El usuario hace una petición `POST` al proxy (puerto 3000) mandando la información.
2. El proxy intercepta esto, apunta el log y reenvía los datos al servicio de IA (puerto 8000) que tengamos en las variables de entorno, usando `axios`.
3. El servicio de Python procesa los datos, usa el modelo para la predicción y le devuelve el archivo JSON al proxy.
4. Para acabar, el proxy devuelve esta respuesta final al usuario.

📝 *[AQUÍ AÑADIR CAPTURA DE UNA PETICIÓN EN POSTMAN O LA TERMINAL MOSTRANDO QUE FUNCIONA]*

## 3. Contenerización (Punto 4)

Para que el sistema funcione en cualquier parte, todo está metido en contenedores Docker. 
He creado un `Dockerfile` para cada uno de los servicios (uno con `python:3-slim` y el otro con `node:18-slim`). Además, para juntarlo todo, tengo un archivo `docker-compose.yaml` que se encarga de:
- Levantar ambos servicios a la vez.
- Crear una red interna para que Node.js encuentre a Python solo utilizando el nombre del contenedor.
- Asegurarse de que el proxy no arranca hasta que el servicio de IA esté 100% levantado (`depends_on`).

📝 *[AQUÍ AÑADIR CAPTURA DEL DOCKER-COMPOSE.YAML O UNA TERMINAL HACIENDO UN `docker compose up`]*