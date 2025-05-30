import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del servidor
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))

# Tokens y API keys
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado")

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY no está configurado")

SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
if not SERPAPI_API_KEY:
    raise ValueError("SERPAPI_API_KEY no está configurado")

# Configuración del webhook
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
if os.getenv('RENDER') and not WEBHOOK_URL:
    # En Render, construimos la URL del webhook usando el nombre del servicio
    service_name = os.getenv('RENDER_SERVICE_NAME', 'telegram-bot')
    WEBHOOK_URL = f"https://{service_name}.onrender.com"
