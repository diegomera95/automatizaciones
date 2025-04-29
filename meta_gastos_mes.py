import os
from pathlib import Path
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import pandas as pd
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CARGAR VARIABLES DE ENTORNO ---
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
SPREADSHEET_ID = '1IDqBepiLEfxUqpRYvYu89M6hih3aRXPQrl9rhzjZD-s'

# --- CUENTAS PUBLICITARIAS ---
CUENTAS = {
    'V&V cuenta A': 'act_1380727158859329',
    'V&V cuenta B': 'act_1035094996689812',
    'VYVE': 'act_2306912219555630',
    'Francesco': 'act_282927489898717'
}

# --- RANGO DE FECHAS: del 1 al día anterior ---
hoy = datetime.now()
fecha_inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
fecha_fin = (hoy - timedelta(days=1)).strftime('%Y-%m-%d')

# --- CONEXIÓN META ADS ---
FacebookAdsApi.init(access_token=ACCESS_TOKEN)

# --- CONEXIÓN GOOGLE SHEETS ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# --- CAMPOS DE CONSULTA META ---
fields = ['campaign_name', 'adset_name', 'spend']
params = {
    'time_range': {'since': fecha_inicio, 'until': fecha_fin},
    'level': 'adset',
    'limit': 500
}

# --- PROCESAMIENTO POR CUENTA ---
for nombre_cuenta, id_cuenta in CUENTAS.items():
    print(f"📊 Procesando cuenta: {nombre_cuenta} ({id_cuenta})")

    account = AdAccount(id_cuenta)
    insights = account.get_insights(fields=fields, params=params)

    datos = []
    for i in insights:
        gasto = float(i.get('spend', 0))
        if gasto > 0:
            datos.append({
                'Fecha Inicio': fecha_inicio,
                'Fecha Fin': fecha_fin,
                'Nombre Campaña': i.get('campaign_name', ''),
                'Nombre Conjunto de Anuncios': i.get('adset_name', ''),
                'Gasto Total (USD)': gasto
            })

    df = pd.DataFrame(datos)

    if df.empty:
        df = pd.DataFrame([{
            'Fecha Inicio': fecha_inicio,
            'Fecha Fin': fecha_fin,
            'Nombre Campaña': 'Sin datos con gasto',
            'Nombre Conjunto de Anuncios': '',
            'Gasto Total (USD)': 0.0
        }])

    # --- SUBIR A GOOGLE SHEET ---
    try:
        worksheet = spreadsheet.worksheet(nombre_cuenta)
        spreadsheet.del_worksheet(worksheet)
    except gspread.exceptions.WorksheetNotFound:
        pass

    worksheet = spreadsheet.add_worksheet(title=nombre_cuenta, rows="1000", cols="10")
    worksheet.append_row(df.columns.tolist())
    worksheet.append_rows(df.values.tolist(), value_input_option="USER_ENTERED")

    print(f"✅ Datos subidos a hoja: {nombre_cuenta}")

print("🚀 Proceso finalizado para todas las cuentas.")
