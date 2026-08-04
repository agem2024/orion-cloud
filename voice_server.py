import os
import requests
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# MULTILINGUAL SYSTEM PROMPTS - MORALES PLUMBING
SYSTEM_MESSAGE_ES = """Eres Nekon, el asistente de IA y dispatcher por teléfono para Morales Plumbing (San Jose, CA).

IDENTIDAD:
- Tu nombre es Nekon.
- Representas a Morales Plumbing (Lic. C-36 #1156542).
- Hablas español fluido, profesional y amable.
- Eres el dispatcher: tomas detalles de los problemas de plomería y agendas citas.

SOBRE MORALES PLUMBING:
- Expertos en plomería residencial y comercial.
- Servicios principales: Water Heaters (Tankless y de tanque), Remodelación de Baños, Detección de Fugas, Inspección con Cámara, Limpieza de Drenajes, Reparación de Tuberías.
- Ubicación: San Jose, California (Bay Area).

PROTOCOLO DE ATENCIÓN:
1. Saludo: Preséntate como Nekon de Morales Plumbing.
2. Identificar el problema: Pregunta qué problema de plomería tienen.
3. Tomar datos: Si requieren servicio, pide su nombre, número de teléfono (si es diferente al que llaman) y dirección o ciudad.
4. Agendar: Diles que un técnico de Morales Plumbing los contactará en breve para confirmar la hora de llegada.
5. Emergencias: Si es una fuga mayor o emergencia, diles que un plomero será enviado de inmediato.

REGLAS:
- NUNCA des precios exactos, di que el técnico dará un estimado en el lugar.
- Respuestas CORTAS y conversacionales (máx 2 oraciones).
- NO ofrezcas servicios de IA ni menciones a Orion Tech. Eres plomería 100%.
- 🔴 SPAM/Ventas → "No estamos interesados, gracias" y TERMINA."""

