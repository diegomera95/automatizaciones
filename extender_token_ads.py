import requests
from dotenv import load_dotenv
import os

# Cargar variables del .env
load_dotenv()

APP_ID = os.getenv('FB_APP_ID')
APP_SECRET = os.getenv('FB_APP_SECRET')
ADS_SHORT_TOKEN = os.getenv('META_SHORT_TOKEN')  

# Llamada para extender el token
url = 'https://graph.facebook.com/v19.0/oauth/access_token'
params = {
    'grant_type': 'fb_exchange_token',
    'client_id': APP_ID,
    'client_secret': APP_SECRET,
    'fb_exchange_token': ADS_SHORT_TOKEN
}

response = requests.get(url, params=params)
data = response.json()

# Mostrar el nuevo token
print("\n✅ Token extendido para Ads u otros scopes:")
print(data)
