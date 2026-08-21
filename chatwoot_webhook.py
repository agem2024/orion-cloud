from fastapi import FastAPI, Request
import logging
from sofia_v9_app import SofiaLinV9Engine
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

app = FastAPI(title="Sofia Lin V9 Omnichannel Gateway")
logger = logging.getLogger("OmnichannelGateway")
engine = SofiaLinV9Engine()

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error sending telegram message: {e}")

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    payload = await request.json()
    
    if "message" in payload and "text" in payload["message"]:
        chat_id = payload["message"]["chat"]["id"]
        text = payload["message"]["text"]
        
        logger.info(f"Nuevo mensaje de Telegram de {chat_id}: {text}")
        
        call_data = {
            "caller_id": str(chat_id),
            "transcript": text,
            "channel": "telegram"
        }
        
        result = engine.process_incoming_call(call_data)
        reply_text = result.get("audio_response_text", "No response generated.")
        
        # Enviar la respuesta real de vuelta al usuario en Telegram
        send_telegram_message(chat_id, reply_text)
        
        return {"status": "processed"}
        
    return {"status": "ignored"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
