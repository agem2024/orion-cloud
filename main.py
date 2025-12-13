import os
import logging
import httpx
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from brain import OrionBrain
from urllib.parse import quote

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
BASE_URL = os.getenv("BASE_URL")

# Inicializar Cerebro
brain = OrionBrain()

def get_tts_url(text: str, lang: str = "es") -> str:
    """Genera URL de Google TTS (fallback)"""
    text_encoded = quote(text[:200])
    return f"https://translate.google.com/translate_tts?ie=UTF-8&q={text_encoded}&tl={lang}&client=tw-ob"

async def get_openai_tts(text: str) -> bytes:
    """Genera audio con OpenAI TTS HD (voz natural de alta calidad)"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.audio.speech.create(
            model="tts-1-hd",  # HD = Alta definición, más natural
            voice="shimmer",   # shimmer = voz femenina cálida y natural
            input=text[:4096],
            speed=1.0  # Velocidad normal
        )
        return response.content
    except Exception as e:
        logger.error(f"OpenAI TTS error: {e}")
        return None

@app.get("/")
def health():
    return {"status": "ok", "system": "ORION CLOUD v3 - Full Commands"}

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
        
        if "message" not in data:
            return {"ok": True}
            
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        
        lang_code = msg["from"].get("language_code", "en")
        lang = "es" if lang_code.startswith("es") else "en"
        
        is_owner = (user_id == OWNER_ID)

        # Manejo de voz entrante
        if "voice" in msg:
            await send_telegram_message(chat_id, "🎤 Audio recibido. Transcripción en desarrollo.")
            return {"ok": True}
        
        # Manejo de texto
        if "text" not in msg:
            return {"ok": True}
            
        text = msg["text"]
        text_lower = text.lower().strip()
        
        # ============ /START ============
        if text_lower.startswith("/start"):
            if is_owner:
                menu = """🚀 *ORION CLOUD v3 ONLINE*
👑 Owner Mode: ACTIVADO

*📖 COMANDOS DISPONIBLES:*

*🔗 Accesos:*
/acutor - Manual ORION
/pb - Price Book
/apps - Orion Apps
/otp - Orion Bots

*💼 Profesional:*
/cv - CV profesional
/tj - Tarjeta digital
/skills - Skills técnicas
/landing - Landing page

*🎤 Voz & IA:*
/say [texto] - Texto a voz
/orvoz [texto] - IA + voz
/tr [texto] a [idioma] - Traducir

*🔧 Sistema:*
/status - Estado sistema
/stats - Estadísticas
/ayuda - Ver comandos

