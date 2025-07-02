import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Obtener la ruta de montaje desde la variable de entorno.
MOUNT_PATH = os.getenv('MOUNT_PATH', '/mnt/azure')

def get_absolute_path(path):
    """Construye una ruta absoluta y segura dentro del volumen montado."""
    requested_path = os.path.join(MOUNT_PATH, path)
    abs_path = os.path.normpath(os.path.realpath(requested_path))
    
    if not abs_path.startswith(os.path.realpath(MOUNT_PATH)):
        abort(403) # Prohibido
    return abs_path

@app.route('/')
@app.route('/<path:path>')
def index(path=''):
    """Muestra los archivos y carpetas para una ruta dada."""
    current_path = get_absolute_path(path)
    
    if not os.path.exists(current_path) or not os.path.isdir(current_path):
        abort(404) # No encontrado

    items = []
    for item_name in sorted(os.listdir(current_path)):
        item_path = os.path.join(current_path, item_name)
        item_type = 'dir' if os.path.isdir(item_path) else 'file'
        items.append({'name': item_name, 'type': item_type, 'path': os.path.join(path, item_name)})

    breadcrumbs = [{'name': 'Inicio', 'path': ''}]
    if path:
        parts = path.split('/')
        for i, part in enumerate(parts):
            breadcrumbs.append({'name': part, 'path': '/'.join(parts[:i+1])})

    return render_template('index.html', items=items, current_path=path, breadcrumbs=breadcrumbs)

@app.route('/upload/', methods=['POST'])
@app.route('/upload/<path:path>', methods=['POST'])
def upload_file(path=''):
    """Maneja la subida de archivos."""
    current_path = get_absolute_path(path)
    
    if 'file' not in request.files:
        return redirect(url_for('index', path=path))
        
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index', path=path))

    if file:
        try:
            filename = secure_filename(file.filename)
            # --- INICIO DE LA CORRECCIÓN ---
            # Asegurarse de que el directorio de destino existe
            os.makedirs(current_path, exist_ok=True)
            file.save(os.path.join(current_path, filename))
            # --- FIN DE LA CORRECCIÓN ---
        except OSError as e:
            # Si ocurre un error del sistema operativo (como 'Permiso denegado'),
            # devolvemos un error claro en lugar de un 500 genérico.
            error_message = f"Error al guardar el archivo: {e}. Esto puede ser un problema de permisos en el volumen montado."
            return error_message, 500
        
    return redirect(url_for('index', path=path))

# --- INICIO DE LA CORRECCIÓN ---
# Añadimos una ruta explícita para manejar la creación de carpetas en la raíz
@app.route('/create-folder/', methods=['POST'])
@app.route('/create-folder/<path:path>', methods=['POST'])
def create_folder(path=''):
# --- FIN DE LA CORRECCIÓN ---
    """Crea una nueva carpeta."""
    current_path = get_absolute_path(path)
    folder_name = request.form.get('folder_name')

    if folder_name:
        try:
            safe_folder_name = secure_filename(folder_name)
            new_folder_path = os.path.join(current_path, safe_folder_name)
            os.makedirs(new_folder_path, exist_ok=True)
        except OSError as e:
            error_message = f"Error al crear la carpeta: {e}. Esto puede ser un problema de permisos en el volumen montado."
            return error_message, 500

    return redirect(url_for('index', path=path))

@app.route('/download/<path:path>')
def download_file(path):
    """Permite la descarga de un archivo."""
    directory = get_absolute_path(os.path.dirname(path))
    filename = os.path.basename(path)
    
    return send_from_directory(directory, filename, as_attachment=True)
