import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

print("Buscando telefonos en la cuenta de Twilio...")
try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    numbers = client.incoming_phone_numbers.list()
    
    for record in numbers:
        print(f"Numero: {record.phone_number}, SID: {record.sid}")
        # Actualizar voz principal y fallback carrier-level
        client.incoming_phone_numbers(record.sid).update(
            voice_url="https://orion-cloud-1.onrender.com/incoming-call",
            voice_method="POST",
            voice_fallback_url="https://orion-cloud-1.onrender.com/voice/incoming",
            voice_fallback_method="POST",
            sms_url="https://orion-cloud-1.onrender.com/webhook/twilio_whatsapp",
            sms_method="POST"
        )
        print(f"OK: Webhook de VOZ (Principal + Fallback) y SMS actualizados para {record.phone_number}")
        
except Exception as e:
    print(f"Error conectando a Twilio: {e}")
