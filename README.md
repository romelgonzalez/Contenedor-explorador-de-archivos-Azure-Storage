# Explorador de Archivos Web para Azure Storage

Este proyecto es una sencilla aplicación web desarrollada en **Python con Flask** que proporciona una interfaz gráfica para explorar y gestionar archivos en un volumen de almacenamiento de Azure montado en un contenedor de App Service.

La aplicación permite navegar por directorios, subir y descargar archivos, y crear nuevas carpetas, todo a través de una **interfaz web intuitiva**.

![image](https://github.com/romelgonzalez/azure-app-container/blob/main/explorer-files-docker.png)

## Características

- **Navegación de directorios:** Muévete entre carpetas con una navegación de tipo "breadcrumb".
- **Visualización de contenido:** Lista los archivos y carpetas del directorio actual.
- **Subida de archivos:** Sube archivos directamente al directorio actual.
- **Creación de carpetas:** Crea nuevas carpetas para organizar tus archivos.
- **Descarga de archivos:** Descarga cualquier archivo con un solo clic.
- **Contenedorizada con Docker:** Lista para ser desplegada como un contenedor en cualquier plataforma compatible.

## Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

```sh
file-explorer-app/
├── templates/
│ └── index.html # Interfaz de usuario (frontend)
├── app.py # Lógica de la aplicación (backend)
├── Dockerfile # Instrucciones para construir la imagen del contenedor
└── requirements.txt # Dependencias de Python
```

## Requisitos Previos

Antes de comenzar, asegúrate de tener lo siguiente:

- Una suscripción de Azure activa.
- Azure CLI instalado y configurado.
- Docker Desktop instalado (para pruebas locales, opcional para el despliegue).
- Un Grupo de Recursos en Azure.
- Un Azure Container Registry (ACR) para almacenar la imagen Docker.
- Una Cuenta de Almacenamiento (Storage Account) de Azure.

## Pasos para el Despliegue en Azure App Service

Sigue estos pasos para desplegar la aplicación en un App Service para Contenedores.

### 1. Construir y Subir la Imagen Docker

Desde la raíz del proyecto, ejecuta el siguiente comando para construir la imagen Docker y subirla a tu Azure Container Registry. Reemplaza `<tu-registro>` con el nombre de tu ACR.

```bash
az acr build --registry <tu-registro> --image file-explorer-app:latest .
```

### 2. Crear el Recurso Compartido de Azure Files

Esta aplicación requiere un volumen de lectura/escritura. **Azure Blob Storage no funcionará**, ya que se monta como solo lectura. Debes usar **Azure Files**.

- Ve a tu Cuenta de Almacenamiento en el Portal de Azure.
- En el menú lateral, selecciona **"Recursos compartidos de archivos" (File shares)**.
- Haz clic en **"+ Recurso compartido de archivos"** y crea uno nuevo (por ejemplo, `app-data`).

---

### 3. Crear el App Service

En el Portal de Azure, crea un nuevo recurso de tipo **"Aplicación web" (Web App)**.

En la configuración básica:

- **Publicar:** Contenedor Docker
- **Sistema operativo:** Linux
- **Plan de App Service:** Elige o crea uno nuevo.

En la pestaña **"Contenedor"**:

- **Origen de la imagen:** Azure Container Registry
- Selecciona tu **Registro**, la **Imagen (`file-explorer-app`)** y la **Etiqueta (`latest`)**.

---

### 4. Configurar el Montaje de Almacenamiento (Paso Crítico)

Una vez creado el App Service, debes montar el recurso compartido de archivos como un volumen.

- Ve a tu App Service y en el menú lateral selecciona:
  - **Configuración -> Trazado de rutas (Path mappings)**.
- Haz clic en **"+ Nuevo montaje de Azure Storage"**.
- Configura el montaje de la siguiente manera:
  - **Nombre:** Un nombre descriptivo (ej. `files-data`).
  - **Tipo de almacenamiento:** Azure Files (**¡Muy importante!**).
  - **Cuenta de almacenamiento:** Selecciona tu cuenta de almacenamiento.
  - **Contenedor de almacenamiento:** Selecciona el recurso compartido de archivos que creaste en el paso 2 (ej. `app-data`).
  - **Ruta de montaje:** `/mnt/azure` (esta ruta debe coincidir con la variable `MOUNT_PATH` en el Dockerfile).
- Haz clic en **Aceptar**.

---

### 5. Configurar Variables de Entorno (Paso Crítico)

Para asegurar que el montaje tenga permisos de escritura, debes deshabilitar el almacenamiento persistente nativo de App Service.

- Ve a tu App Service:
  - **Configuración -> Configuración de la aplicación (Application settings)**.
- Haz clic en **"+ Nueva configuración de la aplicación"**.
- Añade la siguiente variable:
  - **Nombre:** `WEBSITES_ENABLE_APP_SERVICE_STORAGE`
  - **Valor:** `false`
- Haz clic en **Aceptar**.

---

### 6. Guardar y Probar

En la parte superior de la página de configuración, haz clic en **Guardar**. La aplicación se reiniciará.

Una vez reiniciada, navega a la URL de tu App Service:

https://<tu-app-name>.azurewebsites.net

Deberías ver la interfaz del explorador de archivos.

Prueba a crear una carpeta y subir un archivo para verificar que los permisos de escritura funcionan correctamente.

---

## Solución de Problemas Comunes

### Error `Read-only file system`

Este error ocurre si:

- Intentaste montar un Azure Blob Storage en lugar de Azure Files.
- La variable `WEBSITES_ENABLE_APP_SERVICE_STORAGE` no está configurada en `false`.

---

### La aplicación no se inicia o falla

- Ve a la sección:
  - **Supervisión -> Flujo de registro (Log stream)** en tu App Service para ver los logs del contenedor en tiempo real.
- Esto te dará pistas sobre cualquier error de sintaxis en el código Python o problemas de inicio.
