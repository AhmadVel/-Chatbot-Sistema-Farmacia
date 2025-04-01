import os
from flask import Flask, render_template, request, jsonify, Blueprint, redirect, url_for, session
import google.generativeai as genai
from google.cloud import bigquery
from src.DAO.dao_producto import ProductoDAO
from src.controlador.controlador_producto import product_bp
from src.controlador.controlador_login import login_bp
import io
from PIL import Image
import pytesseract
import PyPDF2
from PyPDF2 import PdfReader

app = Flask(__name__)

app.secret_key = os.urandom(24)

app.register_blueprint(product_bp)
app.register_blueprint(login_bp)

# Configura las credenciales de BigQuery
client = bigquery.Client.from_service_account_json('driven-edition-436702-q0-aa07faa8bce3.json')

# Configura tu API key aquí
genai.configure(api_key='INSERTE_SU_API_KEY')

# Crea el modelo de AI 
generation_config = {
    "temperature": 0.1,
    "top_p": 1,
    "max_output_tokens": 1000,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('login_bp.home'))
    return render_template('frm_login.html')

@app.route('/Chatbot')
def chatbot():
    return render_template('frm_chatbot.html')


@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form.get('input')
    file = request.files.get('file')  # Obtener archivo subido, si existe

    file_data = None
    if file:
        file_name = file.filename
        if file_name.endswith('.pdf'):
            # Procesar PDF
            pdf_reader = PdfReader(file)
            file_data = " ".join(page.extract_text() for page in pdf_reader.pages)
            file_data = f"El archivo subido es: {file_name}. Contenido del archivo: {file_data}"
        elif file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Procesar imagen
            image = Image.open(file)
            file_data = pytesseract.image_to_string(image)
            file_data = f"El archivo subido es: {file_name}. Contenido extraído: {file_data}"

    query = """
        SELECT nombre, descripcion, precio_venta, stock, imagen_url 
        FROM `driven-edition-436702-q0.GCP.PRODUCTO` 
        LIMIT 1000
    """
    # Ejecutar la consulta
    query_job = client.query(query)

    # Esperar y obtener los resultados
    producto_dao = ProductoDAO()
    results = producto_dao.obtener_todos()
    
    # Crear una lista para almacenar los resultados formateados
    resultados_formateados = []

    for producto in results:
        # Obtener los valores necesarios
        nombre = producto.nombre
        descripcion = producto.descripcion
        precio_venta = producto.precio_venta
        stock = producto.stock
        imagen_url = producto.imagen_url
        
        # Formatear la respuesta con una imagen HTML
        resultado = f"""
            "Tienes {nombre}, con descripción {descripcion}, precio {precio_venta} y stock {stock}.
            <br><img src="{imagen_url}" alt="{nombre}" style="max-width: 100px; height: auto;" />
        """
        if imagen_url:
            resultado += f"<br><img src='{imagen_url}' alt='{nombre}' style='max-width: 100px; height: auto;' />"
        resultados_formateados.append(resultado)

    context = f"Datos del archivo: {file_data}" if file_data else ""
    # Combinamos los resultados formateados en un solo mensaje
    mensaje_adicional = "<br>".join(resultados_formateados)

    print(mensaje_adicional)
    # Si no hay historial en la sesión, inicialízalo
    if 'chat_history' not in session:
        # Aquí puedes precargar el mensaje inicial
        session['chat_history'] = [
            {
                "role": "user",
                "parts": [
                    f"Eres el dueño de una farmacia. Solo responde preguntas sobre medicamentos, síntomas y productos que tienes. Cuando menciones un producto da su nombre, descripción, precio y stock que tienes. Y cuando recomiendes un producto tambien brinda la dosis recomendada y horario. Además puedes leer los archivos que los usuarios suban. {mensaje_adicional}",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Bienvenido a nuestra farmacia. ¿En qué puedo ayudarle?",
                ],
            },
        ]

    # Obtén el historial del chat de la sesión
    chat_history = session['chat_history']

    try:
        # Crea una nueva sesión de chat con el historial existente
        chat_session = model.start_chat(history=chat_history)

        response = chat_session.send_message(user_input + context)

        # Añade el mensaje del usuario y la respuesta al historial
        chat_history.append({"role": "user", "parts": [user_input]})
        chat_history.append({"role": "model", "parts": [response.parts[0]] if isinstance(response.parts, list) else [response.text]})

        # Guarda el historial actualizado en la sesión
        session['chat_history'] = chat_history

        # Extrae la respuesta del modelo
        response_text = response.parts[0] if isinstance(response.parts, list) else response.text
    except Exception as e:
        print(f"Error processing request: {e}")
        response_text = "LO SIENTO NO ENTIENDO LO QUE QUIERES DECIR."

    return jsonify({'response': response_text})

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se subió ningún archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    # Procesar el PDF
    if file and file.filename.endswith('.pdf'):
        reader = PdfReader(file)
        text = ''.join(page.extract_text() for page in reader.pages)
        session['pdf_content'] = text
        return jsonify({'message': 'Archivo PDF procesado correctamente'})

    # Procesar la Imagen
    elif file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        session['image_content'] = text
        return jsonify({'message': 'Imagen procesada correctamente'})

    return jsonify({'error': 'Formato no válido'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
