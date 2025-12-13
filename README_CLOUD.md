# ☁️ GUÍA DE DESPLIEGUE: ORION CLOUD (Telegram)

Sigue estos pasos para subir tu "Cerebro Telegram" a la nube (Render) GRATIS.

## 1. Preparativos
1.  Crea un repositorio en GitHub llamado `telegram-orion-cloud`.
2.  Sube el contenido de la carpeta `telegram-cloud-bot` a ese repositorio.

## 2. Crear Servicio en Render
1.  Ve a [dashboard.render.com](https://dashboard.render.com) y crea una cuenta.
2.  Click en **"New + "** -> **"Web Service"**.
3.  Conecta tu repositorio de GitHub.
4.  Configura lo siguiente:
    *   **Name:** `orion-telegram`
    *   **Runtime:** Python 3
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
    *   **Instance Type:** Free

## 3. Variables de Entorno (Environment Variables)
En la sección "Environment" de Render, agrega estas claves:

| Key | Value |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Tu Token Nuevo de BotFather |
| `OPENAI_API_KEY` |`sk-proj-...` (Tu llave OpenAI) |
| `GEMINI_API_KEY` | `AIza...` (Tu llave Gemini, opcional) |
| `TELEGRAM_OWNER_ID` | `8572298959` (Tu ID personal de Telegram) |
| `BASE_URL` | La URL que te da Render (ej: `https://orion-telegram.onrender.com`) |

Dale a **"Create Web Service"**. Espera a que diga "Live" 🟢.

## 4. Conectar el Cable (Webhook)
Render te dará una URL (ej: `https://orion-telegram.onrender.com`).
1.  Abre el archivo `set_webhook.py` en tu PC.
2.  Pega tu TOKEN y esa URL donde indica.
3.  Ejecuta: `python set_webhook.py` en tu terminal local.

✅ **¡LISTO!** Tu bot de Telegram ahora vive en la nube, protegido y con XONA.
El bot local (`orion-clean`) sigue manejando WhatsApp y Voz 669.
