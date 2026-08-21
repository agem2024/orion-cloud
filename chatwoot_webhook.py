import os
from fastapi import Request
import logging
from sofia_v9_app import SofiaLinV9Engine
from twilio.rest import Client
import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

logger = logging.getLogger("OmnichannelGateway")
engine = SofiaLinV9Engine()

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        logger.error(f"Telegram error: {e}")

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    payload = await request.json()
    if "message" in payload and "text" in payload["message"]:
        chat_id = payload["message"]["chat"]["id"]
        text = payload["message"]["text"]
        logger.info(f"Telegram Msg from {chat_id}: {text}")
        result = engine.process_incoming_call({"caller_id": str(chat_id), "transcript": text, "channel": "telegram"})
        send_telegram_message(chat_id, result.get("audio_response_text", "Error"))
        return {"status": "processed"}
    return {"status": "ignored"}

from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import Response

@app.post("/webhook/twilio_whatsapp")
async def twilio_whatsapp_webhook(request: Request):
    form_data = await request.form()
    sender = form_data.get("From", "")
    content = form_data.get("Body", "")
    to_number = form_data.get("To", "")
    
    logger.info(f"WhatsApp/SMS Msg from {sender} to {to_number}: {content}")
    
    resp = MessagingResponse()
    if content:
        result = engine.process_incoming_call({"caller_id": sender, "transcript": content, "channel": "whatsapp"})
        reply_text = result.get("audio_response_text", "Gracias por contactar a Morales Plumbing. ¿En qué podemos ayudarle?")
        resp.message(reply_text)
    
    return Response(content=str(resp), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
