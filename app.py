import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__, template_folder='.')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuración de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # El archivo JSON que descargas de Google Cloud
PARENT_FOLDER_ID = 'https://drive.google.com/drive/folders/186TLc4p3hLdRlMKTVXHrX1Wkrp7J151M?usp=drive_link'  # ID de la carpeta de destino en Drive

# Simulación de base de datos en memoria (puedes reemplazarlo por SQLite o Google Sheets más adelante)
registros_usuarios = []

def subir_a_drive(file_path, file_name):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'parents': [PARENT_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get('id')

@app.route('/')
def index():
    # Captura los parámetros de la URL: /?user=Juan&for=Maria&goal=Promocion
    user = request.args.get('user', 'Anónimo')
    target = request.args.get('for', 'General')
    goal = request.args.get('goal', 'Interacción')
    
    # Registramos que el usuario entró al enlace
    registro = {
        "usuario": user,
        "para": target,
        "motivo": goal,
        "estado": "Iniciado"
    }
    registros_usuarios.append(registro)
    print(f"[AGENTE REGISTRO]: {registro}")
    
    return render_template('index.html', user=user, target=target, goal=goal)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    user = request.form.get('user', 'Anónimo')
    if 'foto' not in request.files:
        return jsonify({"error": "No se encontró ningún archivo"}), 400
    
    file = request.files['foto']
    if file.filename == '':
        return jsonify({"error": "Archivo no seleccionado"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{user}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            # Subimos el archivo directamente a Google Drive
            subir_a_drive(filepath, unique_filename)
            # Limpiamos el archivo local del servidor para liberar espacio
            os.remove(filepath)
        except Exception as e:
            return jsonify({"error": f"Error al subir a Drive: {str(e)}"}), 500
        
        return jsonify({"mensaje": "¡Archivo subido a Google Drive con éxito!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
