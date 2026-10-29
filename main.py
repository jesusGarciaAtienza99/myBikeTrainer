import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# Extrae secretos desde variables de entorno (GitHub Secrets)
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# ID de tu documento "Plan Entrenamiento MTB"
SHEET_ID = "1yFRhrlo45UDiLIdQje4UR5894Rq5Vb7z15NkSfkVr-Q"
SHEET_TAB_NAME = "Seguimiento de entrenos"

def get_strava_access_token():
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "refresh_token": STRAVA_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def get_latest_strava_activity(access_token):
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": 1, "page": 1}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    activities = response.json()

    if not activities:
        return None

    activity = activities[0]
    
    # Mapeo de datos respetando la estructura de tu hoja
    return [
        activity.get("start_date_local", "").split("T")[0],            # Fecha
        activity.get("type", "Unknown"),                               # Tipo
        round(activity.get("moving_time", 0) / 60, 1),                 # Duración (minutos)
        activity.get("total_elevation_gain", 0),                       # Desnivel
        activity.get("suffer_score") or activity.get("kilojoules", 0), # Carga
        activity.get("average_heartrate", 0),                          # FC Media
        activity.get("average_watts", 0)                               # Potencia Media
    ]

def append_to_sheet(row_data):
    credentials_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    client = gspread.authorize(creds)

    # Abre la hoja y añade la nueva fila al final
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_TAB_NAME)
    sheet.append_row(row_data)

def main():
    try:
        print("Obteniendo token de Strava...")
        access_token = get_strava_access_token()

        print("Recuperando última actividad...")
        row_data = get_latest_strava_activity(access_token)

        if row_data:
            print(f"Actividad procesada: {row_data}. Insertando en Google Sheets...")
            append_to_sheet(row_data)
            print("Operación completada con éxito.")
        else:
            print("No se encontraron actividades recientes.")

    except Exception as e:
        print(f"Error crítico en el flujo de extracción: {e}")
        raise

if __name__ == "__main__":
    main()
