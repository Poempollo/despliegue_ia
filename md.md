# Resumen de Progreso: Despliegue de un Modelo de IA como Servicio

Hasta el momento, hemos completado las fases de desarrollo base, comunicación y contenerización (Puntos del 1 al 4 de la práctica). A continuación se detalla cómo se ha implementado cada apartado.

## 1. Diseño de los Servicios (Punto 2)

Se ha optado por una arquitectura de microservicios compuesta por dos piezas principales:

### Servicio de IA (Python)
- **Framework:** Se ha construido utilizando **FastAPI**, un framework moderno y rápido para construir APIs en Python.
- **Lógica e IA:** Actualmente, el modelo de IA está simulado mediante una función matemática (calcula el promedio de una lista de números). Esta aproximación ha permitido validar toda la arquitectura del sistema antes de integrar el modelo definitivo de imágenes.
- **Validación de datos:** Todo el tipado y validación de entrada se maneja de forma automática con **Pydantic**. El servicio espera recibir estrictamente una lista de números flotantes (ej. `{"data": [10.5, 20.0]}`).
- **Robustez:** Se ha implementado el módulo estándar de `logging` para registrar cuándo se procesan datos o si ocurre algún fallo. Además, incluye manejo de excepciones (bloque `try/except`) para devolver errores HTTP claros (Status 400) si fallan las validaciones internas.

### Servicio Intermediario / Proxy (Node.js)
- **Framework:** Implementado en Node.js utilizando **Express**.
- **Función:** Actúa como la puerta de entrada (API Gateway) para el cliente, aislando el servicio de IA del exterior.
- **Características:** 
  - Cuenta con un *middleware* de logging que registra todas las rutas solicitadas y el método HTTP.
  - Utiliza `axios` para redirigir las peticiones internamente al servicio de Python.
  - Dispone de un bloque `try/catch` para interceptar cualquier fallo de comunicación o caída del servicio de IA, devolviendo un error HTTP 500 controlado al cliente en lugar de colgarse.

## 2. Comunicación entre Servicios (Punto 3)

La comunicación entre el cliente, el proxy y el servicio de IA se realiza mediante **HTTP (REST)** utilizando el formato **JSON**.

**Flujo de la información:**
1. **Cliente:** Realiza una petición `POST` al endpoint `/get-prediction` del proxy (puerto 3000), enviando el JSON de entrada.
2. **Proxy:** Recibe la petición, registra la entrada y reenvía el mismo *payload* hacia el servicio interno de IA. La ruta interna se configura mediante variables de entorno (`process.env.IA_URL`), lo que permite que sea dinámico.
3. **Servicio de IA:** Recibe los datos por el puerto 8000, los valida, procesa la "predicción" y devuelve un JSON al proxy.
4. **Respuesta final:** El proxy recibe el resultado y lo empaqueta añadiendo un metadato (`source: 'Intermediary Service'`) antes de entregarlo al usuario final.

## 3. Contenerización (Punto 4)

El sistema está completamente contenerizado para asegurar que puede ejecutarse de forma aislada e independiente en cualquier entorno.

- **Dockerfiles:** Se ha creado un contenedor a medida para cada servicio partiendo de imágenes ligeras (`python:3-slim` y `node:18-slim`) para optimizar el peso y tiempo de despliegue. En el de Python, además, se ha configurado un usuario no-root por motivos de seguridad.
- **Orquestación con Docker Compose:** Se ha definido un archivo `docker-compose.yaml` que:
  - Levanta y empaqueta ambos servicios.
  - Asegura que el servicio de Node.js no arranque hasta que la IA esté lista (`depends_on`).
  - Crea una red virtual interna de Docker que permite a los servicios encontrarse por su nombre (el proxy busca a la máquina `servicio_ia` directamente, sin usar IPs estáticas).
  - Expone los puertos (3000 para Node, 8000 para Python) hacia la máquina host (nuestro ordenador).

## 4. Pruebas de Funcionamiento Actuales

Se ha verificado el correcto funcionamiento del ecosistema levantando los contenedores:
```bash
docker compose up --build