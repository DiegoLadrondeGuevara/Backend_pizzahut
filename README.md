# **README: Estructura de Base de Datos para Sistema de Pedidos (DynamoDB)**

Este documento describe la estructura de la base de datos diseñada para un sistema de pedidos en línea (similar a Pizza Hut) utilizando **DynamoDB** como base de datos NoSQL. La estructura está optimizada para consultas rápidas, escalabilidad y facilidad de mantenimiento, y soporta tanto operaciones REST tradicionales como actualizaciones en tiempo real usando WebSockets.

## **Tabla de Contenido**

1. [Usuarios (Users)](#tabla-users)
2. [Restaurantes (Restaurantes)](#tabla-restaurantes)
3. [Pedidos (Pedidos)](#tabla-pedidos)
4. [Productos (Productos)](#tabla-productos)
5. [Estados de Pedidos (Estado_Pedidos)](#tabla-estado_pedidos)
6. [Logs de Actividad (Logs)](#tabla-logs)
7. [Conexiones WebSocket (Conexiones)](#tabla-conexiones)

---

## **1. Tabla `Users` (Usuarios)**

La tabla de **Usuarios** almacena información básica sobre los usuarios, incluyendo su rol (admin, cliente, etc.), email y contraseña encriptada.

### **Definición de la tabla `Users`**:

| Atributo         | Tipo      | Descripción                                       |
| ---------------- | --------- | ------------------------------------------------- |
| `user_id`        | UUID (PK) | Identificador único del usuario (clave primaria). |
| `nombre_usuario` | string    | Nombre de usuario (opcional, puede no ser único). |
| `email`          | string    | Correo electrónico del usuario (puede ser único). |
| `contraseña`     | string    | Contraseña encriptada del usuario.                |
| `user_rol`       | string    | Rol del usuario ("restaurante", "cliente", etc.). |

### **Definición de clave primaria**:

* **Partition Key:** `user_id` (UUID)
* **Sort Key:** No se necesita.

### **Índices Secundarios (opcional)**:

---

## **2. Tabla `Restaurantes` (Restaurantes)**

La tabla de **Restaurantes** almacena información específica sobre cada restaurante, incluyendo su nombre, email, ubicación, teléfono y detalles de autenticación.

### **Definición de la tabla `Restaurantes`**:

| Atributo             | Tipo      | Descripción                                                  |
| -------------------- | --------- | ------------------------------------------------------------ |
| `restaurant_id`      | UUID (PK) | Identificador único del restaurante (clave primaria).        |
| `email`              | string    | Correo electrónico del restaurante (único).                  |
| `nombre_restaurante` | string    | Nombre del restaurante.                                      |
| `direccion`          | string    | Dirección del restaurante.                                   |
| `distrito`           | string    | Distrito donde se ubica el restaurante.                      |
| `departamento`       | string    | Departamento donde se encuentra el restaurante.              |
| `telefono`           | string    | Número de teléfono del restaurante.                          |
| `password`           | string    | Contraseña encriptada para la autenticación del restaurante. |
| `token`              | string    | Token de autenticación generado para el restaurante.         |
| `created_at`         | datetime  | Fecha y hora en que se registró el restaurante.              |

### **Definición de clave primaria**:

* **Partition Key:** `restaurant_id` (UUID)
* **Sort Key:** No se necesita.

### **Índices Secundarios (opcional)**:

* **GSI** con `email` como partition key para obtener fácilmente un restaurante por su correo electrónico.

---

## **3. Tabla `Pedidos` (Pedidos)**

La tabla de **Pedidos** almacena la información relacionada con los pedidos realizados por los usuarios. Cada pedido está asociado a un restaurante (`tenant_id`).

### **Definición de la tabla `Pedidos`**:

| Atributo       | Tipo        | Descripción                                                                          |
| -------------- | ----------- | ------------------------------------------------------------------------------------ |
| `tenant_id`    | string (PK) | Identificador único del restaurante (clúster de restaurantes).                       |
| `pedido_id`    | UUID (SK)   | Identificador único del pedido.                                                      |
| `user_id`      | UUID        | ID del usuario que realizó el pedido.                                                |
| `productos`    | list        | Lista de productos: `[{"producto_id": UUID, "cantidad": int, "precio": float}, ...]` |
| `total`        | float       | Total calculado del pedido.                                                          |
| `estado`       | string      | Estado del pedido (PENDIENTE, EN_PREPARACION, etc.).                                 |
| `fecha_pedido` | datetime    | Fecha y hora en que se realizó el pedido.                                            |

### **Definición de clave primaria**:

* **Partition Key:** `tenant_id` (UUID o string) — Representa el restaurante.
* **Sort Key:** `pedido_id` (UUID) — Identificador único del pedido.

### **Índices Secundarios (opcional)**:

* **GSI** con `estado` o `user_id` como partition key si se necesitan consultas rápidas por estado del pedido o por usuario.

---

## **4. Tabla `Productos` (Productos)**

La tabla de **Productos** contiene la información de los productos disponibles en el restaurante, como pizzas, bebidas, combinados, etc.

### **Definición de la tabla `Productos`**:

| Atributo          | Tipo      | Descripción                                                       |
| ----------------- | --------- | ----------------------------------------------------------------- |
| `producto_id`     | UUID (PK) | Identificador único del producto.                                 |
| `tenant_id`       | string    | Identificador único del restaurante al que pertenece el producto. |
| `nombre_producto` | string    | Nombre del producto (Ej. "Pizza Margarita", "Bebida Cola").       |
| `tipo_producto`   | string    | Tipo de producto (`solo`, `combo`, `promocion`).                  |
| `descripcion`     | string    | Descripción del producto.                                         |
| `precio`          | float     | Precio del producto.                                              |
| `imagen_url`      | string    | URL de la imagen del producto (opcional).                         |

### **Definición de clave primaria**:

* **Partition Key:** `producto_id` (UUID)

### **Índices Secundarios (opcional)**:

* **GSI** con `tenant_id` como partition key si se requiere obtener todos los productos de un restaurante.

---

## **5. Tabla `Estado_Pedidos` (Estados de los Pedidos)**

La tabla de **Estados de Pedidos** almacena los cambios de estado de cada pedido, como cuando el pedido está en preparación, listo para entregar, etc.

### **Definición de la tabla `Estado_Pedidos`**:

| Atributo    | Tipo      | Descripción                                             |
| ----------- | --------- | ------------------------------------------------------- |
| `pedido_id` | UUID (PK) | Identificador único del pedido.                         |
| `timestamp` | datetime  | Fecha y hora en que se registró el cambio de estado.    |
| `estado`    | string    | Estado del pedido (Ej. "PENDIENTE", "EN_PREPARACION").  |
| `notas`     | string    | Notas adicionales sobre el cambio de estado (opcional). |

### **Definición de clave primaria**:

* **Partition Key:** `pedido_id` (UUID)
* **Sort Key:** `timestamp` (datetime) — Se usa para ordenar los estados por fecha de cambio.

### **Índices Secundarios (opcional)**:

* **GSI** con `estado` como partition key si deseas consultar todos los pedidos en un estado específico.

---

## **6. Tabla `Logs` (Logs de Actividad)**

La tabla de **Logs** almacena las acciones realizadas por los usuarios en el sistema, como iniciar sesión, crear un pedido, etc.

### **Definición de la tabla `Logs`**:

| Atributo      | Tipo      | Descripción                                               |
| ------------- | --------- | --------------------------------------------------------- |
| `log_id`      | UUID (PK) | Identificador único del log.                              |
| `user_id`     | UUID      | ID del usuario que realizó la acción.                     |
| `accion`      | string    | Acción realizada (login, logout, crear_pedido, etc.).     |
| `horario`     | datetime  | Fecha y hora en la que ocurrió la acción.                 |
| `resultado`   | string    | Resultado de la acción (éxito, fallo).                    |
| `dispositivo` | string    | Dispositivo desde el que se realizó la acción (opcional). |
| `ip`          | string    | IP del usuario (opcional).                                |

### **Definición de clave primaria**:

* **Partition Key:** `user_id` (UUID) — Agrupar por usuario.
* **Sort Key:** `horario` (datetime) — Para ordenar por fecha.

### **Índices Secundarios (opcional)**:

* **GSI** con `accion` como partition key si deseas consultar todos los logs de


una acción específica.

---

## **7. Tabla `Conexiones` (Conexiones WebSocket)**

Esta tabla almacena las conexiones activas de los clientes que están conectados mediante WebSockets. Permite notificar a los clientes sobre eventos importantes en tiempo real, como actualizaciones de pedidos.

### **Definición de la tabla `Conexiones`**:

| Atributo        | Tipo     | Descripción                                                    |
| --------------- | -------- | -------------------------------------------------------------- |
| `connection_id` | string   | Identificador único de la conexión WebSocket (clave primaria). |
| `user_id`       | UUID     | ID del usuario asociado con la conexión.                       |
| `timestamp`     | datetime | Fecha y hora en que se realizó la conexión.                    |

### **Definición de clave primaria**:

* **Partition Key:** `connection_id` (string)
* **Sort Key:** No se necesita.

### **Índices Secundarios (opcional)**:

* **GSI** con `user_id` como partition key para obtener todas las conexiones de un usuario específico.


ndpoints:
  POST - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/logs
  POST - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/pedidos
  GET - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/pedidos/{pedido_id}/estado
  GET - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/pedidos/activos
  POST - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/login
  POST - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/register
  POST - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/restaurantes/register
  POST - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/restaurantes/login
  PUT - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/pedidos/{pedido_id}/estado
  PUT - https://8wqnmk44tl.execute-api.us-east-1.amazonaws.com/dev/pedidos/{pedido_id}/estado
functions:
  createLog: api-gestion-pedidos-dev-createLog (1.9 MB)
  createPedido: api-gestion-pedidos-dev-createPedido (1.9 MB)
  getEstadoPedido: api-gestion-pedidos-dev-getEstadoPedido (1.9 MB)
  listPedidosActivos: api-gestion-pedidos-dev-listPedidosActivos (1.9 MB)
  login: api-gestion-pedidos-dev-login (1.9 MB)
  register: api-gestion-pedidos-dev-register (1.9 MB)
  registerRestaurant: api-gestion-pedidos-dev-registerRestaurant (1.9 MB)
  loginRestaurant: api-gestion-pedidos-dev-loginRestaurant (1.9 MB)
  notifyPedidoEstado: api-gestion-pedidos-dev-notifyPedidoEstado (1.9 MB)
  updateEstadoPedido: api-gestion-pedidos-dev-updateEstadoPedido (1.9 MB)
