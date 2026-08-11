import os
import logging
import httpx
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from brain import OrionBrain
from urllib.parse import quote

# Configuración

# Configuración
app = FastAPI()

# ============ MEMORIA DE SESIÓN ============
# Diccionario temporal para guardar el historial de la conversación por CallSid
# En producción, esto debería ir a Redis o DB.
call_sessions = {}


# CORS para permitir peticiones desde la web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Morales Plumbing_CLOUD")

# Variables de Entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID = 5989183300  # Alex - puede usar comandos especiales
BASE_URL = os.getenv("BASE_URL")

# Inicializar Cerebro
brain = OrionBrain()

# ============ URLS ACTUALIZADAS (Clonadas de orion-clean) ============
MANUAL_URL = 'https://agem2024.github.io/SEGURITI-USC/Morales Plumbing_MANUAL_PROFESIONAL.html'
PRICEBOOK_URL = 'https://agem2024.github.io/SEGURITI-USC/pricebook-index.html'
MORALES_PLUMBING_BOTS_URL = 'https://agem2024.github.io/Morales_Plumbing/'
CV_URL = 'https://agem2024.github.io/SEGURITI-USC/cv_pro.html'
CV2_URL = 'https://agem2024.github.io/SEGURITI-USC/cv_professional.html'
CARD_URL = 'https://agem2024.github.io/SEGURITI-USC/card.html'
NEONHUB_URL = 'https://neon-agent-hub.web.app/'

