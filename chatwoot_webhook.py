"""
Chatwoot & Evolution API Webhook Gateway (FastAPI)
Conecta los canales de texto (WhatsApp, Web, Telegram) al Motor V9.1.
"""
from fastapi import FastAPI, Request, HTTPException
import logging
from sofia_v9_app import SofiaLinV9Engine

app = FastAPI(title="Sofia Lin V9 Omnichannel Gateway")
logger = logging.getLogger("OmnichannelGateway")
engine = SofiaLinV9Engine()

@app.post("/webhook/chatwoot")
async def chatwoot_webhook(request: Request):
    """
    Recibe eventos de Chatwoot (mensajes entrantes de clientes).
    """
    payload = await request.json()
    
    # Solo procesar mensajes de clientes (no de agentes humanos)
    if payload.get("event") == "message_created" and payload.get("message_type") == "incoming":
        conversation_id = payload.get("conversation", {}).get("id")
        content = payload.get("content", "")
        sender = payload.get("sender", {}).get("phone_number", "Unknown")
        
        logger.info(f"Nuevo mensaje de texto de {sender}: {content}")
        
        # Enviar al motor V9.1 (reutilizando la misma lógica de voz, adaptada a texto)
        call_data = {
            "caller_id": sender,
            "transcript": content,
            "channel": "text"
        }
        
        result = engine.process_incoming_call(call_data)
        
        # Aquí se ejecutaría la lógica para hacer el POST de respuesta hacia la API de Chatwoot
        logger.info(f"Respuesta de Sofia V9.1: {result.get('audio_response_text')}")
        
        return {"status": "processed", "reply": result.get("audio_response_text")}
        
    return {"status": "ignored"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