_Escribe cualquier cosa para hablar con CHONA_"""
                await send_telegram_message(chat_id, menu)
            else:
                await send_telegram_message(chat_id, "👋 *¡Hola parce! Soy CHONA*, asistente de ORION Tech.\n\n¿En qué puedo ayudarte?\n\n📱 WhatsApp: (669) 234-2444\n🌐 Servicios de IA y Automatización")
            return {"ok": True}
        
        # ============ VOZ TTS (OpenAI Natural) ============
        if text_lower.startswith("/say ") or text_lower.startswith("/di "):
            phrase = re.sub(r'^/(say|di)\s+', '', text, flags=re.IGNORECASE).strip()
            if phrase:
                audio_bytes = await get_openai_tts(phrase)
                if audio_bytes:
                    await send_telegram_voice_bytes(chat_id, audio_bytes)
                else:
                    # Fallback a Google TTS
                    voice_url = get_tts_url(phrase, lang)
                    await send_telegram_voice(chat_id, voice_url)
            else:
                await send_telegram_message(chat_id, "❌ Uso: /say [texto a decir]")
            return {"ok": True}
        
        # ============ ORVOZ (IA + VOZ Natural) ============
        if text_lower.startswith("/orvoz "):
            query = text[7:].strip()
            if query:
                await send_telegram_message(chat_id, "🤖🎙️ Procesando con voz natural...")
                response = brain.get_response(query, str(user_id), lang)
                await send_telegram_message(chat_id, response)
                audio_bytes = await get_openai_tts(response)
                if audio_bytes:
                    await send_telegram_voice_bytes(chat_id, audio_bytes)
                else:
                    voice_url = get_tts_url(response[:200], lang)
                    await send_telegram_voice(chat_id, voice_url)
            else:
                await send_telegram_message(chat_id, "❌ Uso: /orvoz [pregunta]")
            return {"ok": True}
        
        # ============ TRADUCIR ============
        if text_lower.startswith("/tr ") or text_lower.startswith("/traducir "):
            match = re.match(r'^/(tr|traducir)\s+(.+?)\s+a\s+(.+)$', text, re.IGNORECASE)
            if match:
                texto = match.group(2).strip()
                idioma = match.group(3).strip()
                prompt = f"Translate this text to {idioma}: \"{texto}\". Return ONLY the translation."
                translation = brain.get_response(prompt, str(user_id), "en")
                await send_telegram_message(chat_id, f"🌐 *{idioma.upper()}:*\n{translation}")
            else:
                await send_telegram_message(chat_id, "❌ Uso: /tr [texto] a [idioma]\nEj: /tr hello a español")
            return {"ok": True}
        
        # ============ ACCESOS DIRECTOS ============
        if text_lower.startswith("/acutor") or text_lower.startswith("/manual"):
            await send_telegram_message(chat_id, "📖 *MANUAL ORION SYSTEM*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/ORION_MANUAL_PROFESIONAL.html\n\n✅ Manual Completo - Guárdalo!")
            return {"ok": True}
        
        if text_lower.startswith("/pb") or text_lower == "pricebook":
            await send_telegram_message(chat_id, "💰 *PRICE BOOK v6.0 PRO*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/pricebook.html\n\n✅ 100 Servicios\n💵 Precios: Estándar/Miembro/Emergencia\n🎯 Sistema Good/Better/Best")
            return {"ok": True}
        
        if text_lower.startswith("/apps") or text_lower == "links":
            await send_telegram_message(chat_id, "🔗 *ORION APPS*\n\n1️⃣ https://ai.studio/apps/drive/1vikKncwaJRxWOANGeEcnchTAM96CqmnZ\n2️⃣ https://ai.studio/apps/drive/1bMGhzGDqLL_aDfnSC78Ie_HnsF7b691I\n3️⃣ https://ai.studio/apps/drive/1BKOJ2-29twcjdG1BooF6-Nh82VpXm6Hi\n\n_Modo App habilitado_")
            return {"ok": True}
        
        if text_lower.startswith("/otp"):
            await send_telegram_message(chat_id, "🤖 *ORION TECH PRODUCTS*\n\n📋 *Industrias:*\n• /restaurant - Restaurantes\n• /salon - Salones\n• /liquor - Licoreras\n• /contractor - Contratistas\n• /retail - Retail\n• /enterprise - Enterprise\n\n🔗 https://agem2024.github.io/SEGURITI-USC/orion-bots.html")
            return {"ok": True}
        
        # ============ INDUSTRIAS ============
        if text_lower.startswith("/restaurant"):
            await send_telegram_message(chat_id, "🍽️ *RESTAURANTES*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/industry-restaurant.html")
            return {"ok": True}
        if text_lower.startswith("/salon"):
            await send_telegram_message(chat_id, "💇 *SALONES DE BELLEZA*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/industry-salon.html")
            return {"ok": True}
        if text_lower.startswith("/liquor"):
            await send_telegram_message(chat_id, "🍷 *LICORERAS*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/industry-liquor.html")
            return {"ok": True}
        if text_lower.startswith("/contractor"):
            await send_telegram_message(chat_id, "🔧 *CONTRATISTAS*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/industry-contractor.html")
            return {"ok": True}
        if text_lower.startswith("/retail"):
            await send_telegram_message(chat_id, "🛒 *RETAIL*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/industry-retail.html")
            return {"ok": True}
        if text_lower.startswith("/enterprise"):
            await send_telegram_message(chat_id, "🏢 *ENTERPRISE*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/industry-enterprise.html")
            return {"ok": True}
        
        # ============ PROFESIONAL (orden importante: cv2 antes de cv) ============
        if text_lower.startswith("/cv2"):
            await send_telegram_message(chat_id, "📄 *CV VERSIÓN 2*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/cv_professional.html\n\n👤 Alex G. Espinosa\n🎯 Versión Profesional Extendida")
            return {"ok": True}
        
        if text_lower.startswith("/cv"):
            await send_telegram_message(chat_id, "📄 *CV PROFESIONAL*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/cv_pro.html\n\n👤 Alex G. Espinosa\n🎯 AI Architect | 21+ años experiencia\n\n_Usa /cv2 para versión extendida_")
            return {"ok": True}
        
        if text_lower.startswith("/tj") or text_lower.startswith("/card"):
            await send_telegram_message(chat_id, "💼 *TARJETA DIGITAL*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/card.html\n\n📱 Contacto profesional digital")
            return {"ok": True}
        
        if text_lower.startswith("/skills"):
            await send_telegram_message(chat_id, "🛠️ *SKILLS TÉCNICAS*\n\n• Python, JavaScript, Node.js\n• AI/ML (Gemini, OpenAI, LangChain)\n• WhatsApp Automation (Baileys)\n• Cloud (Firebase, Render, Vercel)\n• 21+ años ingeniería")
            return {"ok": True}
        
        if text_lower.startswith("/landing"):
            await send_telegram_message(chat_id, "🌐 *LANDING PAGE ORION TECH*\n\n🔗 https://agem2024.github.io/SEGURITI-USC/orion-bots.html\n\n🚀 Servicios de IA y Automatización")
            return {"ok": True}
        
        # ============ CALENDARIO (básico por ahora) ============
        if text_lower.startswith("/cal") or text_lower.startswith("/calendario"):
            await send_telegram_message(chat_id, "📅 *CALENDARIO*\n\n⏰ Función de calendario en desarrollo para cloud.\n\n_El calendario completo está disponible en ORION local (WhatsApp)_")
            return {"ok": True}
        
        # ============ SISTEMA (SOLO OWNER) ============
        if text_lower.startswith("/status") and is_owner:
            await send_telegram_message(chat_id, "🟢 *ORION CLOUD STATUS*\n\n✅ Brain: Online\n✅ Webhook: Active\n✅ API: Running\n✅ TTS: Enabled\n\n🌐 https://orion-cloud.onrender.com")
            return {"ok": True}
        
        if text_lower.startswith("/stats") and is_owner:
            await send_telegram_message(chat_id, "📊 *ESTADÍSTICAS*\n\n🤖 Sistema: XONA v3.0\n☁️ Host: Render\n🧠 IA: Gemini/OpenAI\n🎤 TTS: Google\n\n_Bot 100% Cloud_")
            return {"ok": True}
        
        if text_lower.startswith("/ayuda") or text_lower == "help" or text_lower == "?":
            ayuda = """❓ *AYUDA ORION CLOUD v4*