# Morales Plumbing APPS (Mode App Links)
MORALES_PLUMBING_APPS = [
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

async def get_openai_tts(text: str, lang: str = "es") -> bytes:
    """Genera audio con OpenAI TTS HD - Voz masculina natural"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Voces masculinas: onyx (California cool), echo (elegante)
        voice = "onyx" if lang == "en" else "echo"  # onyx=California, echo=elegante paisa
        response = client.audio.speech.create(
            model="tts-1-hd",  # HD = Alta definición, más natural
            voice=voice,
            input=text[:4096],
            speed=1.0
        )
        return response.content
    except Exception as e:
        logger.error(f"OpenAI TTS error: {e}")
        return None

@app.get("/")
def health():
    return {"status": "ok", "system": "Morales Plumbing CLOUD v4 - Full Commands (Synced with orion-clean)"}

# ============ TTS API FOR WEB ============
@app.post("/api/tts")
async def api_tts(request: Request):
    """TTS endpoint for web chatbot - works on all devices"""
    from fastapi.responses import Response
    try:
        data = await request.json()
        text = data.get("text", "")
        lang = data.get("lang", "es")
        
        if not text:
            return Response(content=b"", media_type="audio/mpeg")
        
        # Use OpenAI TTS
        audio_bytes = await get_openai_tts(text)
        if audio_bytes:
            # Add proper headers to avoid Range request errors
            headers = {
                "Content-Length": str(len(audio_bytes)),
                "Accept-Ranges": "none",  # Disable range requests
                "Cache-Control": "no-cache"
            }
            return Response(content=audio_bytes, media_type="audio/mpeg", headers=headers)
        else:
            # Fallback: return empty audio
            return Response(content=b"", media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"TTS API error: {e}")
        return Response(content=b"", media_type="audio/mpeg")

# ============ WEB CHAT API ============
@app.post("/api/chat")
async def web_chat(request: Request):
    """Endpoint para el chatbot web XONA"""
    try:
        data = await request.json()
        message = data.get("message", "")
        lang = data.get("lang", "es")  # Default: español
        
        if not message:
            error_msg = "Por favor envía un mensaje." if lang == "es" else "Please send a message."
            return {"response": error_msg, "error": True}
        
        response = brain.get_response(message, "web_user", lang)
        return {"response": response, "error": False}
    except Exception as e:
        logger.error(f"Web chat error: {e}")
        error_msg = "Error procesando la solicitud." if lang == "es" else "Error processing request."
        return {"response": error_msg, "error": True}

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
            menu = """🚀 *Morales Plumbing CLOUD v4 ONLINE*

*📖 COMANDOS DISPONIBLES:*

*🔗 Accesos:*
/acutor - Manual Morales Plumbing
/pb - Price Book v6.0 PRO
/ld - Generador Legal (Morales Plumbing)
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

_Escribe cualquier cosa para hablar con Nekon_"""
            await send_telegram_message(chat_id, menu)
            return {"ok": True}
        
        # ============ VOZ TTS (OpenAI Natural) ============
        if text_lower.startswith("/say ") or text_lower.startswith("/di "):
            phrase = re.sub(r'^/(say|di)\s+', '', text, flags=re.IGNORECASE).strip()
            if phrase:
                audio_bytes = await get_openai_tts(phrase, lang)
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
                audio_bytes = await get_openai_tts(response, lang)
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
            await send_telegram_message(chat_id, f"📖 *MANUAL Morales Plumbing SYSTEM*\n\n🔗 {MANUAL_URL}\n\n✅ Manual Completo - Guárdalo!")
            return {"ok": True}
        
        if text_lower.startswith("/pb") or text_lower == "pricebook":
            await send_telegram_message(chat_id, f"💰 *PRICE BOOK v6.0 PRO*\n\n🔗 {PRICEBOOK_URL}\n\n✅ 100+ Servicios\n💵 Precios: Estándar/Miembro/Emergencia\n🎯 Sistema Good/Better/Best\n📐 Metodología de Cálculo")
            return {"ok": True}
            
        if text_lower.startswith("/ld") or text_lower.startswith("/legaldocs") or text_lower.startswith("/contrato") or text_lower.startswith("/factura"):
            msg_ld = f"""⚖️ *MORALES PLUMBING - GENERADOR LEGAL & CONTRATOS*

Plataforma oficial para generar, firmar y consultar contratos, facturas, recibos y órdenes de trabajo.

🌐 *Enlace Directo:* https://morales-plumbing-web.web.app/

📌 *Licencia CSLB:* C-36 #1156542 | San Jose, CA
📞 *Teléfono:* (669) 213-4422
📧 *Email:* moralesplumbing026@gmail.com

💡 *Para abrir un documento guardado:* Usa el formato:
`https://morales-plumbing-web.web.app/?docId=ID_DEL_DOC`"""
            await send_telegram_message(chat_id, msg_ld)
            return {"ok": True}
        
        if text_lower.startswith("/apps") or text_lower == "links":
            msg = "🔗 *Morales Plumbing APPS (Modo App)*\n\n"
            for i, link in enumerate(MORALES_PLUMBING_APPS, 1):
                msg += f"*App {i}:*\n{link}\n\n"
            await send_telegram_message(chat_id, msg)
            return {"ok": True}
        
        if text_lower.startswith("/otp"):
            await send_telegram_message(chat_id, f"🤖 *MORALES PLUMBING PRODUCTS*\n\n📋 *Industrias:*\n• /restaurant - Restaurantes\n• /salon - Salones\n• /liquor - Licoreras\n• /contractor - Contratistas\n• /retail - Retail\n• /enterprise - Enterprise\n\n🔗 {MORALES_PLUMBING_BOTS_URL}")
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
        if text_lower == "/mp" or text_lower == "mp":
            # Enviamos texto con el link de la tarjeta digital usando HTML parse_mode para evitar errores de Markdown
            mp_text = """🔧 <b>MORALES PLUMBING</b>
AI-INTEGRATED SERVICES

Lic. C-36 #1156542 | San Jose, CA
📱 (669) 213-4422
📧 moralesplumbing026@gmail.com
🌐 www.moralesplumbing.com

🪪 <b>Tarjeta Digital:</b>
<a href="https://agem2024.github.io/morales-plumbing-web/tarjeta_presentacion.html">Click aquí para abrir la tarjeta digital</a>"""
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": mp_text, "parse_mode": "HTML"}
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload)
            return {"ok": True}
            
        if text_lower == "/r1" or text_lower == "r1":
            # Enviamos 4 mensajes separados para que Telegram genere la miniatura de cada link
            mensajes_r1 = [
                "📄 *Propuestas - 538 Leigh Ave*\n\n1️⃣ *Reparación:*\nhttps://agem2024.github.io/SEGURITI-USC/docs/proposals/propuesta_reparacion_538_leigh.html",
                "2️⃣ *Opción B:*\nhttps://agem2024.github.io/SEGURITI-USC/docs/proposals/propuesta_opcion_b_538_leigh.html",
                "3️⃣ *ADU Tankless:*\nhttps://agem2024.github.io/SEGURITI-USC/docs/proposals/propuesta_adu_tankless_rodrigo.html",
                "⚖️ *Términos Legales:*\nhttps://agem2024.github.io/SEGURITI-USC/docs/proposals/propuesta_lega_538_leigh.html"
            ]
            
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            async with httpx.AsyncClient() as client:
                for msg in mensajes_r1:
                    # Usamos text plano sin parse_mode para evitar error por guiones bajos
                    payload = {"chat_id": chat_id, "text": msg}
                    await client.post(url, json=payload)
                    
            return {"ok": True}
            
        if text_lower == "/j1" or text_lower == "j1":
            mensajes_j1 = [
                "📄 *Propuestas - Joan Wrabetz*\n\n1️⃣ *Instalación Lavabo Doble:*\nhttps://agem2024.github.io/SEGURITI-USC/docs/proposals/lavy_installation_proposal.html?v=2",
                "2️⃣ *Actualización Tankless:*\nhttps://agem2024.github.io/SEGURITI-USC/docs/proposals/water_heater_update_o_replace.html?v=2"
            ]
            
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            async with httpx.AsyncClient() as client:
                for msg in mensajes_j1:
                    payload = {"chat_id": chat_id, "text": msg}
                    await client.post(url, json=payload)
                    
            return {"ok": True}

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
            await send_telegram_message(chat_id, "🟢 *Morales Plumbing CLOUD STATUS*\n\n✅ Brain: Online\n✅ Webhook: Active\n✅ API: Running\n✅ TTS: Enabled\n\n🌐 https://orion-cloud-1.onrender.com")
            return {"ok": True}
        
        if text_lower.startswith("/stats") and is_owner:
            await send_telegram_message(chat_id, "📊 *ESTADÍSTICAS*\n\n🤖 Sistema: XONA v4.0\n☁️ Host: Render\n🧠 IA: OpenAI/Gemini\n🎤 TTS: OpenAI HD\n\n_Bot 100% Cloud_")
            return {"ok": True}
        
        if text_lower.startswith("/ayuda") or text_lower == "help" or text_lower == "?":
            ayuda = """❓ *AYUDA Morales Plumbing CLOUD v4*

*📖 Accesos:*
/acutor - Manual Morales Plumbing
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

# System prompts para voz - Nekon femenino profesional CON AGENDAMIENTO
VOICE_PROMPT_ES = """Eres Nekon, asistente telefónica ejecutiva (Dispatcher) de Morales Plumbing.
Voz femenina profesional, paciente y amable. Respondes en MÁXIMO 2 oraciones cortas.
Servicios: Plomería profesional residencial y comercial. Horario 24/7.
Regla 1: NO des precios por teléfono bajo ninguna circunstancia.
Regla 2: Para agendar una cita o mandar a un técnico, NECESITAS OBLIGATORIAMENTE 6 DATOS:
1. Nombre
2. Teléfono
3. Email (Pide al cliente que lo deletree si no se entiende bien)
4. Dirección del servicio
5. Estatus (Si es dueño de la propiedad o si renta)
6. Diagnóstico / Problema de plomería

NO CONFIRMES LA CITA SI FALTAN DATOS. Pregunta uno por uno de manera natural y conversacional.
Cuando tengas los 6 datos, responde: "Perfecto, he agendado su cita. Le confirmaremos los detalles y enviaremos al técnico."
"""

VOICE_PROMPT_EN = """You are Nekon, executive phone dispatcher for Morales Plumbing.
Professional female voice, patient and friendly. Respond in MAX 2 short sentences.
Services: Professional residential and commercial plumbing. Available 24/7.
Rule 1: DO NOT give prices over the phone under any circumstances.
Rule 2: To schedule an appointment or dispatch a tech, you STRICTLY NEED 6 FIELDS:
1. Name
2. Phone
3. Email (Ask the client to spell it out if unclear)
4. Service Address
5. Status (Homeowner or Renter)
6. Diagnosis / Plumbing problem

DO NOT CONFIRM THE APPOINTMENT IF ANY DATA IS MISSING. Ask for them one by one naturally.
When you have all 6, say: "Perfect, I've scheduled your appointment. We'll confirm the details and send the tech."
"""

# Archivo compartido de citas (accesible por todos los bots)
APPOINTMENTS_FILE = "/tmp/orion_appointments.json"

def save_appointment(name: str, phone: str, email: str, address: str, status: str, diagnosis: str, materials: str, source: str = "phone") -> str:
    """Guarda cita en archivo JSON compartido y retorna código MP-XXXX"""
    import json
    import random
    from datetime import datetime
    import requests
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        appointments = []
        if os.path.exists(APPOINTMENTS_FILE):
            with open(APPOINTMENTS_FILE, 'r') as f:
                appointments = json.load(f)
        
        # Generar código de confirmación MP-XXXX
        code = f"MP-{random.randint(1000, 9999)}"
        
        appointment = {
            "id": len(appointments) + 1,
            "code": code,
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "status": status,
            "diagnosis": diagnosis,
            "materials": materials,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "confirmed": False
        }
        appointments.append(appointment)
        
        with open(APPOINTMENTS_FILE, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        logger.info(f"📅 Cita guardada: {name} - {phone} - {time_slot} (Código: {code})")

        # Notificar por Telegram
        try:
            tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
            tg_chat = os.getenv("TELEGRAM_OWNER_ID")
            if tg_token and tg_chat:
                msg = f"NUEVA CITA (DISPATCHER)\n\nID: {code}\nNombre: {name}\nTeléfono: {phone}\nEmail: {email}\nDirección: {address}\nEstatus: {status}\n\nProblema: {diagnosis}\nMateriales Recomendados: {materials}"
                requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", data={"chat_id": tg_chat, "text": msg})
        except Exception as e:
            logger.error(f"Error enviando Telegram: {e}")

        # Notificar por Email
        try:
            email_user = os.getenv("EMAIL_USER")
            email_pass = os.getenv("EMAIL_PASS")
            if email_user and email_pass:
                msg = MIMEMultipart()
                msg['From'] = email_user
                msg['To'] = email_user
                msg['Subject'] = f"Nueva Cita - {name} ({code})"
                
                body = f"NUEVA CITA AGENDADA POR DISPATCHER TELEFÓNICO\n\nID: {code}\nNombre: {name}\nTeléfono: {phone}\nEmail: {email}\nDirección: {address}\nEstatus: {status}\n\nDiagnóstico: {diagnosis}\nMateriales Mínimos Sugeridos: {materials}\nOrigen: {source}"
                msg.attach(MIMEText(body, 'plain'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email_user, email_pass)
                text = msg.as_string()
                server.sendmail(email_user, email_user, text)
                server.quit()
        except Exception as e:
            logger.error(f"Error enviando Email: {e}")

        return code
    except Exception as e:
        logger.error(f"Error guardando cita: {e}")
        return ""

def extract_appointment_info(call_history: list, lang: str = "es") -> dict:
    """Usa IA para extraer info de cita usando TODO el historial"""
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in call_history if msg['role'] != 'system'])
    
    prompt = f"""Extract appointment and dispatcher info from this conversation history.
Return JSON only:
{{
  "name": "client name or null",
  "phone": "phone number or null",
  "email": "email address or null",
  "address": "service address or null",
  "status": "owner/renter/null",
  "diagnosis": "brief description of problem or null",
  "materials": "list of minimum recommended tools/materials for this job based on diagnosis, or null",
  "is_complete": true/false (true ONLY if name, phone, email, address, status, and diagnosis are ALL present)
}}

Conversation History:
{history_text}

JSON:"""

    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        
        import json
        raw_json = response.choices[0].message.content.strip()
        if raw_json.startswith('```json'):
            raw_json = raw_json[7:]
        if raw_json.startswith('```'):
            raw_json = raw_json[3:]
        if raw_json.endswith('```'):
            raw_json = raw_json[:-3]
        result = json.loads(raw_json.strip())
        return result
    except Exception as e:
        logger.error(f"Voice AI OpenAI extract error: {e}")
        try:
            if hasattr(brain, 'gemini_client') and brain.gemini_client:
                gemini_response = brain.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                import json
                
                # Clean up Gemini response in case it returns markdown blocks
                raw_json = gemini_response.text.strip()
                if raw_json.startswith('```json'):
                    raw_json = raw_json[7:]
                if raw_json.startswith('```'):
                    raw_json = raw_json[3:]
                if raw_json.endswith('```'):
                    raw_json = raw_json[:-3]
                    
                result = json.loads(raw_json.strip())
                return result
        except Exception as gemini_e:
            logger.error(f"Voice AI Gemini extract error: {gemini_e}")
        return {"is_complete": False}

def ask_voice_ai(user_input: str, call_sid: str, lang: str = "es") -> str:
    """Get AI response for voice calls - with conversation memory and extraction"""
    system_msg = VOICE_PROMPT_ES if lang == "es" else VOICE_PROMPT_EN
    
    # Iniciar historial de sesión si no existe
    if call_sid not in call_sessions:
        call_sessions[call_sid] = [{"role": "system", "content": system_msg}]
        
    # Añadir input del usuario al historial
    call_sessions[call_sid].append({"role": "user", "content": user_input})
    
    # Extraer info usando TODO el historial
    appointment_info = extract_appointment_info(call_sessions[call_sid], lang)
    
    if appointment_info.get("is_complete"):
        code = save_appointment(
            name=appointment_info.get("name", "Cliente"),
            phone=appointment_info.get("phone", "No provisto"),
            email=appointment_info.get("email", "No provisto"),
            address=appointment_info.get("address", "No provisto"),
            status=appointment_info.get("status", "No provisto"),
            diagnosis=appointment_info.get("diagnosis", "Inspección General"),
            materials=appointment_info.get("materials", "Kit básico"),
            source="phone_call"
        )
        
        # Limpiar sesión para evitar doble guardado
        del call_sessions[call_sid]
        
        if lang == "es":
            return f"Perfecto, he agendado su cita con código {code}. Enviaremos a nuestro técnico de inmediato."
        else:
            return f"Perfect, I've scheduled your appointment with code {code}. We will send our technician right away."
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=call_sessions[call_sid],
            max_tokens=150
        )
        ai_response = response.choices[0].message.content.strip()
        
        # Guardar respuesta de la IA en el historial
        call_sessions[call_sid].append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        logger.error(f"Voice AI OpenAI error: {e}")
        try:
            if hasattr(brain, 'gemini_client') and brain.gemini_client:
                full_prompt = f"{system_msg}\n\nUSER MESSAGE: {user_input}"
                gemini_response = brain.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt
                )
                return gemini_response.text.strip()
        except Exception as gemini_e:
            logger.error(f"Voice AI Gemini error: {gemini_e}")
        return "Sorry, technical issue." if lang == "en" else "Perdona, problema técnico."

