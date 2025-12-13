import os
import httpx
import asyncio

# Configura estas variables ANTES de correr el script
TOKEN = "8572298959:AAGR3Q9ohwJaK38EadeYQ0jVCXxb7VTTlb0"
RENDER_URL = "https://orion-cloud.onrender.com"

async def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    webhook_url = f"{RENDER_URL}/webhook/{TOKEN}"
    
    print(f"🔗 Conectando Webhook a: {webhook_url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data={"url": webhook_url})
        print(f"📩 Respuesta Telegram: {response.json()}")

if __name__ == "__main__":
    if TOKEN == "TU_TOKEN_NUEVO_AQUI":
        print("❌ ERROR: Edita este archivo y pon tu TOKEN y URL de Render primero.")
    else:
        asyncio.run(set_webhook())