*📖 Accesos:*
/acutor - Manual ORION
/pb - Price Book
/apps - Orion Apps
/otp - Productos por industria

*🏢 Industrias:*
/restaurant /salon /liquor
/contractor /retail /enterprise

*💼 Profesional:*
/cv - CV Principal
/cv2 - CV Extendido
/tj - Tarjeta Digital
/skills - Skills
/landing - Landing Page

*🎤 Voz & IA:*
/say [texto] - Texto a voz HD
/orvoz [texto] - IA + voz
/tr [texto] a [idioma] - Traducir

*📅 Productividad:*
/cal - Calendario

*🔧 Sistema (Owner):*
/status - Estado
/stats - Estadísticas

_Escribe cualquier pregunta para CHONA_"""
            await send_telegram_message(chat_id, ayuda)
            return {"ok": True}
        
        # ============ XONA RESPONDE A TODO ============
        response = brain.get_response(text, str(user_id), lang)
        await send_telegram_message(chat_id, response)

    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        
    return {"ok": True}

async def send_telegram_message(chat_id: int, text: str):
    """Envía mensaje de texto a Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

async def send_telegram_voice(chat_id: int, voice_url: str):
    """Envía audio/voz a Telegram (URL)"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice"
    payload = {"chat_id": chat_id, "voice": voice_url}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

async def send_telegram_voice_bytes(chat_id: int, audio_bytes: bytes):
    """Envía audio como bytes a Telegram (para OpenAI TTS)"""
    import io
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice"
    files = {"voice": ("audio.mp3", io.BytesIO(audio_bytes), "audio/mpeg")}
    data = {"chat_id": chat_id}
    async with httpx.AsyncClient() as client:
        await client.post(url, data=data, files=files)

# ============ TWILIO VOICE ENDPOINTS ============
from fastapi import Form
from fastapi.responses import Response

# System prompts para voz
VOICE_PROMPT_ES = """Eres CHONA (se escribe XONA), asistente telefónica de ORION Tech.
Hablas español paisa colombiano - cálido y amigable.
Respuestas CORTAS (máx 2 oraciones).
Servicios: Bots WhatsApp, IA para negocios.
Paquetes: Individual $297, Starter $997, Business $1,997, Enterprise $4,997+
Contacto: WhatsApp (669) 234-2444"""

VOICE_PROMPT_EN = """You are XONA, phone assistant for ORION Tech.
California accent - friendly and professional.
SHORT responses (max 2 sentences).
Services: WhatsApp bots, AI for businesses.
Packages: Individual $297, Starter $997, Business $1,997, Enterprise $4,997+
Contact: WhatsApp (669) 234-2444"""

def ask_voice_ai(user_input: str, lang: str = "es") -> str:
    """Get AI response for voice calls"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        system_msg = VOICE_PROMPT_ES if lang == "es" else VOICE_PROMPT_EN
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Voice AI error: {e}")
        return "Sorry, technical issue." if lang == "en" else "Perdona, problema técnico."

