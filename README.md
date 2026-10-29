# Strava to Google Sheets Auto-Sync 🚴‍♂️📊

Este proyecto automatiza la extracción diaria de entrenamientos desde Strava y su volcado en un documento de Google Sheets utilizando un script en Python y GitHub Actions. 

Es una arquitectura *serverless* y de coste cero, diseñada para alimentar posteriormente una IA (Gemini) que actúa como entrenador personal, ajustando la planificación para la **Cactus Challenge**.

## 🚀 Cómo funciona

1. **GitHub Actions** ejecuta el script `main.py` todos los días a las 05:00 UTC (madrugada).
2. El script se conecta a la **API de Strava** usando un *Refresh Token* para obtener los datos del último entrenamiento (Duración, Vatios, FC, Carga, Desnivel).
3. Se conecta a **Google Sheets** mediante una Service Account y añade una nueva fila en la pestaña `Seguimiento de entrenos`.

---

## 🛠️ Configuración Paso a Paso

### Paso 1: Configurar Google Cloud y Google Sheets
1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com).
2. Habilita las APIs: **Google Sheets API** y **Google Drive API**.
3. Ve a **IAM y administración > Cuentas de servicio** y crea una nueva.
4. En la pestaña de "Claves", genera una nueva clave en formato **JSON** y descárgala.
5. Abre tu archivo de Google Sheets, haz clic en "Compartir" y dale permisos de **Editor** al correo electrónico de la cuenta de servicio (ej. `tu-bot@tu-proyecto.iam.gserviceaccount.com`).

### Paso 2: Obtener Credenciales de Strava
1. Ve a [Configuración de API en Strava](https://www.strava.com/settings/api) y crea una aplicación (en *Authorization Callback Domain* pon `localhost`).
2. Apunta tu **Client ID** (ID de cliente) y **Client Secret** (Secreto de cliente).
3. Para obtener el *Refresh Token* con permisos completos, pega esta URL en tu navegador sustituyendo `TU_CLIENT_ID`:
   `https://www.strava.com/oauth/authorize?client_id=TU_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all`
4. Autoriza la app. Serás redirigido a una página de error. Copia el valor del parámetro `code` que aparece en la barra de direcciones de tu navegador.
5. Abre la consola del sistema (cmd) y ejecuta:
   ```cmd
   curl.exe -X POST https://www.strava.com/oauth/token -d client_id=TU_CLIENT_ID -d client_secret=TU_CLIENT_SECRET -d code=EL_CODIGO_COPIADO -d grant_type=authorization_code
   ```
6. Del JSON que te devuelva, copia el valor de `refresh_token`.

### Paso 3: Configurar el Repositorio de GitHub
Debes tener la siguiente estructura de archivos en tu repositorio:
*   `main.py`: Contiene la lógica de extracción y escritura.
*   `requirements.txt`: Contiene las dependencias (`requests`, `gspread`, `google-auth`).
*   `.github/workflows/strava_sync.yml`: Contiene la configuración del cron job de GitHub Actions.

### Paso 4: Configurar los Secretos en GitHub (¡Crítico!)
Para que el script funcione de forma segura, ve a la pestaña de tu repositorio en GitHub: **Settings > Secrets and variables > Actions** y añade los siguientes secretos de repositorio (*New repository secret*):

*   `STRAVA_CLIENT_ID`: Tu ID numérico de Strava.
*   `STRAVA_CLIENT_SECRET`: Tu secreto alfanumérico de Strava.
*   `STRAVA_REFRESH_TOKEN`: El token final que obtuviste en el Paso 2.
*   `GOOGLE_CREDENTIALS_JSON`: Todo el contenido (con llaves `{}` incluidas) del archivo JSON que descargaste de Google Cloud en el Paso 1.

### Paso 5: Ejecución y Pruebas
*   **Automática:** El flujo está configurado en el archivo `.yml` para ejecutarse solo cada día a las 05:00 UTC mediante un `cron`.
*   **Manual:** Puedes forzar la ejecución yendo a la pestaña **Actions** en GitHub, seleccionando "Strava to Google Sheets Sync" en la izquierda, y haciendo clic en **Run workflow**.

---
*Diseñado para la planificación de MTB 2026.*