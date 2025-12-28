# VideoConvert App

Aplicación web moderna para convertir formatos de audio y video, construida con Python Flask y FFmpeg.

## Características

- Conversión de video: MP4, MKV, AVI, MOV, WEBM.
- Conversión de audio: MP3, WAV, FLAC, OGG.
- Opción de compresión para reducir el tamaño del archivo.
- Interfaz web moderna y fácil de usar.
- Listo para desplegar con Docker.

## Requisitos Previos

- Python 3.11+
- FFmpeg instalado en el sistema (para ejecución local).
- Docker (opcional, para despliegue).

## Instalación y Ejecución Local

1.  **Clonar el repositorio y navegar a la carpeta:**
    ```bash
    cd VideoConvert
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    python -m app.src.app
    ```
    La aplicación estará disponible en `http://localhost:5048`.

## Despliegue con Docker (Coolify / VPS)

La aplicación incluye un `Dockerfile` optimizado.

1.  **Construir la imagen:**
    ```bash
    docker build -t videoconvert .
    ```

2.  **Ejecutar el contenedor:**
    ```bash
    docker run -p 5048:5048 videoconvert
    ```

## Estructura del Proyecto

```
VideoConvert/
├── app/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── app.py              # Aplicación Flask principal
│   │   └── converter.py        # Lógica de conversión con FFmpeg
│   ├── templates/
│   │   └── index.html          # Interfaz web moderna
│   ├── static/
│   │   └── css/                # Archivos CSS (si los hay)
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_converter.py  # Pruebas unitarias
│   ├── uploads/                # Archivos temporales subidos
│   ├── processed/              # Archivos convertidos
│   └── __init__.py
├── Dockerfile                  # Configuración Docker
├── requirements.txt            # Dependencias Python
├── .gitignore                  # Archivos ignorados por Git
└── README.md                   # Este archivo
```

## Pruebas

Para ejecutar las pruebas unitarias:

```bash
python -m unittest discover app/tests
```