@app.get("/voice")
def voice_status():
    return {"status": "ok", "service": "XONA Voice Server", "endpoints": ["/incoming-call", "/incoming-call-en"]}

@app.api_route("/incoming-call", methods=["GET", "POST"])
@app.api_route("/incoming-call-es", methods=["GET", "POST"])
async def incoming_call_es():
    """Handle incoming Spanish call"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud.onrender.com")
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-MX" voice="Polly.Mia">Hola parce, soy CHONA, asistente de ORION Tech. ¿En qué te puedo ayudar?</Say>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="es-MX">No escuché nada. Hasta luego.</Say>
</Response>'''
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/process-speech-es", methods=["GET", "POST"])
async def process_speech_es(SpeechResult: str = Form(None)):
    """Process Spanish speech"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud.onrender.com")
    
    if SpeechResult:
        logger.info(f"🎤 ES: {SpeechResult}")
        
        goodbye = ["adiós", "adios", "bye", "chao", "gracias", "ok gracias"]
        if any(w in SpeechResult.lower() for w in goodbye):
            twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response><Say language="es-MX" voice="Polly.Mia">Fue un placer parce. ¡Hasta luego!</Say></Response>'''
            return Response(content=twiml, media_type="application/xml")
        
        ai_response = ask_voice_ai(SpeechResult, "es")
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-MX" voice="Polly.Mia">{ai_response}</Say>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="es-MX" voice="Polly.Mia">¿Algo más?</Say>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="es-MX">Bueno, hasta luego.</Say>
</Response>'''
    else:
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-MX" voice="Polly.Mia">No te escuché. ¿Puedes repetir?</Say>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto"/>
</Response>'''
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/incoming-call-en", methods=["GET", "POST"])
async def incoming_call_en():
    """Handle incoming English call"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud.onrender.com")
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-US" voice="Polly.Joanna">Hello! I'm XONA, assistant for ORION Tech. How can I help you?</Say>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="en-US">I didn't hear anything. Goodbye.</Say>
</Response>'''
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/process-speech-en", methods=["GET", "POST"])
async def process_speech_en(SpeechResult: str = Form(None)):
    """Process English speech"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud.onrender.com")
    
    if SpeechResult:
        logger.info(f"🎤 EN: {SpeechResult}")
        
        goodbye = ["goodbye", "bye", "thanks", "thank you", "that's all"]
        if any(w in SpeechResult.lower() for w in goodbye):
            twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response><Say language="en-US" voice="Polly.Joanna">It was a pleasure. Goodbye!</Say></Response>'''
            return Response(content=twiml, media_type="application/xml")
        
        ai_response = ask_voice_ai(SpeechResult, "en")
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-US" voice="Polly.Joanna">{ai_response}</Say>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="en-US" voice="Polly.Joanna">Anything else?</Say>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="en-US">Alright, goodbye.</Say>
</Response>'''
    else:
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-US" voice="Polly.Joanna">I didn't hear you. Can you repeat?</Say>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto"/>
</Response>'''
    return Response(content=twiml, media_type="application/xml")