# API endpoint para ver citas (accesible por otros bots)
@app.get("/api/appointments")
def get_appointments():
    """Endpoint para que otros bots lean las citas"""
    import json
    try:
        if os.path.exists(APPOINTMENTS_FILE):
            with open(APPOINTMENTS_FILE, 'r') as f:
                return {"appointments": json.load(f)}
        return {"appointments": []}
    except:
        return {"appointments": [], "error": "Could not read appointments"}


@app.get("/voice")
def voice_status():
    return {"status": "ok", "service": "Alex Voice Server", "endpoints": ["/incoming-call", "/incoming-call-en", "/incoming-call-es"]}

# ============ TTS CACHE & SERVE ============
def get_cached_tts_url(text: str, lang: str, base_url: str) -> str:
    import hashlib
    import os
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    filename = f"{lang}_{text_hash}.mp3"
    audio_dir = "/tmp/audio"
    os.makedirs(audio_dir, exist_ok=True)
    filepath = os.path.join(audio_dir, filename)
    
    if not os.path.exists(filepath):
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            voice = "nova" if lang == "es" else "shimmer"
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text[:4096],
                speed=1.0
            )
            response.stream_to_file(filepath)
        except Exception as e:
            logger.error(f"OpenAI TTS file error: {e}")
            return ""
            
    return f"{base_url}/audio/{filename}"

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    from fastapi.responses import FileResponse, Response
    import os
    filepath = f"/tmp/audio/{filename}"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="audio/mpeg")
    return Response(status_code=404)

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def incoming_call_menu():
    """Handle incoming call with language menu"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud-1.onrender.com")
    msg_en1 = get_cached_tts_url("Welcome to Morales Plumbing. Press 1 for English.", "en", base_url)
    msg_es1 = get_cached_tts_url("Bienvenido a Morales Plumbing. Presione 2 para español.", "es", base_url)
    msg_en2 = get_cached_tts_url("We didn't receive a response. Goodbye.", "en", base_url)
    msg_es2 = get_cached_tts_url("No recibimos respuesta. Hasta luego.", "es", base_url)
    
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="{base_url}/select-language" method="POST" timeout="5">
        <Play>{msg_en1}</Play>
        <Play>{msg_es1}</Play>
    </Gather>
    <Play>{msg_en2}</Play>
    <Play>{msg_es2}</Play>
</Response>'''
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/select-language", methods=["GET", "POST"])
async def select_language(Digits: str = Form(None)):
    """Route to correct language based on selection"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud-1.onrender.com")
    
    if Digits == "1":
        # English selected
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-US" voice="Polly.Joanna">Hello! I'm Nekon, assistant for Morales Plumbing. How can I help you?</Say>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="en-US" voice="Polly.Joanna">I didn't hear anything. Goodbye.</Say>
</Response>'''
    elif Digits == "2":
        # Spanish selected
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-MX" voice="Polly.Mia">¡Hola! Soy Nekon, asistente de Morales Plumbing. ¿En qué le puedo ayudar?</Say>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto"/>
    <Say language="es-MX" voice="Polly.Mia">No escuché nada. Hasta luego.</Say>
</Response>'''
    else:
        # Invalid option, retry
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-US" voice="Polly.Joanna">Invalid option.</Say>
    <Say language="es-MX" voice="Polly.Mia">Opción inválida.</Say>
    <Redirect>{base_url}/incoming-call</Redirect>
