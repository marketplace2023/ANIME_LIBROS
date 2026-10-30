import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Proveedor de API
ANIME_API_PROVIDER = os.getenv("ANIME_API_PROVIDER", "ANILIST")

# Rutas de almacenamiento relativas
DATABASE_PATH = os.getenv("DATABASE_PATH", "storage/database/anime.db")
COVERS_PATH = os.getenv("COVERS_PATH", "storage/covers")
EXPORT_PATH = os.getenv("EXPORT_PATH", "storage/exports")

# Rutas de almacenamiento absolutas
DB_FILE_PATH = BASE_DIR / DATABASE_PATH
COVERS_DIR_PATH = BASE_DIR / COVERS_PATH
EXPORT_DIR_PATH = BASE_DIR / EXPORT_PATH

# Asegurar que las carpetas de almacenamiento existan
DB_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
COVERS_DIR_PATH.mkdir(parents=True, exist_ok=True)
EXPORT_DIR_PATH.mkdir(parents=True, exist_ok=True)

# Configuración del Importador
REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "1.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "5"))

# Configuración de PDF
MAX_RECORDS_PER_VOLUME = int(os.getenv("MAX_RECORDS_PER_VOLUME", "500"))
PDF_CARD_LAYOUT = os.getenv("PDF_CARD_LAYOUT", "COMPACT")
INCLUDE_ADULT_CONTENT = os.getenv("INCLUDE_ADULT_CONTENT", "false").lower() == "true"
DOWNLOAD_COVERS = os.getenv("DOWNLOAD_COVERS", "true").lower() == "true"
