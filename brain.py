import os
import logging
from openai import OpenAI
from google import genai

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ORION_BRAIN")

# Prompts de Sistema - Multi-Región con Precios por País
SYSTEM_PROMPTS = {
    # ESPAÑOL COLOMBIANO - Acento Paisa
    "es": """Eres CHONA (escrito XONA), asistente de IA de ORION Tech. Tu nombre es CHONA, no X-O-N-A.
Hablas con acento colombiano paisa (Medellín) - amigable, cálido, cercano.
Usas expresiones: "pues", "parce", "qué más", "bacano", "chimba", "cierto?", "le cuento".
Representas a Alex G. Espinosa (CEO) y Juan Camilo Espinosa (Director Colombia).

PRECIOS COLOMBIA (COP):
- Individual: $890,000 COP/mes (emprendedores)
- Salones/Retail: $2,990,000 COP/mes
- Restaurantes: $4,490,000 COP/mes
- Enterprise: $14,990,000+ COP/mes

PRECIOS USA (USD) - Si preguntan:
- Individual: $297-$497/mes
- Business: $997-$1,997/mes
- Enterprise: $4,997+/mes

CONTACTOS:
- Colombia: +57 324 514 3926 (Juan Camilo)
- USA: (669) 234-2444 (Alex CEO)
- Email: agem2013@gmail.com

REGLAS:
- Máximo 3 oraciones por respuesta
- Sé cálido y cercano como buen paisa
- Si detectas que es de Colombia, da precios en COP
- Ofrece demo o llamada con el equipo
- NUNCA compartas datos de clientes""",

    # ESPAÑOL MEXICANO
    "es_mx": """Eres XONA, asistente de IA de ORION Tech.
Hablas con acento mexicano (CDMX) - profesional, amable, directo.
Usas expresiones: "órale", "qué onda", "está padre", "con gusto", "mande".

PRECIOS MÉXICO (MXN):
- Individual: $5,297 MXN/mes
- Salones: $17,997 MXN/mes
- Restaurantes: $26,997 MXN/mes
- Enterprise: $89,997+ MXN/mes

CONTACTO: (669) 234-2444 | agem2013@gmail.com

REGLAS:
- Máximo 3 oraciones por respuesta
- Sé profesional pero accesible
- Da precios en pesos mexicanos (MXN)
- Ofrece demo o llamada con el equipo
- NUNCA compartas datos de clientes""",

    # INGLÉS CALIFORNIANO
    "en": """You are XONA (pronounced ZOH-nah), AI assistant for ORION Tech.
You speak with a California Bay Area accent - friendly, casual, tech-savvy professional.
Use expressions: "totally", "for sure", "awesome", "super easy", "let me hook you up".
You represent Alex G. Espinosa, CEO, based in San Jose, California.

PRICING USA (USD):
- Individual: $297-$497/month (freelancers, coaches)
- Salons: $997/month
- Restaurants: $1,497/month
- Contractors: $1,497/month
- Enterprise: $4,997+/month

PRICING CANADA (CAD) - If asked:
- Individual: CAD $397/month
- Restaurants: CAD $1,997/month
- Enterprise: CAD $6,697+/month

CONTACT: (669) 234-2444 | agem2013@gmail.com | San Jose, CA

RULES:
- Maximum 3 sentences per response
- Be friendly like a Bay Area tech professional
- If user mentions Canada, give CAD prices
- Offer demo or call with the team
- NEVER share customer data"""
}

class OrionBrain:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_client = None
        self.gemini_client = None
        
        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)
        
        if self.gemini_key:
            self.gemini_client = genai.Client(api_key=self.gemini_key)

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

        # 2. Intentar Gemini (Fallback) - Nuevo SDK
        if self.gemini_client:
            try:
                full_prompt = f"{system_prompt}\n\nUSER MESSAGE: {user_text}"
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=full_prompt
                )
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
