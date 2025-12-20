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

# ============ URLS ACTUALIZADAS (Clonadas de orion-clean) ============
MANUAL_URL = 'https://agem2024.github.io/SEGURITI-USC/ORION_MANUAL_PROFESIONAL.html'
PRICEBOOK_URL = 'https://agem2024.github.io/SEGURITI-USC/pricebook-index.html'
ORIONBOTS_URL = 'https://agem2024.github.io/SEGURITI-USC/orion-bots.html'
CV_URL = 'https://agem2024.github.io/SEGURITI-USC/cv_pro.html'
CV2_URL = 'https://agem2024.github.io/SEGURITI-USC/cv_professional.html'
CARD_URL = 'https://agem2024.github.io/SEGURITI-USC/card.html'
NEONHUB_URL = 'https://neon-agent-hub.web.app/'

# ORION APPS (Mode App Links)
ORION_APPS = [
    'https://ai.studio/apps/drive/1vikKncwaJRxWOANGeEcnchTAM96CqmnZ?fullscreenApplet=true',
    'https://ai.studio/apps/drive/1bMGhzGDqLL_aDfnSC78Ie_HnsF7b691I?fullscreenApplet=true',
    'https://ai.studio/apps/drive/1BKOJ2-29twcjdG1BooF6-Nh82VpXm6Hi?fullscreenApplet=true',
    'https://ai.studio/apps/drive/1x_ibj0UepSYSNZyv6w83UQCk2GFTjJvG?fullscreenApplet=true',
    'https://ai.studio/apps/drive/1BF2Sl5I48Zh843mnJQAo_mrQLLDUd48J?fullscreenApplet=true',
    'https://ai.studio/apps/drive/1u71t_S_8Cp27aEuUcT0Sffws8tEVQ2pw?fullscreenApplet=true',
    'https://ai.studio/apps/drive/1k_9YBvyIRIWIrSEZuIzoHRSH5Qauhpd_?fullscreenApplet=true',
    'https://ai.studio/apps/drive/1NNlIz45X8Pr8waX5P5p90CHzJ5uJv2WN?fullscreenApplet=true'
]

# INDUSTRY PAGES
INDUSTRY_URLS = {
    'restaurant': 'https://agem2024.github.io/SEGURITI-USC/industry-restaurant.html',
    'salon': 'https://agem2024.github.io/SEGURITI-USC/industry-salon.html',
    'liquor': 'https://agem2024.github.io/SEGURITI-USC/industry-liquor.html',
    'contractor': 'https://agem2024.github.io/SEGURITI-USC/industry-contractor.html',
    'retail': 'https://agem2024.github.io/SEGURITI-USC/industry-retail.html',
    'enterprise': 'https://agem2024.github.io/SEGURITI-USC/industry-enterprise.html',
}

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
    return {"status": "ok", "system": "ORION CLOUD v4 - Full Commands (Synced with orion-clean)"}

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

