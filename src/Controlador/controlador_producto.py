from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from src.DAO.dao_producto import ProductoDAO
from werkzeug.utils import secure_filename #Nueva librería
from src.modelo.modelo_producto import Producto  # Asegúrate de que esta importación sea correcta
import os 
from PIL import Image
from src.modelo.modelo_producto import Producto  # Asegúrate de que esta importación sea correcta
import mimetypes


# Define el Blueprint
product_bp = Blueprint('product_bp', __name__)
UPLOAD_FOLDER = 'images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}

def allowed_file(filename):
    # Verificar la extensión del archivo y el tipo MIME
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type in ALLOWED_MIME_TYPES:
            return True
    return False

@product_bp.route('/Home')
def home():
    # Obtener todos los productos
    producto = ProductoDAO().obtener_todos()
    return render_template('frm_menu.html', Producto=producto)

@product_bp.route('/productos')
def get_products():
    # Obtener todos los productos desde la base de datos MySQL
    producto_dao = ProductoDAO()
    productos = producto_dao.obtener_todos()

    # Convierte los productos en un formato JSON
    product_list = [
        {
            "id": producto.id_producto,
            "name": producto.nombre,
            "price": producto.precio_venta,
            "description": producto.descripcion,
            "stock": producto.stock,
            "image": producto.imagen_url,
        }
        for producto in productos
    ]

    # Ordenar la lista alfabéticamente por el nombre del producto
    product_list = sorted(product_list, key=lambda x: x['name'].lower())

    return jsonify(product_list)

@product_bp.route('/producto/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # Obtener el producto desde la base de datos
    producto_dao = ProductoDAO()
    producto = producto_dao.obtener_por_id(product_id)
    if producto:
        # Retornar los datos del producto como JSON
        return jsonify({
            'id': producto.id_producto,
            'nombre': producto.nombre,
            'precio_venta': producto.precio_venta,
            'descripcion': producto.descripcion,
            'stock': producto.stock,
            'imagen_url': producto.imagen_url
        })
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

# Ruta para agregar un nuevo producto
@product_bp.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    # Verificar que los datos lleguen correctamente
    print("Datos recibidos para agregar producto:", request.form)

    # Obtener los datos del formulario
    nombre = request.form.get('nombre')
    precio_venta = float(request.form.get('precio_venta'))
    descripcion = request.form.get('descripcion')
    stock = int(request.form.get('stock'))

    imagen_url = request.files.get('imagen')  # Deberías usar `request.files.get('imagen')` en lugar de `request.form.get('imagen')`

    if imagen_url and allowed_file(imagen_url.filename):
        # Asegurarse de que el nombre del archivo sea seguro
        filename = secure_filename(imagen_url.filename)
        # Ruta completa donde se guardará la imagen
        image_folder = os.path.join('static', 'images')
        
        # Crear la carpeta si no existe
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        # Guardar la imagen en la carpeta correcta
        image_path = os.path.join(image_folder, filename)
        imagen_url.save(image_path)
        
        # Obtener la URL de la imagen relativa
        imagen_url = url_for('static', filename=f'images/{filename}')
    else:
        return jsonify({"error": "Archivo no válido o no permitido"}), 400
    
    # Crear el objeto Producto
    nuevo_producto = Producto(None, nombre, descripcion, precio_venta, stock, imagen_url)
    
    # Insertar el producto en la base de datos
    producto_dao = ProductoDAO()
    producto_dao.agregar(nuevo_producto)

    # Redirigir al usuario a la página principal después de agregar el producto
    return redirect(url_for('product_bp.home'))

@product_bp.route('/producto/<int:product_id>', methods=['PUT'])
def actualizar_producto(product_id):
    # Verificar que los datos lleguen correctamente
    print("Datos recibidos para actualizar producto:", request.json)

    # Obtener los datos enviados en el cuerpo de la solicitud JSON
    datos = request.json
    nombre = datos.get('nombre')
    precio_venta = float(datos.get('precio_venta'))
    descripcion = datos.get('descripcion')
    stock = int(datos.get('stock'))
    imagen_url = datos.get('imagen_url', 'URL_DE_IMAGEN_POR_DEFECTO')
    
    # Crear el objeto Producto con los datos actualizados
    producto_actualizado = Producto(product_id, nombre, descripcion, precio_venta, stock, imagen_url)
    
    # Actualizar el producto en la base de datos
    producto_dao = ProductoDAO()
    producto_dao.actualizar(product_id, producto_actualizado)
    
    # Responder con un JSON de éxito
    return jsonify({"success": True, "message": "Producto actualizado correctamente"})

@product_bp.route('/low_stock_products')
def low_stock_products():
    # Obtener productos con bajo stock desde la base de datos
    producto_dao = ProductoDAO()
    products = producto_dao.obtener_por_bajo_stock(stock_threshold=5)
    
    return jsonify({"products": products})

@product_bp.route('/producto/<int:product_id>', methods=['DELETE'])
def eliminar_producto(product_id):
    try:
        # Eliminar el producto de la base de datos
        producto_dao = ProductoDAO()
        producto_dao.eliminar(product_id)
        
        # Responder con un JSON de éxito
        return jsonify({"success": True, "message": "Producto eliminado correctamente"})
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        return jsonify({"success": False, "message": "Hubo un error al eliminar el producto"}), 500

