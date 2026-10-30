import os
from reportlab.platypus import Image as RLImage, Paragraph, Table, TableStyle, Spacer, HRFlowable
from reportlab.lib import colors
from config.settings import BASE_DIR

def build_ficha_clasica(anime, styles, font_name):
    """
    Construye los flowables para una ficha clásica de anime (1 por página).
    """
    flowables = []
    
    # 1. Títulos
    title_style = styles["AnimeTitle"]
    subtitle_style = styles["AnimeSubtitle"]
    title_style.fontName = font_name
    subtitle_style.fontName = font_name
    
    flowables.append(Paragraph(anime["title"], title_style))
    if anime["title_original"] and anime["title_original"] != anime["title"]:
        flowables.append(Paragraph(anime["title_original"], subtitle_style))
    flowables.append(Spacer(1, 10))
    
    # 2. Portada e Información Técnica
    cover_path = os.path.join(BASE_DIR, anime["cover_local_path"]) if anime["cover_local_path"] else None
    if not cover_path or not os.path.exists(cover_path):
        from services.image_service import generate_placeholder_cover
        placeholder = generate_placeholder_cover()
        cover_path = os.path.join(BASE_DIR, placeholder)
        
    try:
        # Portada: Ancho 120, Alto 180 (Proporción 2:3 estándar)
        img_flowable = RLImage(cover_path, width=120, height=180)
    except Exception:
        img_flowable = Paragraph("[Imagen no disponible]", styles["Normal"])
        
    # Datos técnicos
    label_style = styles["InfoLabel"]
    value_style = styles["InfoValue"]
    label_style.fontName = font_name
    value_style.fontName = font_name
    
    genres = anime["genres_list"] or "No informado"
    studios = anime["studios_list"] or "No informado"
    score = f"{anime['score']}/10.0" if anime["score"] else "Sin puntuación"
    episodes = str(anime["episodes"]) if anime["episodes"] else "No informado"
    duration = f"{anime['duration_minutes']} min" if anime["duration_minutes"] else "No informado"
    
    tech_data = [
        [Paragraph("Año:", label_style), Paragraph(str(anime["release_year"] or "No disponible"), value_style)],
        [Paragraph("Formato:", label_style), Paragraph(str(anime["format"] or "No disponible"), value_style)],
        [Paragraph("Episodios:", label_style), Paragraph(episodes, value_style)],
        [Paragraph("Duración:", label_style), Paragraph(duration, value_style)],
        [Paragraph("Estado:", label_style), Paragraph(str(anime["status"] or "No disponible"), value_style)],
        [Paragraph("Temporada:", label_style), Paragraph(str(anime["season"] or "No disponible"), value_style)],
        [Paragraph("Estudios:", label_style), Paragraph(studios, value_style)],
        [Paragraph("Géneros:", label_style), Paragraph(genres, value_style)],
        [Paragraph("Puntuación:", label_style), Paragraph(score, value_style)],
    ]
    
    # 357 pt de ancho para los datos técnicos en A4
    tech_table = Table(tech_data, colWidths=[80, 277])
    tech_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    # Tabla contenedora superior (Imagen + Tabla técnica)
    container_data = [[img_flowable, tech_table]]
    # Anchos: Imagen (120) + Espacio (10) + Tech (357) = 487 pt (ancho útil A4)
    container_table = Table(container_data, colWidths=[130, 357])
    container_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    
    flowables.append(container_table)
    flowables.append(Spacer(1, 15))
    
    # 3. Sinopsis
    synopsis_title_style = styles["SynopsisTitle"]
    synopsis_text_style = styles["SynopsisText"]
    synopsis_title_style.fontName = font_name
    synopsis_text_style.fontName = font_name
    
    flowables.append(Paragraph("SINOPSIS", synopsis_title_style))
    flowables.append(Spacer(1, 4))
    
    synopsis_text = anime["synopsis"] or "Sinopsis no disponible."
    flowables.append(Paragraph(synopsis_text, synopsis_text_style))
    flowables.append(Spacer(1, 10))
    
    # 4. Línea de footer de la ficha
    flowables.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=10, spaceAfter=15))
    
    return flowables

def build_ficha_compacta_flowables(anime, styles, font_name):
    """
    Construye los flowables para una ficha compacta (se pueden colocar 2 por página).
    Usa fuentes e imágenes más pequeñas.
    """
    flowables = []
    
    # Títulos más pequeños
    title_style = styles["AnimeTitleCompact"]
    subtitle_style = styles["AnimeSubtitleCompact"]
    title_style.fontName = font_name
    subtitle_style.fontName = font_name
    
    flowables.append(Paragraph(anime["title"], title_style))
    if anime["title_original"] and anime["title_original"] != anime["title"]:
        flowables.append(Paragraph(anime["title_original"], subtitle_style))
    flowables.append(Spacer(1, 6))
    
    # Portada pequeña (90x135 px)
    cover_path = os.path.join(BASE_DIR, anime["cover_local_path"]) if anime["cover_local_path"] else None
    if not cover_path or not os.path.exists(cover_path):
        from services.image_service import generate_placeholder_cover
        placeholder = generate_placeholder_cover()
        cover_path = os.path.join(BASE_DIR, placeholder)
        
    try:
        img_flowable = RLImage(cover_path, width=90, height=135)
    except Exception:
        img_flowable = Paragraph("[Imagen]", styles["Normal"])
        
    # Datos técnicos compactos
    label_style = styles["InfoLabelCompact"]
    value_style = styles["InfoValueCompact"]
    label_style.fontName = font_name
    value_style.fontName = font_name
    
    genres = anime["genres_list"] or "No informado"
    studios = anime["studios_list"] or "No informado"
    score = f"{anime['score']}/10.0" if anime["score"] else "Sin puntuación"
    episodes = str(anime["episodes"]) if anime["episodes"] else "No informado"
    
    tech_data = [
        [Paragraph("Año:", label_style), Paragraph(str(anime["release_year"] or "No disponible"), value_style)],
        [Paragraph("Formato:", label_style), Paragraph(str(anime["format"] or "No disponible"), value_style)],
        [Paragraph("Episodios:", label_style), Paragraph(episodes, value_style)],
        [Paragraph("Estudios:", label_style), Paragraph(studios, value_style)],
        [Paragraph("Géneros:", label_style), Paragraph(genres, value_style)],
        [Paragraph("Puntuación:", label_style), Paragraph(score, value_style)],
    ]
    
    tech_table = Table(tech_data, colWidths=[65, 322])
    tech_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    container_data = [[img_flowable, tech_table]]
    container_table = Table(container_data, colWidths=[100, 387])
    container_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    
    flowables.append(container_table)
    flowables.append(Spacer(1, 8))
    
    # Sinopsis corta
    synopsis_title_style = styles["SynopsisTitleCompact"]
    synopsis_text_style = styles["SynopsisTextCompact"]
    synopsis_title_style.fontName = font_name
    synopsis_text_style.fontName = font_name
    
    flowables.append(Paragraph("SINOPSIS", synopsis_title_style))
    flowables.append(Spacer(1, 2))
    
    synopsis_text = anime["synopsis"] or "Sinopsis no disponible."
    # Truncar sinopsis si es demasiado larga para evitar desbordes en diseño de 2 por página
    if len(synopsis_text) > 350:
        synopsis_text = synopsis_text[:347] + "..."
        
    flowables.append(Paragraph(synopsis_text, synopsis_text_style))
    flowables.append(Spacer(1, 10))
    
    # Línea divisoria
    flowables.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=5, spaceAfter=15))
    
    return flowables
