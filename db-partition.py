import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
from glob import glob

# 🟢 Cargar variables del entorno
load_dotenv('/home/pautadigital/Projects/dotfiles/Automatizaciones/.env')
credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')

# 🔢 Ingreso de n dinámico por el usuario
n_input = input("🔢 Ingresa el valor de n para calcular Open Table Partition: ")
try:
    n = float(n_input)
except ValueError:
    raise ValueError("❌ Debes ingresar un número válido para n.")

# Buscar archivo más reciente
files = glob("data/*.xlsx")
if not files:
    raise FileNotFoundError("⚠️ No se encontró ningún archivo .xlsx en la carpeta 'data/'.")
latest_file = max(files, key=os.path.getctime)
print(f"📂 Archivo seleccionado: {latest_file}")

# Leer el archivo
df = pd.read_excel(latest_file)
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# Filtrar y renombrar columnas
df = df[[
    "Venue Name", "Reservation Date", "Reservation Status",
    "Detailed Status", "Confirmation #", "Booked By", "Booked Covers"
]].copy()
df.columns = [
    "Venue Name", "Reservation Date", "Reservation Status",
    "Detailed Status", "REV 2", "Booked By 2", "Booked Covers 2"
]

# Formatear fechas
df["Reservation Date"] = pd.to_datetime(df["Reservation Date"]).dt.strftime('%m/%d/%Y')

# Asignar REV 2
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
df["REV 2"] = "OTROS"
for rev, names in rev_mapping.items():
    df.loc[df["Booked By 2"].isin(names), "REV 2"] = rev

# Duplicar filas WALK-IN o Walk In solo una vez
rows_to_duplicate = df[(df["REV 2"] == "WALK-IN") | (df["Booked By 2"] == "Walk In")].copy()
duplicates = []
for _, row in rows_to_duplicate.iterrows():
    new_row = row.copy()
    if row["REV 2"] == "WALK-IN":
        new_row["REV 2"] = "WALK-IN 2"
    if row["Booked By 2"] == "Walk In":
        new_row["Booked By 2"] = "Walk In 2"
    duplicates.append(new_row)
df = pd.concat([df, pd.DataFrame(duplicates)], ignore_index=True)

# Calcular columnas de partición
df["Partition Covers 15%"] = ""
df["Partition Covers 85%"] = ""
mask_walkin = df["REV 2"].isin(["WALK-IN", "WALK-IN 2"])
df.loc[mask_walkin, "Partition Covers 15%"] = df.loc[mask_walkin, "Booked Covers 2"] * 0.15
df.loc[mask_walkin, "Partition Covers 85%"] = df.loc[mask_walkin, "Booked Covers 2"] * 0.85

# Open Table Partition
df["Open Table Partition"] = ""
mask_ot = (df["Reservation Status"] == "Complete") & (df["REV 2"] == "OT")
sum_booked = df.loc[mask_ot, "Booked Covers 2"].sum()
df.loc[mask_ot, "Open Table Partition"] = df.loc[mask_ot, "Booked Covers 2"] - (
    df.loc[mask_ot, "Booked Covers 2"] * (n / sum_booked)
)

# Agregar fila OT PAUTA
min_date = df.loc[df["REV 2"] == "WALK-IN", "Reservation Date"].min()
pauta_row = pd.DataFrame([{
    "Venue Name": "Francesco Restaurant",
    "Reservation Date": min_date,
    "Reservation Status": "Complete",
    "Detailed Status": "COMPLETE",
    "REV 2": "OT PAUTA",
    "Booked By 2": "Open Table Pauta",
    "Partition Covers 15%": "",
    "Partition Covers 85%": "",
    "Open Table Partition": n,
    "Booked Covers 2": ""
}])

df = pd.concat([pauta_row, df], ignore_index=True)

# Reordenar columnas
df = df[[
    "Venue Name", "Reservation Date", "Reservation Status",
    "Detailed Status", "REV 2", "Booked By 2",
    "Partition Covers 15%", "Partition Covers 85%",
    "Open Table Partition", "Booked Covers 2"
]]

# 🔐 Conexión a Google Sheets con ruta desde .env
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1TgRbf-FE_HeKIG5vVEW0tlljiSQpTN3FVL7JYq6-fJc")
try:
    worksheet = sheet.worksheet("DB Partition")
except gspread.exceptions.WorksheetNotFound:
    worksheet = sheet.add_worksheet(title="DB Partition", rows="1000", cols="20")

# 📥 Insertar datos nuevos debajo de los existentes
existing_data = worksheet.get_all_values()
start_row = len(existing_data) + 1 if existing_data else 1

if not existing_data:
    worksheet.append_row(df.columns.tolist())  # Insertar encabezados si no existen

worksheet.append_rows(df.values.tolist(), value_input_option="USER_ENTERED")

print("✅ Datos agregados a la hoja 'DB Partition' sin borrar información anterior.")