</Response>'''
    
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/incoming-call-es", methods=["GET", "POST"])
async def incoming_call_es():
    """Handle incoming Spanish call (direct)"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud-1.onrender.com")
    msg1 = get_cached_tts_url("¡Hola! Soy Nekon, asistente de Morales Plumbing. ¿En qué le puedo ayudar?", "es", base_url)
    msg2 = get_cached_tts_url("No escuché nada. Hasta luego.", "es", base_url)
    
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto">
        <Play>{msg1}</Play>
    </Gather>
    <Play>{msg2}</Play>
</Response>'''
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/process-speech-es", methods=["GET", "POST"])
async def process_speech_es(SpeechResult: str = Form(None), CallSid: str = Form("NO_SID")):
    """Process Spanish speech"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud-1.onrender.com")
    
    if SpeechResult:
        logger.info(f"🎤 ES: {SpeechResult}")
        
        goodbye = ["adiós", "adios", "bye", "chao", "gracias", "ok gracias"]
        if any(w in SpeechResult.lower() for w in goodbye):
            msg = get_cached_tts_url("Fue un placer. ¡Hasta luego!", "es", base_url)
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response><Play>{msg}</Play></Response>'''
            return Response(content=twiml, media_type="application/xml")
        
        ai_response = ask_voice_ai(SpeechResult, CallSid, "es")
        audio_url = get_cached_tts_url(ai_response, "es", base_url)
        play_ai = f"<Play>{audio_url}</Play>" if audio_url else f'<Say language="es-MX" voice="Polly.Mia">{ai_response}</Say>'
        play_more = f"<Play>{get_cached_tts_url('¿Algo más?', 'es', base_url)}</Play>"
        play_bye = f"<Play>{get_cached_tts_url('Bueno, hasta luego.', 'es', base_url)}</Play>"
        
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto">
        {play_ai}
    </Gather>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto">
        {play_more}
    </Gather>
    {play_bye}
</Response>'''
    else:
        msg = get_cached_tts_url("No le escuché. ¿Puede repetir?", "es", base_url)
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" language="es-MX" action="{base_url}/process-speech-es" method="POST" timeout="5" speechTimeout="auto">
        <Play>{msg}</Play>
    </Gather>
</Response>'''
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/incoming-call-en", methods=["GET", "POST"])
async def incoming_call_en():
    """Handle incoming English call"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud-1.onrender.com")
    msg1 = get_cached_tts_url("Hello! I'm Nekon, assistant for Morales Plumbing. How can I help you?", "en", base_url)
    msg2 = get_cached_tts_url("I didn't hear anything. Goodbye.", "en", base_url)
    
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto">
        <Play>{msg1}</Play>
    </Gather>
    <Play>{msg2}</Play>
