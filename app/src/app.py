"""
Aplicación principal Flask para el convertidor de video.
"""

import os
import logging
import time
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converter import AEPMediaConverter

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
AEP_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AEP_UPLOAD_FOLDER = os.path.join(AEP_BASE_DIR, 'uploads')
AEP_PROCESSED_FOLDER = os.path.join(AEP_BASE_DIR, 'processed')
AEP_ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'mp3', 'wav', 'flac', 'ogg', 'webm'}
AEP_MAX_FILE_AGE_DAYS = 1

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'supersecretkey_change_this_in_production'

# Configuración de carpetas
app.config['UPLOAD_FOLDER'] = AEP_UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = AEP_PROCESSED_FOLDER

# Asegurar que existan los directorios
os.makedirs(AEP_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AEP_PROCESSED_FOLDER, exist_ok=True)

def cleanup_old_files() -> None:
    """
    Elimina archivos antiguos de las carpetas uploads y processed.
    
    Elimina archivos que tengan más de AEP_MAX_FILE_AGE_DAYS días
    de antigüedad para evitar acumulación en el servidor.
    """
    try:
        current_time = time.time()
        max_age_seconds = AEP_MAX_FILE_AGE_DAYS * 24 * 60 * 60
        
        folders_to_clean = [AEP_UPLOAD_FOLDER, AEP_PROCESSED_FOLDER]
        total_deleted = 0
        
        for folder in folders_to_clean:
            if not os.path.exists(folder):
                continue
                
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                
                if not os.path.isfile(file_path):
                    continue
                
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        total_deleted += 1
                        logger.info(
                            f"Archivo eliminado: {filename} "
                            f"(antigüedad: {file_age / 3600:.1f} horas)"
                        )
                    except OSError as e:
                        logger.error(
                            f"Error al eliminar {filename}: {str(e)}"
                        )
        
        if total_deleted > 0:
            logger.info(
                f"Limpieza completada: {total_deleted} archivo(s) eliminado(s)"
            )
        else:
            logger.debug("Limpieza completada: No hay archivos antiguos")
            
    except Exception as e:
        logger.error(f"Error durante la limpieza de archivos: {str(e)}")

# Configurar scheduler para limpieza automática
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=cleanup_old_files,
    trigger="interval",
    hours=1,
    id='cleanup_job',
    name='Limpieza de archivos antiguos'
)
scheduler.start()

# Ejecutar limpieza inicial al iniciar la app
cleanup_old_files()

logger.info("Scheduler de limpieza iniciado - Se ejecutará cada 1 hora")

def allowed_file(filename: str) -> bool:
    """
    Verifica si la extensión del archivo está permitida.

    Args:
        filename: Nombre del archivo.

    Returns:
        True si es válida, False si no.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in AEP_ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Renderiza la página principal.
    """
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_media():
    """
    Maneja la subida y conversión del archivo.
    """
    if 'file' not in request.files:
        flash('No se encontró el archivo en la petición.')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No se seleccionó ningún archivo.')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        target_format = request.form.get('format')
        compress_option = request.form.get('compress') == 'on'
        
        if not target_format:
            flash('Debe seleccionar un formato de destino.')
            return redirect(request.url)

        # Nombre del archivo de salida
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_converted.{target_format}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        
        converter = AEPMediaConverter()
        success = converter.convert_file(input_path, output_path, target_format, compress=compress_option)
        
        if success:
            flash('Conversión exitosa.')
            return render_template('index.html', download_file=output_filename)
        else:
            flash('Ocurrió un error durante la conversión.')
            return redirect(url_for('index'))
            
    else:
        flash('Tipo de archivo no permitido.')
        return redirect(request.url)

@app.route('/download/<filename>')
def download_file(filename: str):
    """
    Permite descargar el archivo procesado.

    Args:
        filename: Nombre del archivo a descargar.
    """
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Solo para desarrollo local
    try:
        app.run(host='0.0.0.0', port=5048, debug=True)
    finally:
        # Detener el scheduler al cerrar la app
        scheduler.shutdown()
