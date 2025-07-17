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
SPREADSHEET_ID = os.getenv('VYV_GOOGLE_SHEETS_ID')
SHEET_NAME = "Consumo"

# --- CUENTAS PUBLICITARIAS ---
CUENTAS = {
    'V&V cuenta A': 'act_1380727158859329',
    'V&V cuenta B': 'act_1035094996689812'
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
worksheet = spreadsheet.worksheet(SHEET_NAME)

# --- CAMPOS DE CONSULTA META ---
fields = ['campaign_name', 'spend', 'actions', 'cost_per_action_type', 'reach']
params = {
    'time_range': {'since': fecha_inicio, 'until': fecha_fin},
    'level': 'campaign',
    'limit': 500
}

# --- CAMPOS DE MÉTRICAS ---
todos_los_datos = []

for nombre_cuenta, id_cuenta in CUENTAS.items():
    print(f"📊 Procesando cuenta: {nombre_cuenta} ({id_cuenta})")

    account = AdAccount(id_cuenta)
    insights = account.get_insights(fields=fields, params=params)

    for i in insights:
        gasto = float(i.get('spend', 0))
        if gasto == 0:
            continue

        campaign_name = i.get('campaign_name', '')
        acciones = i.get('actions', [])
        costos = i.get('cost_per_action_type', [])
        alcance = float(i.get('reach', 0))

        # Tipos de resultado priorizados
        tipos_prioritarios = ['lead', 'offsite_conversion', 'complete_registration']

        tipo_resultado = 'N/A'
        valor_resultado = 0

        for tipo in tipos_prioritarios:
            match = next((a for a in acciones if a['action_type'] == tipo), None)
            if match:
                tipo_resultado = tipo
                valor_resultado = float(match['value'])
                break

        if tipo_resultado == 'N/A' and acciones:
            tipo_resultado = acciones[0]['action_type']
            valor_resultado = float(acciones[0]['value'])

        todos_los_datos.append({
            'Fecha Inicio': fecha_inicio,
            'Fecha Fin': fecha_fin,
            'Nombre Campaña': campaign_name,
            'Tipo de Resultado': tipo_resultado,
            'Resultados': valor_resultado,
            'Gasto Total (USD)': gasto
        })

# --- CREAR DATAFRAME Y AGRUPAR CON COSTO POR SULTADOS ---
df_final = pd.DataFrame(todos_los_datos)

if not df_final.empty:
    # Agrupar por campaña y tipo de resultado
    df_final = df_final.groupby(
        ['Fecha Inicio', 'Fecha Fin', 'Nombre Campaña', 'Tipo de Resultado'],
        as_index=False
    ).agg({
        'Resultados': 'sum',
        'Gasto Total (USD)': 'sum'
    })
    # Calcular costo por resultado
    df_final['Costo por Resultado (USD)'] = df_final['Gasto Total (USD)'] / df_final['Resultados'].replace(0, 1)

    # reordenar columnas
    df_final = df_final[
        ['Fecha Inicio', 'Fecha Fin', 'Nombre Campaña', 'Tipo de Resultado', 
         'Resultados', 'Gasto Total (USD)', 'Costo por Resultado (USD)']
        ]
# --- SUBIR A GOOGLE SHEETS ---
# Limpiar y escribir solo si hay datos
if not df_final.empty:
    worksheet.clear()
    worksheet.append_row(df_final.columns.tolist())
    worksheet.append_rows(df_final.values.tolist(), value_input_option="USER_ENTERED")
    print(f"✅ Datos actualizados en la hoja: {SHEET_NAME}")
else:
    print("⚠️ No hay datos con gasto positivo para subir.")

print("🚀 Proceso finalizado para todas las cuentas.")
