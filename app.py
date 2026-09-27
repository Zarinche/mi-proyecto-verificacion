import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Simulación de base de datos en memoria (puedes conectarlo a SQLite o Google Sheets luego)
registros_usuarios = []

@app.route('/')
def index():
    # Captura los parámetros de la URL: /?user=Juan&for=Maria&goal=Promocion
    user = request.args.get('user', 'Anónimo')
    target = request.args.get('for', 'General')
    goal = request.args.get('goal', 'Interacción')
    
    # Registramos que el usuario entró
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
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{user}_{filename}")
        file.save(filepath)
        
        # Aquí puedes integrar la lógica para subir 'filepath' a tu Google Drive usando la API de Google.
        
        return jsonify({"mensaje": "¡Archivo subido y verificado con éxito!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)