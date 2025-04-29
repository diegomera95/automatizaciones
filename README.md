
# 📊 Automatizaciones de Pauta Digital

Este repositorio contiene scripts de automatización para el procesamiento y carga de datos en Google Sheets, integrando fuentes como archivos Excel, CSV y datos de plataformas como SevenRooms y Meta Ads. Está diseñado para sincronizarse automáticamente con Google Sheets mediante cron jobs y mantener un flujo de datos ordenado y escalable.

## ⚙️ Requisitos

- Python 3.9 o superior (idealmente gestionado con pyenv).
- Entorno virtual con dependencias del archivo requirements.txt.
- Acceso habilitado a la API de Google Sheets y Meta Ads.
- Archivo .env ubicado en la raíz del proyecto.

## 🧪 Variables de entorno

El archivo .env debe contener las siguientes claves:

GOOGLE_SHEETS_CREDENTIALS_PATH=/ruta/absoluta/a/credenciales.json
META_ACCESS_TOKEN=tu_token_de_meta

## 🚀 Instalación

1. Clona el repositorio:

    git clone git@github.com:diegomera95/automatizaciones.git
    cd automatizaciones

2. Crea un entorno virtual e instala dependencias:

    pip install -r requirements.txt

3. Coloca tu archivo .env y las credenciales en la ubicación correcta.

## 🧩 Uso de scripts

Ejecuta cualquier script con:

python nombre_del_script.py

Ejemplos:

python meta_gastos_mes.py
python db-sevenrooms.py
python db-partition.py
python db-reviews.py

## ⏰ Automatización con cron

El script meta_gastos_mes.py se ejecuta automáticamente cada día a las 07:30 a.m. gracias a una tarea programada (cron) definida así:

30 7 * * * /ruta/a/python3 /ruta/al/proyecto/meta_gastos_mes.py >> /ruta/al/log/meta.log 2>&1

El resultado se guarda en cron_logs/meta.log.

## 🔒 Seguridad

- El archivo .env y la carpeta credenciales/ están excluidos del repositorio mediante .gitignore.
- Nunca subas claves ni tokens a un repositorio público.

## 📦 Dependencias (requirements.txt)

pandas
gspread
oauth2client
python-dotenv
openpyxl
facebook_business

## ✨ Autor

Diego Mera
@diegomera95
