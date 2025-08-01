
# Automatizaciones de Pauta Digital – Versión 2.1.0

Este repositorio contiene scripts de automatización para el procesamiento y carga de datos en Google Sheets, integrando fuentes como archivos Excel, CSV y datos de plataformas como **SevenRooms** y **Meta Ads**.

La versión 2.1.0 introduce una nueva funcionalidad clave: **particionado de bases de datos** para optimizar el manejo y segmentación de datos a gran escala, junto con las mejoras previas en seguridad, logging, orquestación y portabilidad.

## Novedades en la versión 2.1.0
- **Partición de datos** en `db_partition.py`, integrado en el flujo de automatizaciones.
- Mantiene todas las mejoras introducidas en la versión 2.0.0:
  - **Archivo `.env`** para gestionar rutas, credenciales y configuraciones sensibles.
  - **Nuevo script `run_all.sh`** para ejecutar de forma secuencial todas las automatizaciones con logs mejorados y manejo de errores.
  - **Logs por script y log general (`ejecuciones.log`)** con fecha y hora.
  - **Script `extender_token_ads.py`** para ampliar la vigencia del token de Meta Ads.
  - Reorganización del proyecto con carpetas `data`, `dataReviews` y `processedData`.

## Requisitos

- Python 3.9 o superior (idealmente gestionado con `pyenv`).
- Entorno virtual con dependencias del archivo `requirements.txt`.
- Acceso habilitado a la API de Google Sheets y Meta Ads.
- Archivo `.env` ubicado en la raíz del proyecto.

## Variables de entorno

El archivo .env debe contener las siguientes claves:

### Credenciales de Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=/ruta/absoluta/a/Automatizaciones/credenciales/credentials.json

### Tokens y credenciales de Meta Ads
META_ACCESS_TOKEN="token extendido para extracción de datos"
META_SHORT_TOKEN="token inicial para solicitar extensión"
FB_APP_ID="facebook app id"
FB_APP_SECRET="facebook app secret"

### IDs de Google Sheets para cada cuenta
FCG_GOOGLE_SHEETS_ID="id del Google Sheet de FCG"
VYV_GOOGLE_SHEETS_ID="id del Google Sheet de VYV"
VYVE_GOOGLE_SHEETS_ID="id del Google Sheet de VYVE"

### Rutas de ejecución y logs
PYTHON_PATH="/ruta/absoluta/a/.pyenv/versions/3.10.13/envs/automatizaciones/bin/python3"
SCRIPTS_DIR="/ruta/absoluta/a/Automatizaciones"
LOG_DIR="/ruta/absoluta/a/cron_logs"

## Instalación

1. Clona el repositorio:

    git clone git@github.com:diegomera95/automatizaciones.git
    cd automatizaciones

2. Crea un entorno virtual e instala dependencias:

    pip install -r requirements.txt

3. Coloca tu archivo .env y las credenciales en la ubicación correcta.

## Uso de scripts

### Ejecuta cualquier script con:

python nombre_del_script.py

Ejemplos:

python meta_gastos_mes.py
python db-sevenrooms.py
python db-partition.py
python db-reviews.py

## Ejecutar todas las automatizaciones con el wrapper:

bash run_all.sh

### Ejemplo para ejecutar el wrapper todos los días a las 09:30 AM:

30 9 * * * /home/usuario/Projects/automatizaciones/run_all.sh

- Ejecuta secuencialmente todos los scripts definidos en run_all.sh.
- Guarda los logs en la carpeta definida en LOG_DIR.


## Seguridad

- El archivo .env y la carpeta credenciales/ están excluidos del repositorio mediante .gitignore.
- Nunca subas claves ni tokens a un repositorio público.

## Dependencias (requirements.txt)

pandas
gspread
oauth2client
python-dotenv
openpyxl
facebook_business
shutil
pathlib
glob2


## Autor

Diego Mera
@diegomera95
