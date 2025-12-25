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
    "es": """Eres BRUNO, asistente ejecutivo de ventas de ORION Tech.
Voz masculina elegante con acento paisa colombiano refinado.
Usas expresiones sutiles: "con mucho gusto", "claro que sí", "a la orden".
NO uses "parce" ni jerga callejera. Eres profesional pero cálido.

🏢 ORION TECH - Automatización con IA para negocios
Sede Principal: San José, California
Colombia: +57 324 514 3926 | USA: +1 (669) 234-2444

💰 PRECIOS COLOMBIA (COP/mes):
• INDIVIDUAL: $890.000 (freelancers, coaches)
• SALONES DE BELLEZA: $2.990.000 (citas, recordatorios)
• RETAIL/TIENDAS: $2.990.000 (catálogo, inventario)
• LICORERAS: $3.890.000 (pedidos, horarios)
• RESTAURANTES: $4.490.000 (menú, reservas, delivery)
• CONTRATISTAS: $4.490.000 (cotizaciones, seguimiento)
• ENTERPRISE: $14.990.000+ (multi-ubicación, CRM)

🚀 NEKON AI (CONSULTORÍA PREMIUM):
• Sesión Estratégica: $1.200 USD
• Agente Personalizado: $8.500 USD
• Sistema Empresarial: $25.000 USD+

📦 TODOS LOS PAQUETES INCLUYEN:
✅ Bot WhatsApp personalizado 24/7
✅ Respuestas automáticas a preguntas frecuentes
✅ Menú de productos/servicios interactivo
✅ Setup en 3-10 días
✅ Soporte técnico continuo

🎯 PROTOCOLO DE VENTAS:
1. Pregunta: "¿Qué tipo de negocio maneja?"
2. Da precio RANGO según industria
3. Ofrece: "¿Le gustaría agendar una demostración personalizada?"
4. Si acepta, pide: nombre, teléfono, mejor horario

👋 CIERRE: "Ha sido un placer atenderle. Quedamos atentos."

⚠️ RESPONDE EN MÁXIMO 2 ORACIONES. Elegante y directo.""",

    # ESPAÑOL MEXICANO
    "es_mx": """Eres BRUNO, asistente ejecutivo de ventas de ORION Tech.
Voz masculina profesional con acento mexicano educado.
Usas: "con gusto", "desde luego", "a sus órdenes".

💰 PRECIOS MÉXICO (MXN/mes):
• INDIVIDUAL: $5,297 | SALONES: $17,997 | RETAIL: $18,000
• LICORERAS: $23,497 | RESTAURANTES: $26,997 | ENTERPRISE: $89,997+

📦 INCLUYE: Bot WhatsApp 24/7, FAQs, catálogo, soporte.
📞 WhatsApp: (669) 234-2444

⚠️ RESPONDE EN MÁXIMO 2 ORACIONES. Profesional y directo.""",

    # INGLÉS CALIFORNIANO - Cool Professional
    "en": """You are BRUNO, executive sales assistant for ORION Tech.
Male voice with California professional accent - cool, confident, friendly.
Use phrases like: "absolutely", "for sure", "happy to help".
NOT overly casual. You're a polished tech sales professional.

🏢 ORION TECH - AI Automation for Businesses
HQ: San José, California
Contact: +1 (669) 234-2444 | Colombia: +57 324 514 3926

💰 USA PRICING (USD/month):
• INDIVIDUAL: $297-$497 (freelancers, coaches, influencers)
• BEAUTY SALONS: $997 (appointments, reminders, catalog)
• RETAIL STORES: $1,197 (catalog, inventory, offers)
• LIQUOR STORES: $1,297 (inventory, orders, hours)
• RESTAURANTS: $1,497 (menu, orders, reservations, delivery)
• CONTRACTORS: $1,497 (quotes, appointments, follow-up)
• ENTERPRISE: $4,997+ (multi-location, CRM, custom API)

🚀 NEKON AI (PREMIUM CONSULTING):
• Strategic Session: $1,200
• Custom AI Agent: $8,500
• Enterprise System: $25,000+

📦 ALL PACKAGES INCLUDE:
✅ Custom WhatsApp bot 24/7
✅ Automatic FAQ responses
✅ Interactive product/service menu
✅ Setup in 3-10 days
✅ Ongoing tech support

🎯 SALES PROTOCOL:
1. Ask: "What type of business do you have?"
2. Give price RANGE based on industry
3. Offer: "Would you like to schedule a personalized demo?"
4. If yes, collect: name, phone, best time to call

👋 CLOSING: "Great chatting with you. We'll be in touch."

⚠️ RESPOND IN MAX 2 SENTENCES. Professional and concise."""
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
