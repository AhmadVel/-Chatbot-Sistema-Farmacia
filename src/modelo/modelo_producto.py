

class Producto:
    def __init__(self, id_producto, nombre, descripcion,precio_venta, stock, imagen_url=None):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_venta = precio_venta
        self.stock = stock
        self.imagen_url= imagen_url
        

    def __repr__(self):
        return f"Producto({self.id_producto}, {self.nombre}, {self.stock})"
