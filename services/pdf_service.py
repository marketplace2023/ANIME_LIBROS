import datetime
from pathlib import Path
import httpx
from reportlab.lib import colors, pagesizes
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, PageBreak, KeepTogether, Spacer, Paragraph
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config.settings import (
    BASE_DIR, EXPORT_DIR_PATH, MAX_RECORDS_PER_VOLUME,
    PDF_CARD_LAYOUT, INCLUDE_ADULT_CONTENT
)
from database.connection import get_connection
from database.repositories import get_anime_for_pdf
from templates.ficha_compacta import build_ficha_clasica, build_ficha_compacta_flowables

FONT_DIR = BASE_DIR / "storage" / "cache" / "fonts"
FONT_PATH = FONT_DIR / "ipag.ttf"
FONT_URL = "https://raw.githubusercontent.com/hyoshiok/ttf-ipafont/master/ipag.ttf"

def setup_unicode_font() -> str:
    """
    Descarga y registra la fuente IPAGothic para soportar caracteres japoneses en el PDF.
    Si falla, retorna 'Helvetica' como fallback seguro.
    """
    if not FONT_PATH.exists():
        try:
            print("\nDescargando fuente IPAGothic para soporte de caracteres japoneses...")
            print("Esto podría tardar unos segundos...")
            FONT_DIR.mkdir(parents=True, exist_ok=True)
            with httpx.Client() as client:
                response = client.get(FONT_URL, timeout=45.0, follow_redirects=True)
                response.raise_for_status()
                FONT_PATH.write_bytes(response.content)
            print("[OK] Fuente Unicode descargada e instalada con éxito.\n")
        except Exception as e:
            print(f"\n[WARN] No se pudo descargar la fuente IPAGothic. Se usará la estándar. Detalle: {e}\n")
            return "Helvetica"
            
    try:
        pdfmetrics.registerFont(TTFont("IPAGothic", str(FONT_PATH)))
        return "IPAGothic"
    except Exception as e:
        print(f"\n[WARN] Falló el registro de la fuente descargada: {e}. Fallback a Helvetica.\n")
        return "Helvetica"

class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado para calcular y dibujar la numeración total de páginas
    y añadir decoraciones de cabecera y pie de página en dos pasadas.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Omitir decoraciones en la portada (página 1)
        if self._pageNumber == 1:
            return
            
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569")) # Slate 600
        
        # Cabecera (A4 es 595 x 842 pt)
        self.drawString(54, 800, "CATÁLOGO PERSONAL DE ANIME")
        self.setStrokeColor(colors.HexColor("#CBD5E1")) # Slate 200
        self.setLineWidth(0.5)
        self.line(54, 792, 541, 792)
        
        # Pie de página
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(541, 35, page_text)
        self.drawString(54, 35, "Generado por Catálogo Anime PDF | Fuente: AniList API")
        self.line(54, 47, 541, 47)
        self.restoreState()

def get_custom_styles():
    """Genera las hojas de estilos personalizadas para ReportLab."""
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#1E293B")   # Slate 800 (Títulos)
    secondary_color = colors.HexColor("#475569") # Slate 600 (Meta)
    accent_color = colors.HexColor("#2563EB")    # Blue 600 (Subsección)
    text_color = colors.HexColor("#0F172A")      # Slate 900 (Contenido)
    
    # Estilo del Título Ficha Clásica
    styles.add(ParagraphStyle(
        name="AnimeTitle",
        parent=styles["Normal"],
        fontSize=16,
        leading=19,
        textColor=primary_color,
        fontName="Helvetica-Bold",
        spaceAfter=2
    ))
    
    styles.add(ParagraphStyle(
        name="AnimeSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=13,
        textColor=secondary_color,
        fontName="Helvetica-Oblique",
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        name="InfoLabel",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=secondary_color,
        fontName="Helvetica-Bold"
    ))
    
    styles.add(ParagraphStyle(
        name="InfoValue",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=text_color,
        fontName="Helvetica"
    ))
    
    styles.add(ParagraphStyle(
        name="SynopsisTitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        textColor=accent_color,
        fontName="Helvetica-Bold",
        spaceBefore=5,
        spaceAfter=2
    ))
    
    styles.add(ParagraphStyle(
        name="SynopsisText",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=secondary_color,
        fontName="Helvetica",
        alignment=TA_JUSTIFY
    ))
    
    # Estilos Compactos (2 por página)
    styles.add(ParagraphStyle(
        name="AnimeTitleCompact",
        parent=styles["Normal"],
        fontSize=12,
        leading=14,
        textColor=primary_color,
        fontName="Helvetica-Bold",
        spaceAfter=1
    ))
    
    styles.add(ParagraphStyle(
        name="AnimeSubtitleCompact",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=secondary_color,
        fontName="Helvetica-Oblique",
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name="InfoLabelCompact",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=secondary_color,
        fontName="Helvetica-Bold"
    ))
    
    styles.add(ParagraphStyle(
        name="InfoValueCompact",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=text_color,
        fontName="Helvetica"
    ))
    
    styles.add(ParagraphStyle(
        name="SynopsisTitleCompact",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=accent_color,
        fontName="Helvetica-Bold",
        spaceBefore=3,
        spaceAfter=1
    ))
    
    styles.add(ParagraphStyle(
        name="SynopsisTextCompact",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=secondary_color,
        fontName="Helvetica",
        alignment=TA_JUSTIFY
    ))
    
    # Estilos de la Portada
    styles.add(ParagraphStyle(
        name="CoverTitle",
        parent=styles["Normal"],
        fontSize=26,
        leading=32,
        textColor=primary_color,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=15
    ))
    
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        parent=styles["Normal"],
        fontSize=14,
        leading=18,
        textColor=accent_color,
        fontName="Helvetica",
        alignment=TA_CENTER,
        spaceAfter=50
    ))
    
    styles.add(ParagraphStyle(
        name="CoverMeta",
        parent=styles["Normal"],
        fontSize=10,
        leading=16,
        textColor=secondary_color,
        fontName="Helvetica",
        alignment=TA_CENTER
    ))
    
    return styles

