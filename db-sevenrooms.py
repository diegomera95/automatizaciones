import pandas as pd 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
from glob import glob

# 🟢 Cargar variables del entorno
load_dotenv('/home/pautadigital/Projects/dotfiles/Automatizaciones/.env')
credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')

# Buscar el archivo más reciente en la carpeta "data"
files = glob("data/*.xlsx")
if not files:
    raise FileNotFoundError("⚠️ No se encontró ningún archivo .xlsx en la carpeta 'data/'.")
latest_file = max(files, key=os.path.getctime)
input_path = latest_file
print(f"📂 Archivo seleccionado: {input_path}")

# Cargar archivo Excel
df = pd.read_excel(input_path)

# Eliminar columna A (Unnamed)
df = df.drop(columns=["Unnamed: 0"])

# Formatear fechas
df["Created Date"] = pd.to_datetime(df["Created Date"]).dt.strftime('%m/%d/%Y')
df["Reservation Date"] = pd.to_datetime(df["Reservation Date"]).dt.strftime('%m/%d/%Y')
df["Updated - Local Date"] = pd.to_datetime(df["Updated - Local Date"]).dt.strftime('%m/%d/%Y')
df["Created Time"] = pd.to_datetime(df["Created Time"]).dt.strftime('%m/%d/%Y %H:%M:%S')
df["Updated - Local Time"] = pd.to_datetime(df["Updated - Local Time"]).dt.strftime('%m/%d/%Y %H:%M:%S')

# Renombrar columna M y limpiar su contenido
df.rename(columns={"Confirmation #": "REV"}, inplace=True)
df["REV"] = ""

# Mapeo REV según Booked By
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
    "WIDGET": ["Booking Widget"]
}

# Asignar REV según Booked By
df["REV"] = "OTROS"  # Valor por defecto
for rev, names in rev_mapping.items():
    df.loc[df["Booked By"].isin(names), "REV"] = rev

# Limpiar "+" en columna Phone Number
df["Phone Number"] = df["Phone Number"].astype(str).str.replace("+", "", regex=False)

# Reemplazar valores problemáticos antes de subir
df = df.replace([float("inf"), float("-inf")], pd.NA)
df = df.fillna("")

# Conexión a Google Sheets con ruta desde .env
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)

# Abrir archivo y seleccionar hoja
spreadsheet = client.open_by_key("1TgRbf-FE_HeKIG5vVEW0tlljiSQpTN3FVL7JYq6-fJc")
try:
    worksheet = spreadsheet.worksheet("Sevenrooms")
except gspread.exceptions.WorksheetNotFound:
    worksheet = spreadsheet.add_worksheet(title="Sevenrooms", rows="1000", cols="50")
    worksheet.append_row(df.columns.tolist())

worksheet.append_rows(df.values.tolist(), value_input_option="USER_ENTERED")

print("✅ Datos agregados a la hoja 'Sevenrooms' sin sobreescribir.")
