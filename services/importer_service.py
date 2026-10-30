import datetime
import time
from tqdm import tqdm
from config.settings import (
    REQUEST_DELAY_SECONDS, MAX_RETRIES, RETRY_DELAY_SECONDS,
    DOWNLOAD_COVERS, INCLUDE_ADULT_CONTENT
)
from database.connection import get_connection
from database.repositories import (
    upsert_anime, associate_genre, associate_studio,
    clear_anime_genres_and_studios, log_sync, log_error, get_last_processed_page
)
from providers.anilist_provider import AniListProvider
from services.text_service import clean_html
from services.image_service import download_and_optimize_cover

def run_import(limit: int = None, start_page: int = None):
    """
    Orquesta el proceso de importación desde AniList a la base de datos SQLite.
    Soporta reintentos, límites, reanudación y descarga optimizada de portadas.
    """
    provider = AniListProvider()
    conn = get_connection()
    
    # Determinar página de inicio si no se especifica
    if start_page is None:
        start_page = get_last_processed_page(conn, "ANILIST") + 1
        
    started_at = datetime.datetime.now().isoformat()
    current_page = start_page
    records_processed = 0
    records_created = 0
    records_updated = 0
    total_errors = 0
    
    print(f"\nIniciando importación desde AniList.")
    print(f"-> Página inicial: {current_page}")
    print(f"-> Límite: {limit if limit is not None else 'Completo (Sin límite)'}")
    print(f"-> Descargar portadas: {'Sí' if DOWNLOAD_COVERS else 'No'}")
    print(f"-> Incluir contenido adulto: {'Sí' if INCLUDE_ADULT_CONTENT else 'No'}\n")
    
    # Configuración de barra de progreso tqdm
    pbar = tqdm(total=limit, desc="Importando anime", unit="reg") if limit else None
    
    try:
        has_next_page = True
        while has_next_page:
            # Reintentos con exponencial backoff para obtener la página
            page_data = None
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    page_data = provider.fetch_page(current_page, per_page=50)
                    break
                except Exception as e:
                    retries += 1
                    total_errors += 1
                    log_error(conn, "API_FETCH", f"page_{current_page}", type(e).__name__, str(e))
                    if retries >= MAX_RETRIES:
                        print(f"\n[ERROR] Fallaron todos los reintentos para la página {current_page}. Abortando importación.")
                        raise e
                    sleep_time = RETRY_DELAY_SECONDS * (2 ** (retries - 1))
                    print(f"\n[WARN] Error al obtener página {current_page}. Reintento {retries}/{MAX_RETRIES} en {sleep_time}s...")
                    time.sleep(sleep_time)
            
            if not page_data or not page_data.get("records"):
                print(f"\nNo se encontraron más registros en la página {current_page}.")
                break
                
            records = page_data["records"]
            page_info = page_data["page_info"]
            
            for rec in records:
                # Filtrar contenido adulto si está desactivado en la configuración
                if not INCLUDE_ADULT_CONTENT and rec["is_adult"]:
                    continue
                    
                # Limpiar sinopsis
                rec["synopsis"] = clean_html(rec["synopsis"])
                
                # Descargar e integrar portada si está habilitado
                if DOWNLOAD_COVERS and rec["cover_url"]:
                    cover_local = download_and_optimize_cover(
                        rec["external_id"], rec["cover_url"], rec["release_year"]
                    )
                    if cover_local:
                        rec["cover_local_path"] = cover_local
                    else:
                        total_errors += 1
                        log_error(
                            conn, "COVER_DOWNLOAD", rec["external_id"], 
                            "DownloadError", f"Fallo al descargar u optimizar {rec['cover_url']}"
                        )
                
                # Guardar el anime en la base de datos
                try:
                    anime_id = upsert_anime(conn, rec)
                    
                    # Actualizar géneros y estudios (limpiar viejas asociaciones e insertar nuevas)
                    clear_anime_genres_and_studios(conn, anime_id)
                    for genre in rec["genres"]:
                        associate_genre(conn, anime_id, genre)
                    for studio in rec["studios"]:
                        associate_studio(conn, anime_id, studio)
                        
                    records_created += 1
                except Exception as db_err:
                    total_errors += 1
                    log_error(conn, "DATABASE_UPSERT", rec["external_id"], type(db_err).__name__, str(db_err))
                    continue
                    
                records_processed += 1
                if pbar:
                    pbar.update(1)
                
                # Detener la importación si alcanzamos el límite deseado
                if limit and records_processed >= limit:
                    has_next_page = False
                    break
            
            # Confirmar los cambios por página para evitar pérdidas en fallos repentinos
            conn.commit()
            
            # Validar si hay más páginas disponibles en la API
            if not page_info["has_next_page"]:
                has_next_page = False
                
            if has_next_page:
                current_page += 1
                # Esperar el delay establecido entre peticiones para respetar los rate limits de AniList
                time.sleep(REQUEST_DELAY_SECONDS)
                
        finished_at = datetime.datetime.now().isoformat()
        log_sync(
            conn, "ANILIST", started_at, finished_at, start_page, current_page,
            records_processed, records_created, records_updated, total_errors, "SUCCESS",
            f"Importación exitosa de {records_processed} registros."
        )
        print(f"\n[OK] Sincronización completada con éxito.")
        print(f" -> Páginas procesadas: {start_page} a {current_page}")
        print(f" -> Registros guardados: {records_processed}")
        print(f" -> Errores registrados: {total_errors}")
        
    except Exception as fatal_err:
        finished_at = datetime.datetime.now().isoformat()
        log_sync(
            conn, "ANILIST", started_at, finished_at, start_page, current_page,
            records_processed, records_created, records_updated, total_errors, "FAILED",
            str(fatal_err)
        )
        print(f"\n[FATAL] La importación falló debido a un error crítico: {fatal_err}")
    finally:
        if pbar:
            pbar.close()
        conn.close()
