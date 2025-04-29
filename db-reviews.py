import pandas as pd
import os
from glob import glob
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import shutil

# --- CONFIGURACIÓN INICIAL ---
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

GOOGLE_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1TgRbf-FE_HeKIG5vVEW0tlljiSQpTN3FVL7JYq6-fJc/edit?usp=sharing"
SHEET_NAME = "Reviews"

# --- CONEXIÓN A GOOGLE SHEETS ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(SPREADSHEET_URL)
worksheet = spreadsheet.worksheet(SHEET_NAME)

# --- CARGAR CSV MÁS RECIENTE ---
csv_files = glob("dataReviews/*.csv")
if not csv_files:
    raise FileNotFoundError("❌ No se encontró ningún archivo .csv en 'dataReviews/'")

latest_csv = max(csv_files, key=os.path.getctime)
print(f"📂 Archivo CSV seleccionado: {latest_csv}")
df = pd.read_csv(latest_csv, encoding='utf-8')

# --- TRANSFORMAR COLUMNA DE FECHA ---
df["Review date"] = pd.to_datetime(df["Review date"], format="%b %d, %Y").dt.strftime("%m/%d/%Y")

# --- FORMATEAR COLUMNAS ---
df_transformed = df[[ 
    "Source", "Restaurant name", "Review date", "Overall rating", "Food",
    "Service", "Noise", "Ambience", "Review comments", "Guest name", "Restaurant reply"
]].copy()

df_transformed["Count review"] = df_transformed["Overall rating"].apply(lambda x: 1 if pd.notna(x) else 0)
df_transformed["Count comment"] = df_transformed["Review comments"].apply(lambda x: 1 if pd.notna(x) and str(x).strip() else 0)

df_transformed = df_transformed[[ 
    "Source", "Restaurant name", "Review date", "Count review", "Overall rating",
    "Food", "Service", "Noise", "Ambience", "Count comment",
    "Review comments", "Guest name", "Restaurant reply"
]]

# --- AGREGAR DATOS DE EXCEL SI HAY ---
xlsx_files = glob("data/*.xlsx")
if xlsx_files:
    latest_xlsx = max(xlsx_files, key=os.path.getctime)
    print(f"📄 Archivo Excel seleccionado: {latest_xlsx}")
    feedback = pd.read_excel(latest_xlsx)

    if "Overall Score" in feedback.columns:
        valid_feedback = feedback[feedback["Overall Score"] > 0].copy()
        valid_feedback["Review date"] = pd.to_datetime(valid_feedback["Reservation Date"]).dt.strftime('%m/%d/%Y')
        valid_feedback["Overall rating"] = valid_feedback["Overall Score"]
        valid_feedback["Review comments"] = valid_feedback["Feedback Notes"]
        valid_feedback["Guest name"] = valid_feedback["Full Name"]
        valid_feedback["Source"] = "SevenRooms"
        valid_feedback["Restaurant name"] = "Francesco Restaurant"
        valid_feedback["Count review"] = valid_feedback["Overall rating"].apply(lambda x: 1 if pd.notna(x) else 0)
        valid_feedback["Count comment"] = valid_feedback["Review comments"].apply(lambda x: 1 if pd.notna(x) and str(x).strip() else 0)

        for col in df_transformed.columns:
            if col not in valid_feedback.columns:
                valid_feedback[col] = ""

        valid_feedback = valid_feedback[df_transformed.columns]
        df_transformed = pd.concat([df_transformed, valid_feedback], ignore_index=True)

# --- LIMPIAR Y SUBIR ---
df_transformed = df_transformed.replace([float("inf"), float("-inf")], pd.NA).fillna("")
worksheet.append_rows(df_transformed.values.tolist(), value_input_option="USER_ENTERED")
print("✅ Nuevos datos agregados exitosamente a la hoja 'Reviews'.")

# --- MOVER CSV PROCESADO ---
destination_folder = "processedData"
os.makedirs(destination_folder, exist_ok=True)
shutil.move(latest_csv, os.path.join(destination_folder, os.path.basename(latest_csv)))
print(f"📦 Archivo procesado movido a '{destination_folder}/'.")
