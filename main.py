import os
import logging
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from brain import OrionBrain

# Configuración
app = FastAPI()

# CORS para permitir peticiones desde la web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ORION_CLOUD")

# Variables de Entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_OWNER_ID = int(os.getenv("TELEGRAM_OWNER_ID", "8572298959")) # Whitelist por defecto
BASE_URL = os.getenv("BASE_URL") # URL de Render

# Inicializar Cerebro
brain = OrionBrain()

@app.get("/")
def health():
    return {"status": "ok", "system": "ORION CLOUD v2 - Web Chat Enabled"}

# ============ WEB CHAT API ============
@app.post("/api/chat")
async def web_chat(request: Request):
    """Endpoint para el chatbot web XONA"""
    try:
        data = await request.json()
        message = data.get("message", "")
        lang = data.get("lang", "en")
        
        if not message:
            return {"response": "Please send a message.", "error": True}
        
        response = brain.get_response(message, "web_user", lang)
        return {"response": response, "error": False}
    except Exception as e:
        logger.error(f"Web chat error: {e}")
        return {"response": "Error processing request.", "error": True}

@app.post(f"/webhook/{TELEGRAM_TOKEN}")
async def telegram_webhook(req: Request):
    """Endpoint principal para recibir updates de Telegram"""
    try:
        data = await req.json()
        
        # Verificar si es un mensaje
        if "message" not in data:
            return {"ok": True}
            
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        
        # 🔒 SEGURIDAD: Whitelist Check
        if user_id != TELEGRAM_OWNER_ID:
            logger.warning(f"⛔ Intento de acceso no autorizado: {user_id}")
            return {"ok": True} # Ignorar silenciosamente

        # Detectar Idioma (básico)
        lang_code = msg["from"].get("language_code", "en")
        lang = "es" if lang_code.startswith("es") else "en"

        response_text = ""

        # Manejo de voz
        if "voice" in msg:
            # TODO: Descargar audio y transcribir (requiere manejo de archivos temporales)
            response_text = "🎤 Audio recibido. (Procesamiento de voz en nube pendiente de config de archivos)"
            # Para producción real, aquí descargaríamos el file_id
        
        # Manejo de texto
        elif "text" in msg:
            text = msg["text"]
            
            # Comandos básicos
            if text == "/start":
                response_text = f"🚀 **ORION CLOUD ONLINE**\nID Autorizado: {user_id}\n\nListo para trabajar."
            else:
                # Consultar al Cerebro XONA
                response_text = brain.get_response(text, str(user_id), lang)

        # Enviar respuesta
        if response_text:
            await send_telegram_message(chat_id, response_text)

    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        
    return {"ok": True}

async def send_telegram_message(chat_id: int, text: str):
    """Envía mensaje de vuelta a Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
