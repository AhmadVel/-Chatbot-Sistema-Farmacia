
        function toggleMenu() {
            const menuContent = document.getElementById("menuContent");
            const menuOverlay = document.getElementById("menuOverlay");
            menuContent.classList.toggle("show");
            menuOverlay.style.display = "block";
            document.body.classList.add("overflow-hidden");
            menuContent.addEventListener("transitionend", () => {
                const firstButton = menuContent.querySelector("button");
                if (firstButton) firstButton.focus();  // Poner el foco en el primer botón
            });
            // Añadir el evento para restringir la tabulación
            restrictTabbing(menuContent);
        }

        function closeMenu() {
            const menuContent = document.getElementById("menuContent");
            const menuOverlay = document.getElementById("menuOverlay");
            menuContent.classList.remove("show");
            menuOverlay.style.display = "none";
            document.body.classList.remove("overflow-hidden");
            removeTabbingRestriction(menuContent);
        }

        // Variable global para almacenar los productos con bajo stock
        let lowStockProducts = [];
        // Función que se ejecuta al cargar la página para obtener los productos de bajo stock
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/low_stock_products')
                .then(response => response.json())
                .then(data => {
                    lowStockProducts = data.products; // Almacena los productos con bajo stock
                    updateNotificationIcon(lowStockProducts); // Actualiza el icono al cargar la página
                })
                .catch(error => console.error('Error al verificar el stock bajo:', error));
        });

        function updateNotificationIcon(products) {
            const notificationIcon = document.getElementById('notificationIcon');
            const notificationButton = document.getElementById("notificationButton");
            const lowStockImageUrl = notificationButton.getAttribute('data-low-stock-image');
            const noNotificationImageUrl = notificationButton.getAttribute('data-no-notification-image');
        
            // Cambiar el ícono según si hay stock bajo o no
            notificationIcon.src = products.length > 0 ? lowStockImageUrl : noNotificationImageUrl;
        
            // Si hay productos con stock bajo, activar la animación
            if (products.length > 0) {
                notificationIcon.classList.add('vibrating');
            } else {
                notificationIcon.classList.remove('vibrating');
            }
        }

        function toggleNotifications() {
            const notificationMenu = document.getElementById("notificationMenu");
            const notificationOverlay = document.getElementById("notificationOverlay");

            notificationMenu.classList.toggle("show");
            notificationOverlay.style.display = "block";
            document.body.classList.add("overflow-hidden");
            displayLowStockProducts();
            const firstFocusableElement = document.querySelector("#notificationList .product-item, #notificationList p[tabindex='0']");
            if (firstFocusableElement) firstFocusableElement.focus();
            restrictTabbing(notificationMenu); 
        }

        function displayLowStockProducts() {
            const notificationList = document.getElementById('notificationList');
            notificationList.innerHTML = '';
            if (lowStockProducts.length > 0) {
                lowStockProducts.forEach(product => {
                    const productItem = document.createElement('div');
                    productItem.classList.add('product-item');
                    productItem.tabIndex = 0;
                    productItem.innerHTML = `
                        <strong>${product.name}</strong>
                        <span class="product-stock">Stock: ${product.stock}</span>
                    `;
                    notificationList.appendChild(productItem);
                });
            } else {
                const noStockMessage = document.createElement('p');
                noStockMessage.tabIndex = 0; // Hacer el mensaje tabulable
                noStockMessage.textContent = 'No hay productos con bajo stock';
                notificationList.appendChild(noStockMessage);
            }
        }

        function closeNotifications() {
            const notificationMenu = document.getElementById("notificationMenu");
            const notificationOverlay = document.getElementById("notificationOverlay");
            notificationMenu.classList.remove("show");
            notificationOverlay.style.display = "none";
            document.body.classList.remove("overflow-hidden");
            removeTabbingRestriction(notificationMenu);
        }

        function openEditModal(productId) {
            const modal = document.getElementById("editProductModal");
            modal.style.display = "block";
            document.body.classList.add("overflow-hidden");
            
            // Restablece todos los campos del formulario a sus valores por defecto
            const form = modal.querySelector('form');
            if (form) {
                form.reset(); 
            }

            // Asignar el foco al primer campo del formulario
            const firstInput = modal.querySelector("input:not([type='hidden']), textarea, button, select");
            if (firstInput) firstInput.focus();
            // Añadir el evento para restringir la tabulación
            restrictTabbing(modal);
            
            // Mostrar "Cargando..." en los campos antes de que se carguen los datos
            document.getElementById("productName").value = "Cargando...";
            document.getElementById("productDescription").value = "Cargando...";
            document.getElementById("productPrice").value = 0;  
            document.getElementById("productStock").value = 0;
            
            // Cargar los datos del producto usando fetch
            fetch(`/producto/${productId}`)
                .then(response => response.json())
                .then(productData => {
                    // Llenar los campos con los datos del producto
                    document.getElementById("productName").value = productData.nombre;
                    document.getElementById("productPrice").value = productData.precio_venta;
                    document.getElementById("productDescription").value = productData.descripcion;
                    document.getElementById("productStock").value = productData.stock;
                    document.getElementById("productId").value = productId; // Establecer el ID del producto en el campo oculto
                })
                .catch(error => console.error('Error al cargar los datos del producto:', error));
        }
        
        // Capturar el evento de envío del formulario
        document.getElementById("editProductForm").addEventListener("submit", function(event) {
            event.preventDefault(); // Evitar el envío normal del formulario

            // Obtener los datos del formulario
            const productId = document.getElementById("productId").value; // Asegúrate de tener un campo oculto con el ID del producto
            const nombre = document.getElementById("productName").value;
            const precioVenta = parseFloat(document.getElementById("productPrice").value);
            const descripcion = document.getElementById("productDescription").value;
            const stock = parseInt(document.getElementById("productStock").value);

            // Crear el objeto de datos para enviar
            const datosProducto = {
                nombre: nombre,
                precio_venta: precioVenta,
                descripcion: descripcion,
                stock: stock,
                // No es necesario incluir imagen_url aquí si no se está modificando
            };

            // Configurar la solicitud PUT utilizando Fetch API
            fetch(`/producto/${productId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datosProducto),
            })
            .then(response => {
                if (response.ok) {
                    // Si la respuesta es exitosa, recargar la pagina
                    window.location.reload();
                } else {
                    // Si hay un error, mostrar un mensaje
                    alert("Error al actualizar el producto. Por favor, inténtelo nuevamente.");
                }
            })
            .catch(error => {
                // Manejar cualquier error de la solicitud
                console.error('Error:', error);
                alert("Hubo un error al realizar la solicitud.");
            });
        });
        function closeEditModal() {
            const modal = document.getElementById("editProductModal");
            modal.style.display = "none";
            document.body.classList.remove("overflow-hidden");
            removeTabbingRestriction(modal);
        }

        function openAddModal() {
            const modal = document.getElementById("addProductModal");
            modal.style.display = "block";
            document.body.classList.add("overflow-hidden");
            const form = modal.querySelector('form');
            if (form) {
                form.reset(); // Restablece todos los campos del formulario a sus valores por defecto
            }
            // Asignar el foco al primer campo del formulario
            const firstInput = modal.querySelector("input, textarea, select");
            if (firstInput) firstInput.focus();
            // Añadir el evento para restringir la tabulación
            restrictTabbing(modal);
        }

        function closeAddModal() {
            const modal = document.getElementById("addProductModal");
            modal.style.display = "none";
            document.body.classList.remove("overflow-hidden");
            removeTabbingRestriction(modal);
        }

        function restrictTabbing(modal) {
            modal.addEventListener("keydown", function(event) {
                const focusableElements = modal.querySelectorAll("input:not([type='hidden']), textarea, button, select, a[href], #notificationList .product-item, #notificationList p[tabindex='0']");
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];
        
                // Si presionamos Tab, restringimos la navegación dentro del modal
                if (event.key === "Tab") {
                    if (event.shiftKey) { // Shift + Tab
                        if (document.activeElement === firstElement) {
                            lastElement.focus();
                            event.preventDefault(); // Prevenir que el foco salga del modal
                        }
                    } else { // Tab
                        if (document.activeElement === lastElement) {
                            firstElement.focus();
                            event.preventDefault(); // Prevenir que el foco salga del modal
                        }
                    }
                }
            });
        }

        function removeTabbingRestriction(modal) {
            modal.removeEventListener("keydown", restrictTabbing);
        }

        window.onclick = function(event) {
            const addModal = document.getElementById("addProductModal");
            const editModal = document.getElementById("editProductModal");
            const menuOverlay = document.getElementById("menuOverlay");
            const notificationOverlay = document.getElementById("notificationOverlay");
            switch (event.target) {
                case addModal:
                    closeAddModal();
                    break;
                case editModal:
                    closeEditModal();
                    break;
                case menuOverlay:
                    closeMenu();
                    break;
                case notificationOverlay:
                    closeNotifications();
                    break;
                default:
                    break;
            }
        }

        // Función para renderizar productos
        function renderProducts(products) {
            return products.map(product => `
                <div class="product-card">
                    <img src="${product.image}" alt="${product.name}" class="img-fluid mb-3">
                    <h3 class="h5 mb-2">${product.name}</h3>
                    <p style="height: 42px;" class="text-muted small mb-2">${product.description}</p>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <span class="font-weight-bold">$${Number(product.price).toFixed(2)}</span>
                        <span class="badge-stock ${product.stock > 5 ? 'badge-stock-high' : 'badge-stock-low'}">
                            Stock: ${product.stock}
                        </span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <!-- Botón de editar -->
                        <button class="btn btn-outline-primary" onclick="openEditModal(${product.id})">Editar Producto</button>
                        
                        <!-- Botón de eliminar -->
                        <button class="btn btn-danger ms-2" onclick="openDeleteModal(${product.id})">
                            <i class="bi bi-trash"></i> Eliminar
                        </button>
                    </div>
                </div>
            `).join('');
        }
        

        // Función para manejar la búsqueda de productos
        function handleSearch(inputElement, allProducts, productsGrid) {
            inputElement.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase().trim();
                const filteredProducts = allProducts.filter(product =>
                    product.name.toLowerCase().includes(searchTerm) ||
                    product.description.toLowerCase().includes(searchTerm)
                );
                productsGrid.innerHTML = renderProducts(filteredProducts);
                if (filteredProducts.length === 0) {
                    productsGrid.innerHTML = `
                        <div class="col-12 text-center">
                            <p class="text-muted">No se encontraron productos que coincidan con la búsqueda</p>
                        </div>
                    `;
                }
            });
        }

        // Función principal para mostrar los productos
        function showProducts() {
            let allProducts = [];
            fetch('/productos')
                .then(response => response.json())
                .then(products => {
                    allProducts = products;
                    const contentDiv = document.getElementById("content");
                    // Configurar la estructura de la página
                    contentDiv.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <div class="search-bar">
                                <input type="text" id="searchInput" placeholder="Buscar productos..." class="form-control">
                            </div>
                            <button class="btn btn-primary" onclick="openAddModal()">Agregar Producto</button>
                        </div>
                        <div class="products-grid">${renderProducts(products)}</div>
                    `;
                    // Configurar el evento de búsqueda
                    const searchInput = document.getElementById('searchInput');
                    const productsGrid = document.querySelector('.products-grid');
                    handleSearch(searchInput, allProducts, productsGrid);
                    closeMenu();
                })
                .catch(error => console.error('Error:', error));
        }
        // Inicializar la vista de productos
        showProducts();
        
        let productIdToDelete = null; // Variable para almacenar el ID del producto a eliminar

        // Función para abrir el modal de confirmación
        function openDeleteModal(productId) {
            productIdToDelete = productId; // Guardamos el ID del producto a eliminar
            const modal = document.getElementById("deleteProductModal");
            modal.style.display = "block";
            document.body.classList.add("overflow-hidden");
        }

        // Función para cerrar el modal de confirmación
        function closeDeleteModal() {
            const modal = document.getElementById("deleteProductModal");
            modal.style.display = "none";
            document.body.classList.remove("overflow-hidden");
        }

        // Función para eliminar el producto
        function deleteProduct() {
            if (productIdToDelete !== null) {
                // Hacer la solicitud DELETE al servidor
                fetch(`/producto/${productIdToDelete}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Producto eliminado correctamente');
                        // Recargar la página después de eliminar
                        location.reload(); // Recarga la página
                    } else {
                        alert('Hubo un error al eliminar el producto');
                    }
                })
                .catch(error => {
                    console.error('Error al eliminar el producto:', error);
                    alert('Error al eliminar el producto');
                })
                .finally(() => {
                    closeDeleteModal(); // Cerrar el modal después de la eliminación
                });
            }
        }