SYSTEM_MESSAGE_EN = """You are Nekon, AI phone dispatcher for Morales Plumbing (San Jose, CA).

IDENTITY:
- Your name is Nekon.
- You represent Morales Plumbing (Lic. C-36 #1156542).
- Speak professional, friendly, natural English.
- You are the dispatcher: you take plumbing issue details and schedule appointments.

ABOUT MORALES PLUMBING:
- Residential and commercial plumbing experts.
- Main services: Water Heaters (Tankless and standard), Bathroom Remodels, Leak Detection, Camera Inspections, Drain Cleaning, Pipe Repair.
- Location: San Jose, California (Bay Area).

PROTOCOL:
1. Greeting: Introduce yourself as Nekon from Morales Plumbing.
2. Identify issue: Ask what plumbing problem they are experiencing.
3. Collect info: If they need service, ask for their name, phone number (if different), and city/address.
4. Schedule: Tell them a Morales Plumbing technician will contact them shortly to confirm arrival time.
5. Emergencies: If it's a major leak or emergency, tell them a plumber will be dispatched immediately.

RULES:
- NEVER give exact prices, say the technician will provide an estimate on-site.
- SHORT, conversational responses (max 2 sentences).
- DO NOT offer AI services or mention Orion Tech. You are 100% plumbing.
- 🔴 SPAM/Sales → "We are not interested, thank you" and END."""nces)
- Futuristic but accessible tone"""

# Default language
current_lang = "es"

app = FastAPI()

def get_ngrok_url():
    """Get the public ngrok URL from its local API"""
    try:
        resp = requests.get("http://localhost:4040/api/tunnels", timeout=2)
        tunnels = resp.json().get("tunnels", [])
        for tunnel in tunnels:
            if tunnel.get("proto") == "https":
                return tunnel.get("public_url", "")
        return None
    except:
        return None

def ask_openai(user_input: str, lang: str = "es") -> str:
    """Send message to OpenAI GPT-4o-mini and get response"""
    try:
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_msg = SYSTEM_MESSAGE_ES if lang == "es" else SYSTEM_MESSAGE_EN
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        
        if response.status_code == 200 and "choices" in data:
            ai_response = data["choices"][0]["message"]["content"].strip()
            print(f"🤖 OpenAI ({lang}): {ai_response}")
            return ai_response
        else:
            print(f"❌ OpenAI Error: {data}")
            return "Sorry, technical issue. Can you repeat?" if lang == "en" else "Perdona, problema técnico. ¿Puedes repetir?"
        
    except Exception as e:
        print(f"❌ OpenAI Exception: {e}")
        return "Sorry, there was an issue." if lang == "en" else "Perdona, hubo un problemita."

@app.get("/", response_class=HTMLResponse)
async def index_page():
    return "<h1>XONA Voice Server (Multilingual EN/ES) 🟢</h1>"

# SPANISH ENDPOINT
@app.api_route("/incoming-call", methods=["GET", "POST"])
@app.api_route("/incoming-call-es", methods=["GET", "POST"])
async def handle_incoming_call_es():
    """Handle incoming call - Spanish"""
    response = VoiceResponse()
    base_url = get_ngrok_url() or "http://localhost:5050"
    print(f"🌐 Spanish Call - Base URL: {base_url}")
    
    response.say(
        "Hola, soy Xona, asistente de ORION Tech. ¿En qué te puedo ayudar?",
        language="es-MX",
        voice="Polly.Mia"
    )
    
    gather = Gather(
        input="speech",
        language="es-MX",
        action=f"{base_url}/process-speech-es",
        method="POST",
        timeout=5,
        speech_timeout="auto"
    )
    response.append(gather)
    
    response.say("No escuché nada. Hasta luego.", language="es-MX")
    
    return Response(content=str(response), media_type="application/xml")

@app.api_route("/process-speech-es", methods=["GET", "POST"])
async def process_speech(SpeechResult: str = Form(None), CallSid: str = Form(None)):
    """Process user speech, get AI response, and continue conversation"""
    response = VoiceResponse()
    base_url = get_ngrok_url() or "http://localhost:5050"
    
    if SpeechResult:
        print(f"🎤 Usuario dijo: {SpeechResult}")
        
        goodbye_words = ["adiós", "adios", "bye", "chao", "hasta luego", "gracias", "ok gracias"]
        if any(word in SpeechResult.lower() for word in goodbye_words):
            response.say("Fue un placer. ¡Hasta luego!", language="es-MX", voice="Polly.Mia")
            return Response(content=str(response), media_type="application/xml")
        
        # Get AI response from OpenAI
        ai_response = ask_openai(SpeechResult)
        response.say(ai_response, language="es-MX", voice="Polly.Mia")
        
        # Continue listening
        gather = Gather(
            input="speech",
            language="es-MX",
            action=f"{base_url}/process-speech-es",
            method="POST",
            timeout=5,
            speech_timeout="auto"
        )
        response.append(gather)
        
        response.say("¿Algo más?", language="es-MX", voice="Polly.Mia")
        gather2 = Gather(
            input="speech",
            language="es-MX",
            action=f"{base_url}/process-speech-es",
            method="POST",
            timeout=5,
            speech_timeout="auto"
        )
        response.append(gather2)
        response.say("Bueno, hasta luego.", language="es-MX", voice="Polly.Mia")
    else:
        response.say("No te escuché. ¿Puedes repetir?", language="es-MX", voice="Polly.Mia")
        gather = Gather(
            input="speech",
            language="es-MX",
            action=f"{base_url}/process-speech-es",
            method="POST",
            timeout=5,
            speech_timeout="auto"
        )
        response.append(gather)
    
    return Response(content=str(response), media_type="application/xml")

# ENGLISH ENDPOINT
@app.api_route("/incoming-call-en", methods=["GET", "POST"])
async def handle_incoming_call_en():
    """Handle incoming call - English"""
    response = VoiceResponse()
    base_url = get_ngrok_url() or "http://localhost:5050"
    print(f"🌐 English Call - Base URL: {base_url}")
    
    response.say(
        "Hello, I'm XONA, assistant for ORION Tech. How can I help you?",
        language="en-US",
        voice="Polly.Joanna"
    )
    
    gather = Gather(
        input="speech",
        language="en-US",
        action=f"{base_url}/process-speech-en",
        method="POST",
        timeout=5,
        speech_timeout="auto"
    )
    response.append(gather)
    
    response.say("I didn't hear anything. Goodbye.", language="en-US")
    
    return Response(content=str(response), media_type="application/xml")

@app.api_route("/process-speech-en", methods=["GET", "POST"])
async def process_speech_en(SpeechResult: str = Form(None), CallSid: str = Form(None)):
    """Process user speech in English"""
    response = VoiceResponse()
    base_url = get_ngrok_url() or "http://localhost:5050"
    
    if SpeechResult:
        print(f"🎤 User said: {SpeechResult}")
        
        goodbye_words = ["goodbye", "bye", "thanks", "thank you", "ok thanks", "that's all"]
        if any(word in SpeechResult.lower() for word in goodbye_words):
            response.say("It was a pleasure. Goodbye!", language="en-US", voice="Polly.Joanna")
            return Response(content=str(response), media_type="application/xml")
        
        # Get AI response from OpenAI in English
        ai_response = ask_openai(SpeechResult, lang="en")
        response.say(ai_response, language="en-US", voice="Polly.Joanna")
        
        # Continue listening
        gather = Gather(
            input="speech",
            language="en-US",
            action=f"{base_url}/process-speech-en",
            method="POST",
            timeout=5,
            speech_timeout="auto"
        )
        response.append(gather)
        
        response.say("Anything else?", language="en-US", voice="Polly.Joanna")
        gather2 = Gather(
            input="speech",
            language="en-US",
            action=f"{base_url}/process-speech-en",
            method="POST",
            timeout=5,
            speech_timeout="auto"
        )
        response.append(gather2)
        response.say("Alright, goodbye.", language="en-US", voice="Polly.Joanna")
    else:
        response.say("I didn't hear you. Can you repeat?", language="en-US", voice="Polly.Joanna")
        gather = Gather(
            input="speech",
            language="en-US",
            action=f"{base_url}/process-speech-en",
            method="POST",
            timeout=5,
            speech_timeout="auto"
        )
        response.append(gather)
    
    return Response(content=str(response), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting XONA Voice Server (Multilingual EN/ES)...")
    print("📞 Spanish: /incoming-call or /incoming-call-es")
    print("📞 English: /incoming-call-en")
    uvicorn.run(app, host="0.0.0.0", port=5050)
