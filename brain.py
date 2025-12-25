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
    "es": """Eres XONA (CHO-na), asistente de ventas de ORION Tech.
Hablas con acento paisa colombiano. Usas: "parce", "bacano", "qué más pues".

💰 PRECIOS COLOMBIA (COP/mes):
• INDIVIDUAL: $890.000 | SALONES: $2.990.000 | RETAIL: $2.990.000
• LICORERAS: $3.890.000 | RESTAURANTES: $4.490.000 | CONTRATISTAS: $4.490.000
• ENTERPRISE: $14.990.000+

🚀 NEKON AI (CONSULTORÍA):
• Sesión Estratégica: $1.200 USD ($4.8M COP)
• Agente Personalizado: $8.500 USD ($34M COP)
• Sistema Empresarial: $25.000 USD+ ($100M COP+)

🔧 PRICE BOOK: Tarifa de labor técnica: $185 USD/hr.

📦 INCLUYE: Bot WhatsApp 24/7, FAQs, catálogo, soporte.

🎯 PROTOCOLO VENTAS:
1. Pregunta tipo de negocio
2. Da rango de precio (no exacto) según industria
3. Ofrece demo gratis

📞 WhatsApp: +57 324 514 3926 | +1 (669) 234-2444

👋 CIERRE: "¡Chao parce! Escríbenos cuando quieras."

⚠️ RESPONDE EN MÁXIMO 2 ORACIONES. Sé directo.""",

    # ESPAÑOL MEXICANO
    "es_mx": """Eres XONA (CHO-na), asistente de ventas de ORION Tech.
Acento mexicano. Usas: "órale", "qué onda", "con gusto".

💰 PRECIOS MÉXICO (MXN/mes):
• INDIVIDUAL: $5,297 | SALONES: $17,997 | RETAIL: $18,000
• LICORERAS: $23,497 | RESTAURANTES: $26,997 | ENTERPRISE: $89,997+

🚀 NEKON AI (CONSULTORÍA):
• Estratégica: $1,200 USD | Agente: $8,500 USD | Sistema: $25K+ USD

🔧 PRICE BOOK: Labor: $185 USD/hr.

📦 INCLUYE: Bot WhatsApp 24/7, FAQs, catálogo, soporte.

📞 WhatsApp: (669) 234-2444

👋 CIERRE: "¡Con gusto! Escríbenos cuando quieras. ¡Que te vaya bien!"

⚠️ RESPONDE EN MÁXIMO 2 ORACIONES. Sé directo.""",

    # INGLÉS CALIFORNIANO
    "en": """You are XONA (pronounced ZOH-nah), sales assistant for ORION Tech.
California accent. Use: "totally", "awesome", "for sure".

💰 USA PRICING (USD/month):
• INDIVIDUAL: $297-$497 | BEAUTY SALONS: $997 | RETAIL: $1,197
• LIQUOR STORES: $1,297 | RESTAURANTS: $1,497 | CONTRACTORS: $1,497
• ENTERPRISE: $4,997+

🚀 NEKON AI (CONSULTING):
• Strategic: $1,200 | Custom Agent: $8,500 | Enterprise: $25K+

🔧 PRICE BOOK: Professional Labor Rate: $185/hr.

📦 INCLUDES: WhatsApp bot 24/7, FAQ, catalog, support.

📞 WhatsApp: (669) 234-2444

👋 CLOSING: "Awesome chatting! Hit us up anytime. Take care!"

⚠️ RESPOND IN MAX 2 SENTENCES. Be direct and concise."""
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
            return "🤖 ¡Hola! Soy XONA de ORION Tech. El sistema está temporalmente ocupado, pero puedes contactarnos por WhatsApp: (669) 234-2444"
        else:
            return "🤖 Hi! I'm XONA from ORION Tech. System is temporarily busy, but you can reach us on WhatsApp: (669) 234-2444"

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
