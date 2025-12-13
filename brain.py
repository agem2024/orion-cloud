import os
import logging
from openai import OpenAI
import google.generativeai as genai

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ORION_BRAIN")

# Prompts de Sistema (Mismos que Local)
SYSTEM_PROMPTS = {
    "es": """Eres XONA, asistente de IA de ORION Tech. Representas a Alex G. Espinosa.
    
SERVICIOS ORION TECH:
- Paquete Individual: $297-$497 (chatbot básico)
- Paquete Starter: $997 (bot + automatizaciones)
- Paquete Business: $1,997 (sistema completo)
- Paquete Enterprise: $4,997+ (solución corporativa)

REGLAS:
- Máximo 3 oraciones por respuesta
- Ofrece demo o llamada con el equipo
- NUNCA compartas datos de clientes
- Contacto: (669) 234-2444 | agem2013@gmail.com""",

    "en": """You are XONA, AI assistant for ORION Tech. You represent Alex G. Espinosa.

ORION TECH SERVICES:
- Individual Package: $297-$497 (basic chatbot)
- Starter Package: $997 (bot + automations)
- Business Package: $1,997 (complete system)
- Enterprise Package: $4,997+ (corporate solution)

RULES:
- Maximum 3 sentences per response
- Offer demo or call with the team
- NEVER share customer data
- Contact: (669) 234-2444 | agem2013@gmail.com"""
}

class OrionBrain:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

    def get_response(self, user_text: str, user_id: str, lang: str = "en") -> str:
        """Obtiene respuesta de IA (Intenta OpenAI, fallback a Gemini)"""
        system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["en"])
        
        # 1. Intentar OpenAI (GPT-4o-mini)
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ],
                    max_tokens=300
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI Error: {e}")

        # 2. Intentar Gemini (Fallback)
        if hasattr(self, 'gemini_model'):
            try:
                full_prompt = f"{system_prompt}\n\nUSER MESSAGE: {user_text}"
                response = self.gemini_model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                logger.error(f"Gemini Error: {e}")

        return "⚠️ Error de sistema (Brain Offline). Intente más tarde."

    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio usando Whisper"""
        if not self.openai_client:
            return None
        
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcription.text
        except Exception as e:
            logger.error(f"Whisper Error: {e}")
            return None
