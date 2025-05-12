import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from glob import glob
from pathlib import Path
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

GOOGLE_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
SPREADSHEET_ID = "1TgRbf-FE_HeKIG5vVEW0tlljiSQpTN3FVL7JYq6-fJc"
SHEET_NAME = "Sevenrooms"

# --- PROCESAR ARCHIVO MÁS RECIENTE ---
files = glob("data/*.xlsx")
if not files:
    raise FileNotFoundError("⚠️ No se encontró ningún archivo .xlsx en la carpeta 'data/'.")

latest_file = max(files, key=os.path.getctime)
print(f"📂 Archivo seleccionado: {latest_file}")

df = pd.read_excel(latest_file)
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# --- LIMPIEZA Y FORMATEO ---
df["Created Date"] = pd.to_datetime(df["Created Date"]).dt.strftime('%m/%d/%Y')
df["Reservation Date"] = pd.to_datetime(df["Reservation Date"]).dt.strftime('%m/%d/%Y')
df["Updated - Local Date"] = pd.to_datetime(df["Updated - Local Date"]).dt.strftime('%m/%d/%Y')
df["Created Time"] = pd.to_datetime(df["Created Time"]).dt.strftime('%m/%d/%Y %H:%M:%S')
df["Updated - Local Time"] = pd.to_datetime(df["Updated - Local Time"]).dt.strftime('%m/%d/%Y %H:%M:%S')

df.rename(columns={"Confirmation #": "REV"}, inplace=True)
df["REV"] = ""

rev_mapping = {
    "CP": ["Cynthia Pinto"],
    "FB": ["Facebook"],
    "FD": ["Franco Danovaro", "Franco D."],
    "GOOGLE": ["Google Reserve Integration"],
    "HOST": ["Thalia Caceres", "Navelin", "Alejandra", "Richard Mendez", "Thalia", "Erick Arteta", "Franco Jr. Delgado"],
    "IG": ["Instagram"],
    "MAILING": ["Mailing", "Valentine’s Day - Landing Page"],
    "MAYA": ["Maria Jose Calmet"],
    "OT": ["Open Table"],
    "RP": ["Ricardo de Páramo", "Ricardo De Paramo"],
    "WALK-IN": ["Walk In"],
    "SMS": ["SMS"],
    "WIDGET": ["Booking Widget"]
}

df["REV"] = "OTROS"
for rev, names in rev_mapping.items():
    df.loc[df["Booked By"].isin(names), "REV"] = rev

df["Phone Number"] = df["Phone Number"].astype(str).str.replace("+", "", regex=False)
df = df.replace([float("inf"), float("-inf")], pd.NA).fillna("")

# --- CONEXIÓN GOOGLE SHEETS ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# --- SUBIR DATOS ---
try:
    worksheet = spreadsheet.worksheet(SHEET_NAME)
except gspread.exceptions.WorksheetNotFound:
    worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows="1000", cols="50")
    worksheet.append_row(df.columns.tolist())

worksheet.append_rows(df.values.tolist(), value_input_option="USER_ENTERED")
print(f"✅ Datos agregados a la hoja '{SHEET_NAME}' sin sobreescribir.")
