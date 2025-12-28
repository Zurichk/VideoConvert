"""
Módulo para la conversión de medios utilizando FFmpeg.
"""

import subprocess
import logging
import os
import shutil
from typing import Optional

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
AEP_FFMPEG_CMD = 'ffmpeg'


class AEPMediaConverter:
    """
    Clase encargada de la conversión de archivos de audio y video.
    """

    def __init__(self) -> None:
        """
        Inicializa el convertidor de medios y verifica que FFmpeg esté disponible.
        """
        self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """
        Verifica si FFmpeg está disponible en el sistema.

        Returns:
            True si FFmpeg está disponible, False en caso contrario.
        """
        if shutil.which(AEP_FFMPEG_CMD) is None:
            logger.error(
                "FFmpeg no está instalado o no está en el PATH. "
                "Descárgalo desde https://ffmpeg.org/download.html"
            )
            return False
        return True

    def convert_file(
        self,
        input_path: str,
        output_path: str,
        output_format: str,
        compress: bool = False
    ) -> bool:
        """
        Convierte un archivo de medios a otro formato.

        Args:
            input_path: Ruta absoluta del archivo de entrada.
            output_path: Ruta absoluta del archivo de salida.
            output_format: Formato de salida deseado (ej. 'mp3', 'mkv').
            compress: Si es True, aplica compresión básica.

        Returns:
            True si la conversión fue exitosa, False en caso contrario.
        """
        # Verificar que FFmpeg esté disponible
        if not self._check_ffmpeg():
            return False

        try:
            logger.info(f"Iniciando conversión: {input_path} -> {output_path}")

            command = [
                AEP_FFMPEG_CMD,
                '-y',  # Sobrescribir archivos de salida sin preguntar
                '-i', input_path
            ]

            # Configuración básica de compresión/calidad
            if compress:
                if output_format in ['mp4', 'mkv', 'avi', 'mov']:
                    # CRF 28 para compresión de video (calidad aceptable, menor peso)
                    command.extend(['-vcodec', 'libx264', '-crf', '28'])
                    # Audio AAC
                    command.extend(['-acodec', 'aac', '-b:a', '128k'])
                elif output_format in ['mp3']:
                    # Bitrate variable para MP3
                    command.extend(['-q:a', '5'])
            else:
                # Copia o defaults de ffmpeg si no se pide compresión explícita
                # Para video, usamos libx264 por compatibilidad general
                if output_format in ['mp4', 'mkv', 'avi']:
                     command.extend(['-c:v', 'libx264', '-c:a', 'aac'])

            command.append(output_path)

            # Ejecutar comando
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"Error en FFmpeg: {result.stderr}")
                return False

            logger.info("Conversión completada exitosamente.")
            return True

        except FileNotFoundError as e:
            logger.error(
                f"FFmpeg no encontrado. Asegúrate de tenerlo instalado: {str(e)}"
            )
            return False
        except Exception as e:
            logger.error(f"Excepción durante la conversión: {str(e)}")
            return False
