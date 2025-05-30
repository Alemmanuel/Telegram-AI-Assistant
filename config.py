import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del servidor
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))  # Render asignará el puerto automáticamente

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

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL and os.getenv('RENDER'):
    # En Render, construimos la URL de la base de datos usando las variables de entorno proporcionadas
    db_host = os.getenv('RENDER_DB_HOST')
    db_name = os.getenv('RENDER_DB_NAME', 'botdb')
    db_user = os.getenv('RENDER_DB_USER')
    db_pass = os.getenv('RENDER_DB_PASSWORD')
    DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"
elif not DATABASE_URL:
    DATABASE_URL = 'sqlite:///conversations.db'  # Fallback para desarrollo local

# Configuración del webhook
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
if os.getenv('RENDER') and not WEBHOOK_URL:
    # En Render, construimos la URL del webhook usando el nombre del servicio
    service_name = os.getenv('RENDER_SERVICE_NAME', 'telegram-bot')
    WEBHOOK_URL = f"https://{service_name}.onrender.com"
