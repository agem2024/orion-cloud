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

async def telegram_webhook(request: Request):
    """Handler Telegram — registrado en main.py en /webhook/telegram"""
    try:
        payload = await request.json()
        if "message" in payload and "text" in payload["message"]:
            chat_id = payload["message"]["chat"]["id"]
            text = payload["message"]["text"]
            logger.info(f"Telegram msg from {chat_id}: {text}")
            result = engine.process_incoming_call({
                "caller_id": str(chat_id),
                "transcript": text,
                "channel": "telegram"
            })
            reply = result.get("audio_response_text", "Thank you for contacting Morales Plumbing. How can we help you today?")
            send_telegram_message(chat_id, reply)
            return {"status": "processed"}
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
    return {"status": "ignored"}

from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import Response

async def twilio_whatsapp_webhook(request: Request):
    """Handler WhatsApp/Twilio — registrado en main.py en /webhook/twilio_whatsapp"""
    try:
        form_data = await request.form()
        sender  = form_data.get("From", "")
        content = form_data.get("Body", "")
        to_num  = form_data.get("To", "")
        logger.info(f"WhatsApp msg from {sender} to {to_num}: {content}")

        resp = MessagingResponse()
        if content:
            result = engine.process_incoming_call({
                "caller_id": sender,
                "transcript": content,
                "channel": "whatsapp"
            })
            reply_text = result.get(
                "audio_response_text",
                "Thank you for contacting Morales Plumbing. How can we help you today?"
            )
            resp.message(reply_text)

        return Response(content=str(resp), media_type="application/xml")
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        resp = MessagingResponse()
        resp.message("Thank you for contacting Morales Plumbing. Please call us at (669) 213-4422.")
        return Response(content=str(resp), media_type="application/xml")
