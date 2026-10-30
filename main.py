import argparse
import sys
import os

from database.connection import get_connection
from database.models import initialize_database

def print_statistics():
    """Muestra estadísticas agregadas sobre los registros locales en SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM anime")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM anime WHERE cover_local_path IS NOT NULL")
        covers = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(release_year), MAX(release_year) FROM anime")
        min_year, max_year = cursor.fetchone()
        
        cursor.execute("SELECT format, COUNT(*) FROM anime GROUP BY format ORDER BY COUNT(*) DESC")
        formats = cursor.fetchall()
        
        print("\n================================================")
        print("           ESTADÍSTICAS DEL CATÁLOGO")
        print("================================================")
        print(f"Total de registros de anime: {total}")
        print(f"Portadas locales optimizadas: {covers}")
        print(f"Rango de años registrados:    {min_year or 'N/A'} - {max_year or 'N/A'}")
        print("\nDistribución por formato:")
        for f in formats:
            fmt_name = f[0] or "Desconocido"
            print(f" -> {fmt_name}: {f[1]} registros")
        print("================================================\n")
    except Exception as e:
        print(f"\n[ERROR] No se pudieron leer las estadísticas (¿Base de datos inicializada?): {e}\n")
    finally:
        conn.close()

def interactive_menu():
    """Menú interactivo de consola para facilitar el uso del sistema."""
    # Asegurar inicialización de base de datos
    conn = get_connection()
    initialize_database(conn)
    conn.close()
    
    while True:
        print("================================================")
        print("          CATÁLOGO PERSONAL DE ANIME")
        print("================================================")
        print("1. Descargar catálogo (Prueba 100 registros)")
        print("2. Descargar catálogo completo (Sin límite)")
        print("3. Generar PDF (Layout Compacto - 2 por página)")
        print("4. Generar PDF (Layout Clásico - 1 por página)")
        print("5. Ver estadísticas locales")
        print("0. Salir")
        print("================================================")
        
        try:
            choice = input("Selecciona una opción: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n¡Hasta pronto!")
            break
            
        if choice == "1":
            from services.importer_service import run_import
            run_import(limit=100)
        elif choice == "2":
            from services.importer_service import run_import
            run_import()
        elif choice == "3":
            import config.settings as settings
            settings.PDF_CARD_LAYOUT = "COMPACT"
            from services.pdf_service import generate_pdf
            generate_pdf()
        elif choice == "4":
            import config.settings as settings
            settings.PDF_CARD_LAYOUT = "CLASSIC"
            from services.pdf_service import generate_pdf
            generate_pdf()
        elif choice == "5":
            print_statistics()
        elif choice == "0":
            print("¡Hasta pronto!")
            break
        else:
            print("Opción inválida. Intenta nuevamente.\n")

def main():
    parser = argparse.ArgumentParser(description="Gestor de catálogo personal de anime en PDF")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando de Importación
    import_parser = subparsers.add_parser("import", help="Importar registros desde AniList")
    import_parser.add_argument("--limit", type=int, default=None, help="Límite máximo de registros a importar")
    import_parser.add_argument("--page", type=int, default=None, help="Página inicial de consulta")
    
    # Comando de PDF
    pdf_parser = subparsers.add_parser("generate-pdf", help="Generar tomos PDF del catálogo")
    pdf_parser.add_argument("--format", type=str, default=None, help="Filtrar por formato. Acepta uno o varios separados por coma (ej: TV  o  TV,MOVIE,ONA)")
    pdf_parser.add_argument("--year-from", type=int, default=None, help="Filtrar desde el año especificado")
    pdf_parser.add_argument("--year-to", type=int, default=None, help="Filtrar hasta el año especificado")
    pdf_parser.add_argument("--layout", type=str, choices=["CLASSIC", "COMPACT"], default=None, help="Diseño de fichas")
    
    # Comando de Estadísticas
    subparsers.add_parser("stats", help="Mostrar estadísticas de la base de datos local")
    
    # Parsing de argumentos
    args = parser.parse_args()
    
    if args.command is None:
        # Ejecutar menú interactivo si no hay argumentos
        interactive_menu()
    else:
        # Asegurar inicialización de la BD
        conn = get_connection()
        initialize_database(conn)
        conn.close()
        
        if args.command == "import":
            from services.importer_service import run_import
            run_import(limit=args.limit, start_page=args.page)
        elif args.command == "generate-pdf":
            import config.settings as settings
            if args.layout:
                settings.PDF_CARD_LAYOUT = args.layout
            
            filters = {}
            if args.format:
                filters["format"] = args.format.upper()
            if args.year_from:
                filters["year_from"] = args.year_from
            if args.year_to:
                filters["year_to"] = args.year_to
                
            from services.pdf_service import generate_pdf
            generate_pdf(filters=filters)
        elif args.command == "stats":
            print_statistics()

if __name__ == "__main__":
    main()
