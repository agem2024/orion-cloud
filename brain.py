import os
import logging
from openai import OpenAI
from google import genai

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ORION_BRAIN")

# Prompts de Sistema - BRUNO: Voz Masculina Elegante ORION Tech
SYSTEM_PROMPTS = {
    # ESPAÑOL COLOMBIANO - Paisa Elegante Masculino
    "es": """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing.""",

    # FRANÇAIS CANADIEN
    "fr": """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing.""",

    # DEUTSCH
    "de": """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing.""",

    # ITALIANO
    "it": """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing.""",

    # 中文 (CHINESE MANDARIN)
    "zh": """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing.""",

    # 日本語 (JAPANESE)
    "ja": """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing.""",

    # हिन्दी (HINDI)
    "hi": """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing.""",

    # العربية (ARABIC)
    "ar": """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing."""
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
                    max_tokens=150,
                    temperature=0.7
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

        # Respuesta de emergencia según idioma
        if lang == "es":
            return "🤖 ¡Hola! Soy Alex de Morales Plumbing. El sistema está temporalmente ocupado, pero puedes contactarnos por WhatsApp: (669) 234-2444"
        else:
            return "🤖 Hi! I'm Alex from Morales Plumbing. System is temporarily busy, but you can reach us on WhatsApp: (669) 234-2444"

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
