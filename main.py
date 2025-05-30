from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import logging
from database import init_db
from agent import ask_agent
from config import (
    TELEGRAM_BOT_TOKEN,
    HOST,
    PORT,
    WEBHOOK_URL
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar la aplicación
app = FastAPI(title="Telegram Bot API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar la base de datos
@app.on_event("startup")
async def startup_event():
    init_db()
    # Configurar webhook de Telegram
    if WEBHOOK_URL:
        set_webhook()

def set_webhook():
    """Configura el webhook de Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    webhook_url = f"{WEBHOOK_URL}/"
    response = requests.post(url, json={"url": webhook_url})
    if response.status_code == 200:
        logger.info(f"Webhook configurado correctamente en {webhook_url}")
    else:
        logger.error(f"Error configurando webhook: {response.text}")

def send_telegram_message(chat_id, text):
    """Envía mensaje a Telegram con manejo de errores."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Error enviando mensaje a Telegram: {str(e)}")
        return False

@app.post("/")
async def webhook(req: Request):
    """Webhook de Telegram con manejo de errores mejorado"""
    try:
        data = await req.json()
        message = data.get("message", {}).get("text")
        chat_id = data.get("message", {}).get("chat", {}).get("id")

        if not message or not chat_id:
            raise HTTPException(status_code=400, detail="Mensaje o chat_id no encontrados")

        # Obtener respuesta del agente
        try:
            reply = ask_agent(message, str(chat_id))
            if reply:
                if send_telegram_message(chat_id, reply):
                    return {"ok": True, "message": "Mensaje enviado correctamente"}
                else:
                    raise HTTPException(status_code=500, detail="Error enviando mensaje a Telegram")
            else:
                raise HTTPException(status_code=500, detail="No se obtuvo respuesta del agente")
        except Exception as e:
            error_msg = f"Error procesando el mensaje: {str(e)}"
            logger.error(error_msg)
            send_telegram_message(chat_id, "Lo siento, hubo un error procesando tu mensaje. Por favor, intenta más tarde.")
            raise HTTPException(status_code=500, detail=error_msg)

    except Exception as e:
        logger.error(f"Error en el webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en el webhook: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
