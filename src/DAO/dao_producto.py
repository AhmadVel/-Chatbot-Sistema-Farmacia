import mysql.connector
from ..modelo.modelo_producto import Producto

from dotenv import load_dotenv
import os

class ProductoDAO:
    def __init__(self):
         # Cargar variables del archivo .env
        load_dotenv()
        
        # Configura la conexión a MySQL usando las variables del .env
        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),        # Cargado desde .env
            port=int(os.getenv("DB_PORT")),  # Convertido a entero
            user=os.getenv("DB_USER"),       # Usuario
            password=os.getenv("DB_PASSWORD"),  # Contraseña
            database=os.getenv("DB_NAME")    # Base de datos
        )
        self.cursor = self.conn.cursor(dictionary=True)

    # Método para obtener todos los productos
    def obtener_todos(self):
        query = "SELECT id_producto, nombre, descripcion, precio_venta, stock, imagen_url FROM PRODUCTO LIMIT 1000"
        self.cursor.execute(query)
        productos = self.cursor.fetchall()
        return [Producto(fila['id_producto'], fila['nombre'], fila['descripcion'], fila['precio_venta'], fila['stock'], fila['imagen_url']) for fila in productos]

    # Método para obtener un producto por su ID
    def obtener_por_id(self, id_producto):
        query = "SELECT * FROM PRODUCTO WHERE id_producto = %s LIMIT 1"
        self.cursor.execute(query, (id_producto,))
        fila = self.cursor.fetchone()
        if fila:
            return Producto(
                id_producto=fila['id_producto'], 
                nombre=fila['nombre'], 
                descripcion=fila['descripcion'], 
                precio_venta=fila['precio_venta'], 
                stock=fila['stock'], 
                imagen_url=fila['imagen_url']
            )
        return None

    # Método para agregar un nuevo producto
    def agregar(self, producto):
        query = "INSERT INTO PRODUCTO (nombre, descripcion, precio_venta, stock, imagen_url) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(query, (producto.nombre, producto.descripcion, producto.precio_venta, producto.stock, producto.imagen_url))
        self.conn.commit()

    # Método para actualizar un producto existente
    def actualizar(self, id_producto, producto_actualizado):
        query = """
        UPDATE PRODUCTO
        SET nombre = %s, descripcion = %s, precio_venta = %s, stock = %s
        WHERE id_producto = %s
        """
        self.cursor.execute(query, (producto_actualizado.nombre, producto_actualizado.descripcion, producto_actualizado.precio_venta, producto_actualizado.stock, id_producto))
        self.conn.commit()

    # Método para obtener productos con bajo stock
    def obtener_por_bajo_stock(self, stock_threshold=0):
        query = "SELECT nombre, stock FROM PRODUCTO WHERE stock <= %s"
        self.cursor.execute(query, (stock_threshold,))
        productos = self.cursor.fetchall()
        return [{'name': fila['nombre'], 'stock': fila['stock']} for fila in productos]

    # Método para eliminar un producto por su ID
    def eliminar(self, id_producto):
        query = "DELETE FROM PRODUCTO WHERE id_producto = %s"
        self.cursor.execute(query, (id_producto,))
        self.conn.commit()

    # Destructor para cerrar la conexión al final
    def __del__(self):
        self.cursor.close()
        self.conn.close()
