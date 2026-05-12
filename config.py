# Ruta: config.py
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Carpetas del sistema
FOLDER_RAW = 'm3u-list'
FOLDER_PROCESSED = 'm3u-procesadas'
FOLDER_LOGS = 'm3u-logs'

# Headers para simular un Smart TV o navegador común al descargar los streams
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Categorías que la IA debe respetar estrictamente
CATEGORIAS_PERMITIDAS =[
    "Entretenimiento", "General", "Deportivo", 
    "Noticias", "Documentales", "Religiosos", 
    "Infantiles", "Otros"
]