import os
import sys

# Redirigir el trafico de main.py (el viejo) al nuevo Motor V9 (chatwoot_webhook.py)
# Esto evita que tengas que cambiar la configuracion en Render.

from chatwoot_webhook import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