# ============ REALTIME API TOKEN ============
@app.post("/api/realtime-token")
async def realtime_token(request: Request):
    """Genera token efímero para OpenAI Realtime API WebRTC"""
    try:
        data = await request.json() if request.headers.get("content-type") == "application/json" else {}
        config = data.get("config", {})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/realtime/sessions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.get("model", "gpt-4o-realtime-preview"),
                    "voice": config.get("voice", "shimmer"),
                    "instructions": config.get("instructions", """Eres XONA (pronunciado "CHO-nah"), asistente de ventas AI de ORION Tech.
Hablas español paisa colombiano - cálido, amigable, profesional.
Respuestas CORTAS (máximo 2 oraciones).
Servicios: Bots WhatsApp con IA, automatización para negocios.
Precios: Individual $297-$497, Salones $997, Restaurantes $1,497, Enterprise $4,997+
Contacto: WhatsApp (669) 234-2444""")
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Realtime token error: {response.text}")
                return {"error": "Failed to generate token"}
            
            token_data = response.json()
            logger.info("🎤 Realtime token generated")
            return token_data
            
    except Exception as e:
        logger.error(f"Realtime token error: {e}")
        return {"error": str(e)}

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
                menu = """🚀 *ORION CLOUD v4 ONLINE*
👑 Owner Mode: ACTIVADO

*📖 COMANDOS DISPONIBLES:*

*🔗 Accesos:*
/acutor - Manual ORION
/pb - Price Book v6.0 PRO
/apps - Orion Apps (8 links)
/otp - Landing Orion Bots

*💼 Profesional:*
/cv - CV Principal
/cv2 - CV Profesional Extendido
/tj - Tarjeta Digital
/skills - Skills técnicas
/landing - Neon Hub

*🏢 Industrias:*
/restaurant - Restaurantes
/salon - Salones de Belleza  
/liquor - Licoreras
/contractor - Contratistas
/retail - Retail
/enterprise - Enterprise

*🎤 Voz & IA:*
/say [texto] - Texto a voz HD
/orvoz [texto] - IA + voz
/tr [texto] a [idioma] - Traducir

*🔧 Sistema:*
/status - Estado sistema
/stats - Estadísticas
/ayuda - Ver comandos

_Escribe cualquier cosa para hablar con XONA_"""
                await send_telegram_message(chat_id, menu)
            else:
                await send_telegram_message(chat_id, "👋 *¡Hola! Soy XONA*, asistente de ORION Tech.\n\n¿En qué puedo ayudarte?\n\n📱 WhatsApp: (669) 234-2444\n🌐 Servicios de IA y Automatización")
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
        
        # ============ ACCESOS DIRECTOS (Actualizados) ============
        if text_lower.startswith("/acutor") or text_lower.startswith("/manual"):
            await send_telegram_message(chat_id, f"📖 *MANUAL ORION SYSTEM*\n\n🔗 {MANUAL_URL}\n\n✅ Manual Completo - Guárdalo!")
            return {"ok": True}
        
        if text_lower.startswith("/pb") or text_lower == "pricebook":
            await send_telegram_message(chat_id, f"💰 *PRICE BOOK v6.0 PRO*\n\n🔗 {PRICEBOOK_URL}\n\n✅ 100+ Servicios\n💵 Precios: Estándar/Miembro/Emergencia\n🎯 Sistema Good/Better/Best\n📐 Metodología de Cálculo")
            return {"ok": True}
        
        if text_lower.startswith("/apps") or text_lower == "links":
            msg = "🔗 *ORION APPS (Modo App)*\n\n"
            for i, link in enumerate(ORION_APPS, 1):
                msg += f"*App {i}:*\n{link}\n\n"
            await send_telegram_message(chat_id, msg)
            return {"ok": True}
        
        if text_lower.startswith("/otp"):
            await send_telegram_message(chat_id, f"🤖 *ORION TECH PRODUCTS*\n\n📋 *Industrias:*\n• /restaurant - Restaurantes\n• /salon - Salones\n• /liquor - Licoreras\n• /contractor - Contratistas\n• /retail - Retail\n• /enterprise - Enterprise\n\n🔗 {ORIONBOTS_URL}")
            return {"ok": True}
        
        # ============ INDUSTRIAS ============
        if text_lower.startswith("/restaurant"):
            await send_telegram_message(chat_id, f"🍽️ *RESTAURANTES*\n\n🔗 {INDUSTRY_URLS['restaurant']}")
            return {"ok": True}
        if text_lower.startswith("/salon"):
            await send_telegram_message(chat_id, f"💇 *SALONES DE BELLEZA*\n\n🔗 {INDUSTRY_URLS['salon']}")
            return {"ok": True}
        if text_lower.startswith("/liquor"):
            await send_telegram_message(chat_id, f"🍷 *LICORERAS*\n\n🔗 {INDUSTRY_URLS['liquor']}")
            return {"ok": True}
        if text_lower.startswith("/contractor"):
            await send_telegram_message(chat_id, f"🔧 *CONTRATISTAS*\n\n🔗 {INDUSTRY_URLS['contractor']}")
            return {"ok": True}
        if text_lower.startswith("/retail"):
            await send_telegram_message(chat_id, f"🛒 *RETAIL*\n\n🔗 {INDUSTRY_URLS['retail']}")
            return {"ok": True}
        if text_lower.startswith("/enterprise"):
            await send_telegram_message(chat_id, f"🏢 *ENTERPRISE*\n\n🔗 {INDUSTRY_URLS['enterprise']}")
            return {"ok": True}
        
        # ============ PROFESIONAL (CV, TJ, Skills) ============
        if text_lower.startswith("/cv2"):
            await send_telegram_message(chat_id, f"📄 *CV VERSIÓN 2 (Profesional)*\n\n✨ Formato ATS-friendly con logros\n📊 21+ años experiencia\n🔗 {CV2_URL}")
            return {"ok": True}
        
        if text_lower.startswith("/cv"):
            await send_telegram_message(chat_id, f"📄 *CV PROFESIONAL*\n\n🔗 {CV_URL}\n\n👤 Alex G. Espinosa\n🎯 AI Architect | 21+ años experiencia\n\n_Usa /cv2 para versión extendida_")
            return {"ok": True}
        
        if text_lower.startswith("/tj") or text_lower.startswith("/card"):
            await send_telegram_message(chat_id, f"💼 *TARJETA DIGITAL*\n\n🔗 {CARD_URL}\n\n📱 Contacto profesional digital")
            return {"ok": True}
        
        if text_lower.startswith("/skills"):
            await send_telegram_message(chat_id, """🛠️ *SKILLS TÉCNICAS*

🤖 *AI & DEV:*
• Multi-Agent Systems (Orion)
• Generative AI (Gemini, GPT-4, Claude)
• Node.js, Python, WhatsApp Automation

🏗️ *INGENIERÍA:*
• Diseño Hidráulico & Sanitario
• Estimación de Costos & Presupuestos
• Auditoría ISO 14001

💼 *MANAGEMENT:*
• Liderazgo de Equipos
• Gestión de Proyectos Complejos
• Consultoría Estratégica""")
            return {"ok": True}
        
        if text_lower.startswith("/landing"):
            await send_telegram_message(chat_id, f"🌐 *NEON AGENT HUB*\n\nAcceso global a tus agentes:\n🔗 {NEONHUB_URL}")
            return {"ok": True}
        
        # ============ SISTEMA (SOLO OWNER) ============
        if text_lower.startswith("/status") and is_owner:
            await send_telegram_message(chat_id, "🟢 *ORION CLOUD STATUS*\n\n✅ Brain: Online\n✅ Webhook: Active\n✅ API: Running\n✅ TTS: Enabled\n\n🌐 https://orion-cloud.onrender.com")
            return {"ok": True}
        
        if text_lower.startswith("/stats") and is_owner:
            await send_telegram_message(chat_id, "📊 *ESTADÍSTICAS*\n\n🤖 Sistema: XONA v4.0\n☁️ Host: Render\n🧠 IA: OpenAI/Gemini\n🎤 TTS: OpenAI HD\n\n_Bot 100% Cloud_")
            return {"ok": True}
        
        if text_lower.startswith("/ayuda") or text_lower == "help" or text_lower == "?":
            ayuda = """❓ *AYUDA ORION CLOUD v4*

*📖 Accesos:*
/acutor - Manual ORION
/pb - Price Book v6.0 PRO
/apps - Orion Apps (8 links)
/otp - Productos por industria

*🏢 Industrias:*
/restaurant /salon /liquor
/contractor /retail /enterprise

*💼 Profesional:*
/cv - CV Principal
/cv2 - CV Extendido
/tj - Tarjeta Digital
/skills - Skills
/landing - Neon Hub

*🎤 Voz & IA:*
/say [texto] - Texto a voz HD
/orvoz [texto] - IA + voz
/tr [texto] a [idioma] - Traducir

*🔧 Sistema (Owner):*
/status - Estado
/stats - Estadísticas

_Escribe cualquier pregunta para XONA_"""
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
VOICE_PROMPT_ES = """Eres XONA (se escribe XONA pero se pronuncia CHONA), asistente telefónica de ORION Tech.
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
    return {"status": "ok", "service": "XONA Voice Server", "endpoints": ["/incoming-call", "/incoming-call-en", "/incoming-call-es"]}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def incoming_call_menu():
    """Handle incoming call with language menu"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud.onrender.com")
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="{base_url}/select-language" method="POST" timeout="5">
        <Say language="en-US" voice="Polly.Joanna">Welcome to ORION Tech. Press 1 for English.</Say>
        <Say language="es-MX" voice="Polly.Mia">Bienvenido a ORION Tech. Presione 2 para español.</Say>
    </Gather>
    <Say language="en-US">We didn't receive a response. Goodbye.</Say>
    <Say language="es-MX">No recibimos respuesta. Hasta luego.</Say>
</Response>'''
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/select-language", methods=["GET", "POST"])
async def select_language(Digits: str = Form(None)):
    """Route to correct language based on selection"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud.onrender.com")
    
    if Digits == "1":
        # English selected
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-US" voice="Polly.Joanna">Hello! I'm XONA, assistant for ORION Tech. How can I help you?</Say>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="en-US">I didn't hear anything. Goodbye.</Say>
</Response>'''
    elif Digits == "2":
        # Spanish selected
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-MX" voice="Polly.Mia">¡Hola parce! Soy XONA, asistente de ORION Tech. ¿En qué te puedo ayudar?</Say>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="es-MX">No escuché nada. Hasta luego.</Say>
</Response>'''
    else:
        # Invalid option, retry
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-US">Invalid option.</Say>
    <Say language="es-MX">Opción inválida.</Say>
    <Redirect>{base_url}/incoming-call</Redirect>
</Response>'''
    
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/incoming-call-es", methods=["GET", "POST"])
async def incoming_call_es():
    """Handle incoming Spanish call (direct)"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud.onrender.com")
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-MX" voice="Polly.Mia">Hola parce, soy XONA, asistente de ORION Tech. ¿En qué te puedo ayudar?</Say>
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
