from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CARGAR VARIABLES DE ENTORNO ---
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
SPREADSHEET_ID = '1aHr-kK7QY5TffvjtpzpjW9jNrPfCyajzxMzScCuJkjY'

CUENTAS = {
    'V&V cuenta A': 'act_1380727158859329',
    'V&V cuenta B': 'act_1035094996689812'
}

FacebookAdsApi.init(access_token=ACCESS_TOKEN)

# --- CONEXIÓN GOOGLE SHEETS ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# --- FECHAS ---
DATE_START = '2025-03-01'
DATE_END = '2025-05-31'

# --- CAMPOS DE MÉTRICAS ---
fields = [
    'campaign_id', 'campaign_name', 'adset_name', 'adset_id',
    'actions', 'reach', 'impressions', 'cost_per_action_type',
    'spend', 'video_p50_watched_actions', 'frequency', 'cpc', 'ctr'
]

params = {
    'time_range': {'since': DATE_START, 'until': DATE_END},
    'level': 'adset',
    'limit': 500
}

for nombre, cuenta_id in CUENTAS.items():
    print(f"Procesando {nombre}...")
    cuenta = AdAccount(cuenta_id)
    insights = cuenta.get_insights(fields=fields, params=params)

    registros = []
    for i in insights:
        if float(i.get('spend', 0)) <= 0:
            continue

        def extraer_metricas(key, field='value'):
            return next((x.get(field, '') for x in i.get(key, []) if field in x), '')

        registros.append({
            'Campaña ID': i.get('campaign_id'),
            'Nombre Campaña': i.get('campaign_name'),
            'Adset ID': i.get('adset_id'),
            'Nombre Adset': i.get('adset_name'),
            'Tipo de Resultado': extraer_metricas('actions', 'action_type'),
            'Resultados': extraer_metricas('actions'),
            'Alcance': i.get('reach'),
            'Impresiones': i.get('impressions'),
            'Costo por Resultado': extraer_metricas('cost_per_action_type'),
            'Importe gastado (USD)': i.get('spend'),
            'Reproducciones video 50%': extraer_metricas('video_p50_watched_actions'),
            'Frecuencia': i.get('frequency'),
            'CPC': i.get('cpc'),
            'CTR': i.get('ctr')
        })

    df = pd.DataFrame(registros)

    # SUBIR A GOOGLE SHEETS
    try:
        worksheet = spreadsheet.worksheet(nombre)
        spreadsheet.del_worksheet(worksheet)
    except gspread.exceptions.WorksheetNotFound:
        pass

    worksheet = spreadsheet.add_worksheet(title=nombre, rows="1000", cols="20")
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    print(f"✅ Datos subidos: {nombre}")
