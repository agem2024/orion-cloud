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
OWNER_ID = 5989183300  # Alex - puede usar comandos especiales
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
        
        # Detectar Idioma
        lang_code = msg["from"].get("language_code", "en")
        lang = "es" if lang_code.startswith("es") else "en"
        
        is_owner = (user_id == OWNER_ID)
        response_text = ""

        # Manejo de voz
        if "voice" in msg:
            response_text = "🎤 Audio recibido. Función en desarrollo."
        
        # Manejo de texto
        elif "text" in msg:
            text = msg["text"]
            text_lower = text.lower().strip()
            
            # /start - Todos
            if text_lower.startswith("/start"):
                if is_owner:
                    response_text = "🚀 *ORION CLOUD ONLINE*\n👑 Owner Mode: ACTIVADO\n\n*📖 COMANDOS:*\n\n*Accesos:*\n/acutor - Manual ORION\n/pb - Price Book\n/apps - Orion Apps\n/otp - Orion Bots\n\n*Profesional:*\n/cv - CV profesional\n/tj - Tarjeta trabajo\n/skills - Skills técnicas\n/landing - Landing page\n\n*Sistema:*\n/status - Estado\n/stats - Estadísticas\n/ayuda - Ver comandos\n\nO escribe cualquier cosa para hablar con XONA."
                else:
                    response_text = "👋 *¡Hola! Soy XONA*, asistente de ORION Tech.\n\n¿En qué puedo ayudarte hoy?\n\n📱 WhatsApp: (669) 234-2444\n🌐 Servicios de IA y Automatización"
            
            # ============ ACCESOS DIRECTOS ============
            elif text_lower.startswith("/acutor") or text_lower == "manual":
                response_text = "📖 *MANUAL ORION SYSTEM*\n\n🔗 https://neon-agent-hub.web.app/jarvis_manual.html\n\n✅ Link Público - Guárdalo!"
            
            elif text_lower.startswith("/pb") or text_lower == "pricebook":
                response_text = "💰 *PRICE BOOK v6.0 PRO*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/pricebook.html\n\n✅ 100 Servicios\n💵 Precios: Estándar/Miembro/Emergencia\n🎯 Sistema Good/Better/Best"
            
            elif text_lower.startswith("/apps") or text_lower == "links":
                response_text = "🔗 *ORION APPS*\n\n1️⃣ https://ai.studio/apps/drive/1vikKncwaJRxWOANGeEcnchTAM96CqmnZ\n2️⃣ https://ai.studio/apps/drive/1bMGhzGDqLL_aDfnSC78Ie_HnsF7b691I\n3️⃣ https://ai.studio/apps/drive/1BKOJ2-29twcjdG1BooF6-Nh82VpXm6Hi\n\n_Modo App habilitado_"
            
            elif text_lower.startswith("/otp") or text_lower == "orion bots":
                response_text = "🤖 *ORION BOTS - Landing*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/orion-bots.html\n\n✨ Servicios de Automatización WhatsApp\n🚀 Bots Personalizados"
            
            # ============ PROFESIONAL ============
            elif text_lower.startswith("/cv"):
                response_text = "📄 *CV PROFESIONAL*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/cv_pro.html\n\n👤 Alex G. Espinosa\n🎯 AI Architect | 21+ años experiencia"
            
            elif text_lower.startswith("/tj"):
                response_text = "💼 *TARJETA DIGITAL*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/card.html\n\n📱 Contacto profesional digital"
            
            elif text_lower.startswith("/skills"):
                response_text = "🛠️ *SKILLS TÉCNICAS*\n\n• Python, JavaScript, Node.js\n• AI/ML (Gemini, OpenAI, LangChain)\n• WhatsApp Automation (Baileys)\n• Cloud (Firebase, Render, Vercel)\n• 21+ años ingeniería"
            
            elif text_lower.startswith("/landing"):
                response_text = "🌐 *LANDING PAGE*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/orion-bots.html\n\n🚀 ORION Tech - AI Solutions"
            
            # ============ SISTEMA (SOLO OWNER) ============
            elif text_lower.startswith("/status") and is_owner:
                response_text = "🟢 *ORION CLOUD STATUS*\n\n✅ Brain: Online\n✅ Webhook: Active\n✅ API: Running\n\n🌐 https://orion-cloud.onrender.com"
            
            elif text_lower.startswith("/stats") and is_owner:
                response_text = "📊 *ESTADÍSTICAS*\n\n🤖 Sistema: XONA v2.0\n☁️ Host: Render\n🧠 IA: Gemini/OpenAI\n\n_Stats detalladas próximamente_"
            
            elif text_lower.startswith("/ayuda") or text_lower == "help" or text_lower == "?":
                response_text = "❓ *AYUDA ORION CLOUD*\n\n*📖 Accesos:*\n/acutor - Manual\n/pb - Price Book\n/apps - Orion Apps\n/otp - Orion Bots\n\n*💼 Profesional:*\n/cv - CV\n/tj - Tarjeta\n/skills - Skills\n/landing - Landing\n\n*🔧 Sistema:*\n/status - Estado\n/stats - Stats\n\n_O escribe cualquier pregunta para XONA_"
            
            # Cualquier otro texto - XONA responde a TODOS
            else:
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
