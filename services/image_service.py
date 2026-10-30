import httpx
from PIL import Image
from io import BytesIO
from pathlib import Path
from config.settings import COVERS_DIR_PATH, BASE_DIR

def get_target_directory(release_year: int) -> Path:
    """
    Retorna la subcarpeta de destino según el año o la década.
    Ejemplo: 1995 -> storage/covers/1990-1999/
    """
    if not release_year:
        return COVERS_DIR_PATH / "unknown-year"
    
    decade_start = (release_year // 10) * 10
    decade_end = decade_start + 9
    return COVERS_DIR_PATH / f"{decade_start}-{decade_end}"

def generate_placeholder_cover() -> str:
    """
    Genera una imagen de portada genérica (placeholder) si no existe.
    Retorna la ruta relativa del archivo.
    """
    target_path = COVERS_DIR_PATH / "placeholder.jpg"
    if target_path.exists():
        return str(target_path.relative_to(BASE_DIR))
        
    try:
        COVERS_DIR_PATH.mkdir(parents=True, exist_ok=True)
        # Crear una imagen gris de 500x750
        img = Image.new('RGB', (500, 750), color=(220, 225, 230))
        
        # Guardar imagen
        img.save(target_path, "JPEG")
        return str(target_path.relative_to(BASE_DIR))
    except Exception as e:
        print(f"Error al generar portada placeholder: {e}")
        return None

def download_and_optimize_cover(anime_id: str, cover_url: str, release_year: int) -> str:
    """
    Descarga la portada desde una URL, la convierte a RGB,
    la redimensiona a un máximo de 500x750 px conservando la relación de aspecto,
    y la guarda en formato JPEG optimizado al 75%.
    
    Retorna la ruta relativa del archivo final respecto al directorio base del proyecto,
    o la portada predeterminada si ocurre algún error.
    """
    if not cover_url:
        return generate_placeholder_cover()
        
    try:
        # Descarga de la imagen
        with httpx.Client() as client:
            response = client.get(cover_url, timeout=20.0)
            if response.status_code != 200:
                return generate_placeholder_cover()
            image_bytes = response.content
            
        # Determinar directorio de destino y crearlo si no existe
        target_dir = get_target_directory(release_year)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar un nombre de archivo unificado
        filename = f"anilist_{anime_id}.jpg"
        target_file_path = target_dir / filename
        
        # Cargar la imagen con Pillow
        img = Image.open(BytesIO(image_bytes))
        
        # Asegurar compatibilidad JPEG convirtiendo a RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Redimensionar conservando relación de aspecto (LANCZOS para calidad)
        max_width, max_height = 500, 750
        width, height = img.size
        
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
        # Guardar imagen optimizada
        img.save(target_file_path, "JPEG", quality=75, optimize=True)
        
        # Retornar ruta relativa para mayor portabilidad de la base de datos
        return str(target_file_path.relative_to(BASE_DIR))
        
    except Exception:
        # Retornar la portada de marcador de posición en caso de error
        return generate_placeholder_cover()

