Claro, aquí te dejo el **README actualizado** con los cambios de la arquitectura híbrida (WebSockets + REST) y la nueva tabla de **conexiones de WebSocket** que se agregó para manejar la comunicación en tiempo real entre clientes y restaurantes:

---

# **README: Estructura de Base de Datos para Sistema de Pedidos (DynamoDB)**

Este documento describe la estructura de la base de datos diseñada para un sistema de pedidos en línea (similar a Pizza Hut) utilizando **DynamoDB** como base de datos NoSQL. La estructura está optimizada para consultas rápidas, escalabilidad y facilidad de mantenimiento, y soporta tanto operaciones REST tradicionales como actualizaciones en tiempo real usando WebSockets.

## **Tabla de Contenido**

1. [Usuarios (Users)](#tabla-users)
2. [Pedidos (Pedidos)](#tabla-pedidos)
3. [Productos (Productos)](#tabla-productos)
4. [Estados de Pedidos (Estado_Pedidos)](#tabla-estado_pedidos)
5. [Logs de Actividad (Logs)](#tabla-logs)
6. [Conexiones WebSocket (Conexiones)](#tabla-conexiones)

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

## **2. Tabla `Pedidos` (Pedidos)**

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

## **3. Tabla `Productos` (Productos)**

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

## **4. Tabla `Estado_Pedidos` (Estados de los Pedidos)**

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

## **5. Tabla `Logs` (Logs de Actividad)**

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

* **GSI** con `accion` como partition key si deseas consultar todos los logs de una acción específica.

---

## **6. Tabla `Conexiones` (Conexiones WebSocket)**

Esta nueva tabla almacena las conexiones activas de los clientes que están conectados mediante WebSockets. Permite notificar a los clientes sobre eventos importantes en tiempo real, como actualizaciones de pedidos.

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

---