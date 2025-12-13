# ORION Cloud - XONA AI Backend

Backend para el chatbot XONA AI de ORION Tech.

## Endpoints
- `GET /` - Health check
- `POST /api/chat` - Chat con XONA AI

## Deploy en Render

Build Command:
```
pip install -r requirements.txt
```

Start Command:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Variables de Entorno Requeridas
- `GEMINI_API_KEY` - API key de Google Gemini
- `OPENAI_API_KEY` - (Opcional) API key de OpenAI
