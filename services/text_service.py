import html
import re

def clean_html(text: str) -> str:
    """
    Limpia etiquetas HTML y entidades HTML de un texto (como sinopsis).
    Reduce espacios múltiples y normaliza saltos de línea.
    """
    if not text:
        return ""
    
    # Desconvertir entidades HTML (ej: &quot; -> ", &lt; -> <)
    text = html.unescape(text)
    
    # Eliminar todas las etiquetas HTML (como <br>, <i>, <b>, etc.)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Reemplazar múltiples espacios en la misma línea por uno solo
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Limpiar saltos de línea repetidos (permitir máximo 2 consecutivos para separar párrafos)
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()