</Response>'''
    return Response(content=twiml, media_type="application/xml")

@app.api_route("/process-speech-en", methods=["GET", "POST"])
async def process_speech_en(SpeechResult: str = Form(None), CallSid: str = Form("NO_SID")):
    """Process English speech"""
    base_url = os.getenv("BASE_URL", "https://orion-cloud-1.onrender.com")
    
    if SpeechResult:
        logger.info(f"🎤 EN: {SpeechResult}")
        
        goodbye = ["goodbye", "bye", "thanks", "thank you", "that's all"]
        if any(w in SpeechResult.lower() for w in goodbye):
            msg = get_cached_tts_url("It was a pleasure. Goodbye!", "en", base_url)
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response><Play>{msg}</Play></Response>'''
            return Response(content=twiml, media_type="application/xml")
        
        ai_response = ask_voice_ai(SpeechResult, CallSid, "en")
        audio_url = get_cached_tts_url(ai_response, "en", base_url)
        play_ai = f"<Play>{audio_url}</Play>" if audio_url else f'<Say language="en-US" voice="Polly.Joanna">{ai_response}</Say>'
        play_more = f"<Play>{get_cached_tts_url('Anything else?', 'en', base_url)}</Play>"
        play_bye = f"<Play>{get_cached_tts_url('Alright, goodbye.', 'en', base_url)}</Play>"
        
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto">
        {play_ai}
    </Gather>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto">
        {play_more}
    </Gather>
    {play_bye}
</Response>'''
    else:
        msg = get_cached_tts_url("I didn't hear you. Can you repeat?", "en", base_url)
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" language="en-US" action="{base_url}/process-speech-en" method="POST" timeout="5" speechTimeout="auto">
        <Play>{msg}</Play>
    </Gather>
</Response>'''
    return Response(content=twiml, media_type="application/xml")