def build_cover_page_story(volume_num: int, records_count: int, styles, font_name: str) -> list:
    """Genera la estructura de la página de portada del tomo."""
    story = []
    story.append(Spacer(1, 150))
    
    title_style = styles["CoverTitle"]
    subtitle_style = styles["CoverSubtitle"]
    meta_style = styles["CoverMeta"]
    
    title_style.fontName = font_name
    subtitle_style.fontName = font_name
    meta_style.fontName = font_name
    
    story.append(Paragraph("CATÁLOGO PERSONAL DE ANIME", title_style))
    story.append(Paragraph(f"VOLUMEN {volume_num:03d}", subtitle_style))
    
    story.append(Spacer(1, 100))
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d")
    story.append(Paragraph(f"<b>Cantidad de registros:</b> {records_count}", meta_style))
    story.append(Paragraph(f"<b>Fecha de generación:</b> {now_str}", meta_style))
    story.append(Paragraph("<b>Fuente de datos:</b> AniList API", meta_style))
    story.append(Paragraph("<b>Formato:</b> PDF Portable", meta_style))
    
    story.append(PageBreak())
    return story

def generate_pdf(filters=None) -> list:
    """
    Lee los registros guardados en SQLite, aplica los filtros y genera
    los volúmenes de catálogo PDF requeridos en storage/exports/.
    
    Retorna la lista de archivos PDF generados.
    """
    conn = get_connection()
    
    # Aplicar filtro por defecto de contenido adulto según config
    if filters is None:
        filters = {}
    if 'include_adult' not in filters:
        filters['include_adult'] = INCLUDE_ADULT_CONTENT
        
    records = get_anime_for_pdf(conn, filters)
    conn.close()
    
    if not records:
        print("[WARN] No se encontraron registros de anime en la base de datos para generar el PDF.")
        return []
        
    # Inicializar la fuente Unicode (Japonesa)
    font_name = setup_unicode_font()
    styles = get_custom_styles()
    
    # Asegurar que el directorio de salida exista
    EXPORT_DIR_PATH.mkdir(parents=True, exist_ok=True)
    
    # Dividir registros por volúmenes
    records_chunks = [
        records[i:i + MAX_RECORDS_PER_VOLUME] 
        for i in range(0, len(records), MAX_RECORDS_PER_VOLUME)
    ]
    
    generated_files = []
    
    for idx, chunk in enumerate(records_chunks):
        volume_num = idx + 1
        output_file_name = f"Anime_Catalogo_Volumen_{volume_num:03d}.pdf"
        output_file_path = EXPORT_DIR_PATH / output_file_name
        
        print(f"Generando {output_file_name} con {len(chunk)} registros...")
        
        # Documento base
        doc = SimpleDocTemplate(
            str(output_file_path),
            pagesize=pagesizes.A4,
            leftMargin=54,
            rightMargin=54,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # 1. Añadir portada
        story.extend(build_cover_page_story(volume_num, len(chunk), styles, font_name))
        
        # 2. Añadir fichas
        layout = PDF_CARD_LAYOUT.upper()
        
        for anime in chunk:
            if layout == "CLASSIC":
                # Ficha clásica: una por página
                card_flowables = build_ficha_clasica(anime, styles, font_name)
                story.extend(card_flowables)
                story.append(PageBreak())
            else:
                # Ficha compacta: dos por página (KeepTogether previene que se rompa una ficha a la mitad)
                card_flowables = build_ficha_compacta_flowables(anime, styles, font_name)
                story.append(KeepTogether(card_flowables))
                story.append(Spacer(1, 10))
                
        # Construir archivo PDF
        doc.build(story, canvasmaker=NumberedCanvas)
        generated_files.append(str(output_file_path))
        
    print(f"\n[OK] Generación de PDF finalizada. Archivos creados: {len(generated_files)}")
    for file in generated_files:
        print(f" -> {Path(file).name}")
        
    return generated_files
