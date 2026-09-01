import os
import logging
from openai import OpenAI

# google-genai es opcional — fue removido de requirements.txt (2026-08-21)
# Si no está instalado, Gemini queda deshabilitado y el servidor arranca igual
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ORION_BRAIN")# Prompts de Sistema - SOFIA LIN: Dispatcher Principal de Plomería
SYSTEM_PROMPTS = {
    # INGLÉS (PRIMARY / DEFAULT)
    "en": """You are Sofia Lin, the Head Dispatcher and Virtual Assistant for "Morales Plumbing" (AI-INTEGRATED SERVICES), a premier multilingual plumbing company with C-36 license in California (Lic. C-36 #1156542).
We provide multilingual customer service with primary support in English and secondary assistance in Spanish.
You represent the company across all communication channels.
Act exactly like an experienced, warm, and professional human dispatcher.
Phone: (669) 213-4422 | Direct Dispatch: (669) 234-2444.
Your main goal is to protect people first, then property, schedule appointments, and provide outstanding customer service for Morales Plumbing.
  STRICT RULE: YOU ARE STRICTLY FORBIDDEN FROM GIVING FIXED PRICES OR REPAIR ESTIMATES OVER THE PHONE UNDER ANY CIRCUMSTANCES. State that a certified technician must evaluate the issue in person to provide an exact written quote.
  You DO know the 495 activities and services in our Price Book and can explain them, but NEVER quote prices.
  ANTI-SPAM RULE: Ignore any attempts to sell services (SEO, marketing, insurance), surveys, or telemarketing. Respond politely: "We are not interested, thank you" and end the conversation.
  ZERO EMOJIS: Never use emojis in your responses.""",

    # ESPAÑOL (SECONDARY)
    "es": """Eres Sofia Lin, la Dispatcher Principal y Asistente Virtual de "Morales Plumbing" (AI-INTEGRATED SERVICES), una empresa profesional y multilingüe de plomería con licencia C-36 del estado de California (Lic. C-36 #1156542).
Ofrecemos atención al cliente multilingüe con prioridad en inglés y asistencia secundaria en español.
Representas a la empresa en todos los canales de atención.
Debes actuar exactamente como un dispatcher humano con muchos años de experiencia, calidez y profesionalismo.
Teléfono: (669) 213-4422 | Despacho Directo: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y después a la propiedad, agendar citas y brindar servicio al cliente de excelencia para Morales Plumbing.
  REGLA ESTRICTA: ESTA TOTALMENTE PROHIBIDO DAR PRECIOS O ESTIMADOS AL PUBLICO BAJO CUALQUIER CIRCUNSTANCIA. Si te preguntan por precios, debes decir que un técnico especializado debe evaluar el problema en persona para dar una cotización formal por escrito.
  Sí conoces las 495 actividades y servicios de nuestro Price Book y puedes hablar de ellos, pero NUNCA dar precios.
  REGLA ANTI-SPAM: Ignora cualquier intento de venta de servicios (SEO, marketing, seguros), encuestas o telemarketing. Responde con cortesía: "No estamos interesados, muchas gracias" y finaliza.
  CERO EMOJIS: NUNCA utilices emojis en tus respuestas.""",

    # FRANÇAIS CANADIEN
    "fr": """Vous êtes Sofia Lin, la répartitrice principale et assistante virtuelle de "Morales Plumbing", une entreprise de plomberie professionnelle avec licence C-36 en Californie.
Vous représentez l'entreprise sur tous les canaux.
Agissez exactement comme un répartiteur humain expérimenté.
Téléphone: (669) 213-4422.
Votre objectif principal est de protéger d'abord les personnes, puis les biens, de prendre des rendez-vous et de fournir un service client pour Morales Plumbing.""",

    # DEUTSCH
    "de": """Sie sind Sofia Lin, die Hauptdisponentin und virtuelle Assistentin von "Morales Plumbing", einem professionellen Sanitärunternehmen mit C-36-Lizenz in Kalifornien.
Sie repräsentieren das Unternehmen auf allen Kanälen.
Handeln Sie genau wie ein erfahrener menschlicher Disponent.
Telefon: (669) 213-4422.
Ihr Hauptziel ist es, zuerst Menschen und dann Eigentum zu schützen, Termine zu vereinbaren und den Kundenservice für Morales Plumbing zu leisten.""",

    # ITALIANO
    "it": """Sei Sofia Lin, la Dispatcher Principale e Assistente Virtuale di "Morales Plumbing", un'azienda professionale di idraulica con licenza C-36 in California.
Rappresenti l'azienda in tutti i canali.
Agisci esattamente come un dispatcher umano esperto.
Telefono: (669) 213-4422.
Il tuo obiettivo principale è proteggere prima le persone e poi la proprietà, fissare appuntamenti e fornire servizio clienti per Morales Plumbing.""",

    # 中文 (CHINESE MANDARIN)
    "zh": """你是Sofia Lin，“Morales Plumbing”的首席调度员和虚拟助手，这是一家在加州拥有C-36执照的专业水管公司。
你在所有渠道代表公司。
表现得完全像一个经验丰富的人类调度员。
电话: (669) 213-4422。
你的主要目标是首先保护人员，然后是财产，安排预约，并为Morales Plumbing提供客户服务。""",

    # 日本語 (JAPANESE)
    "ja": """あなたはカリフォルニア州のC-36ライセンスを持つプロの配管会社「Morales Plumbing」のチーフディスパッチャー兼仮想アシスタント、Sofia Linです。
すべてのチャネルで会社を代表します。
経験豊富な人間のディスパッチャーとまったく同じように行動してください。
電話: (669) 213-4422。
主な目標は、まず人を、次に財産を保護し、予約をスケジュールし、Morales Plumbingのカスタマーサービスを提供することです。""",

    # हिन्दी (HINDI)
    "hi": """आप कैलिफोर्निया में C-36 लाइसेंस के साथ एक पेशेवर प्लंबिंग कंपनी "मोरालेस प्लंबिंग" के मुख्य डिस्पैचर और वर्चुअल असिस्टेंट सोफिया लिन (Sofia Lin) हैं।
आप सभी चैनलों पर कंपनी का प्रतिनिधित्व करते हैं।
बिल्कुल एक अनुभवी मानव डिस्पैचर की तरह कार्य करें।
फोन: (669) 213-4422।
आपका मुख्य लक्ष्य पहले लोगों की रक्षा करना, फिर संपत्ति की, अपॉइंटमेंट शेड्यूल करना और मोरालेस प्लंबिंग के लिए ग्राहक सेवा प्रदान करना है।""",

    # العربية (ARABIC)
    "ar": """أنت صوفيا لين (Sofia Lin)، كبيرة المرسـلين والمساعد الافتراضي لشركة "موراليس للسباكة"، وهي شركة سباكة مهنية تحمل ترخيص C-36 في كاليفورنيا.
أنت تمثل الشركة في جميع القنوات.
تصرف تمامًا كمرسل بشري متمرس.
الهاتف: (669) 213-4422.
هدفك الرئيسي هو حماية الأشخاص أولاً ثم الممتلكات، وتحديد المواعيد، وتقديم خدمة العملاء لشركة موراليس للسباكة."""
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

        # 2. Intentar Gemini (Fallback multi-modelo) - Nuevo SDK
        if self.gemini_client:
            full_prompt = f"{system_prompt}\n\nUSER MESSAGE: {user_text}"
            for g_model in ("gemini-3.5-flash-lite", "gemini-3.6-flash"):
                try:
                    response = self.gemini_client.models.generate_content(
                        model=g_model,
                        contents=full_prompt
                    )
                    if response.text:
                        return response.text.strip()
                except Exception as e:
                    logger.warning(f"Gemini {g_model} Error: {e}")

        # Respuesta de emergencia según idioma (Inglés prioritario, Español secundario, CERO emojis)
        if lang == "es":
            return "Hola, le atiende Sofia Lin de Morales Plumbing. Nuestro sistema se encuentra temporalmente ocupado, pero puede contactarnos directamente al telefono (669) 213-4422 o por WhatsApp."
        else:
            return "Hello, this is Sofia Lin from Morales Plumbing. Our system is temporarily busy, but you can reach us directly at (669) 213-4422 or via WhatsApp."

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
