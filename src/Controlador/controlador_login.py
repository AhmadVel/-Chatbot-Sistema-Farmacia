from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
login_bp = Blueprint('login_bp', __name__)

# Configuración de conexión a MySQL
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),        # IP pública de Cloud SQL desde .env
            port=int(os.getenv("DB_PORT")),  # Puerto desde .env
            user=os.getenv("DB_USER"),       # Usuario desde .env
            password=os.getenv("DB_PASSWORD"),  # Contraseña desde .env
            database=os.getenv("DB_NAME"),   # Base de datos desde .env
        )
        print("Conexión exitosa a la base de datos")  # Verificación de conexión
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        # Conectar a la base de datos
        conn = get_db_connection()
        if conn is None:
            return jsonify(success=False, message="Error de conexión a la base de datos")

        cursor = conn.cursor(dictionary=True)
        
        # Consulta para obtener el usuario por email
        query = "SELECT * FROM USUARIO WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        # Imprimir el resultado de la consulta para depuración
        print("Usuario encontrado en la base de datos:", user)

        cursor.close()
        conn.close()

        if user:
            # Comparar directamente la contraseña en texto plano, ya que no está encriptada
            if user['password'] == password:
                # Guardar el usuario en la sesión
                session['username'] = user['email']
                print("Inicio de sesión exitoso")  # Mensaje de éxito
                return jsonify(success=True)
            else:
                print("Contraseña incorrecta")  # Mensaje de error de contraseña
                return jsonify(success=False, message="Usuario o contraseña incorrectos")
        else:
            print("Usuario no encontrado")  # Mensaje de error de usuario no encontrado
            return jsonify(success=False, message="Usuario o contraseña incorrectos")

    except Exception as e:
        print(f"Error en la autenticación: {e}")
        return jsonify(success=False, message=f"Error al acceder a la base de datos: {e}")

@login_bp.route('/home')
def home():
    if 'username' in session:
        return render_template('frm_menu.html')
    else:
        return redirect(url_for('login_bp.login'))

@login_bp.route('/logout')
def logout():
    session.pop('username', None)  # Elimina el nombre de usuario de la sesión
    flash("Has cerrado sesión.", "info")
    return render_template('frm_login.html')  # Redirige a la vista del login
