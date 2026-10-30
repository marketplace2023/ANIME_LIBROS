import datetime
import sqlite3

def upsert_anime(conn, data):
    """
    Inserta o actualiza un registro de anime en la base de datos.
    Retorna el ID interno del registro.
    """
    cursor = conn.cursor()
    
    # Manejar timestamps automáticos
    now = datetime.datetime.now().isoformat()
    if 'created_at' not in data or not data['created_at']:
        data['created_at'] = now
    data['updated_at'] = now
    data['last_synced_at'] = now

    query = """
    INSERT INTO anime (
        provider, external_id, title, title_original, title_english, title_romaji, title_native,
        release_year, release_date, format, episodes, duration_minutes, status, season,
        synopsis, synopsis_es, cover_url, cover_local_path, banner_url, rating, is_adult,
        score, source_url, created_at, updated_at, last_synced_at
    ) VALUES (
        :provider, :external_id, :title, :title_original, :title_english, :title_romaji, :title_native,
        :release_year, :release_date, :format, :episodes, :duration_minutes, :status, :season,
        :synopsis, :synopsis_es, :cover_url, :cover_local_path, :banner_url, :rating, :is_adult,
        :score, :source_url, :created_at, :updated_at, :last_synced_at
    )
    ON CONFLICT(provider, external_id) DO UPDATE SET
        title = excluded.title,
        title_original = excluded.title_original,
        title_english = excluded.title_english,
        title_romaji = excluded.title_romaji,
        title_native = excluded.title_native,
        release_year = excluded.release_year,
        release_date = excluded.release_date,
        format = excluded.format,
        episodes = excluded.episodes,
        duration_minutes = excluded.duration_minutes,
        status = excluded.status,
        season = excluded.season,
        synopsis = excluded.synopsis,
        cover_url = excluded.cover_url,
        banner_url = excluded.banner_url,
        rating = excluded.rating,
        is_adult = excluded.is_adult,
        score = excluded.score,
        source_url = excluded.source_url,
        updated_at = excluded.updated_at,
        last_synced_at = excluded.last_synced_at
    RETURNING id;
    """
    
    try:
        cursor.execute(query, data)
        row = cursor.fetchone()
        if row:
            return row[0]
    except sqlite3.Error as e:
        # Fallback si RETURNING no es soportado en versiones muy antiguas de sqlite3
        cursor.execute(
            "SELECT id FROM anime WHERE provider = ? AND external_id = ?",
            (data['provider'], data['external_id'])
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        raise e

def associate_genre(conn, anime_id, genre_name):
    """Asocia un género a un anime, insertando el género si no existe."""
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (genre_name,))
    cursor.execute("SELECT id FROM genres WHERE name = ?", (genre_name,))
    genre_row = cursor.fetchone()
    if genre_row:
        genre_id = genre_row[0]
        cursor.execute(
            "INSERT OR IGNORE INTO anime_genres (anime_id, genre_id) VALUES (?, ?)",
            (anime_id, genre_id)
        )

def associate_studio(conn, anime_id, studio_name):
    """Asocia un estudio a un anime, insertando el estudio si no existe."""
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO studios (name) VALUES (?)", (studio_name,))
    cursor.execute("SELECT id FROM studios WHERE name = ?", (studio_name,))
    studio_row = cursor.fetchone()
    if studio_row:
        studio_id = studio_row[0]
        cursor.execute(
            "INSERT OR IGNORE INTO anime_studios (anime_id, studio_id) VALUES (?, ?)",
            (anime_id, studio_id)
        )

def clear_anime_genres_and_studios(conn, anime_id):
    """Limpia las relaciones previas de un anime antes de re-asociar."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM anime_genres WHERE anime_id = ?", (anime_id,))
    cursor.execute("DELETE FROM anime_studios WHERE anime_id = ?", (anime_id,))

def get_anime_for_pdf(conn, filters=None):
    """
    Retorna registros de anime optimizados y filtrados para la generación de PDF.
    Une géneros y estudios usando GROUP_CONCAT para eficiencia.
    """
    cursor = conn.cursor()
    
    query = """
    SELECT a.*, 
           (SELECT GROUP_CONCAT(g.name, ', ') 
            FROM anime_genres ag 
            JOIN genres g ON ag.genre_id = g.id 
            WHERE ag.anime_id = a.id) as genres_list,
           (SELECT GROUP_CONCAT(s.name, ', ') 
            FROM anime_studios ast 
            JOIN studios s ON ast.studio_id = s.id 
            WHERE ast.anime_id = a.id) as studios_list
    FROM anime a
    WHERE 1=1
    """
    
    params = []
    
    if filters:
        if 'format' in filters and filters['format']:
            # Soportar múltiples formatos separados por coma (ej: "TV,MOVIE,ONA")
            formats = [f.strip().upper() for f in str(filters['format']).split(',') if f.strip()]
            if len(formats) == 1:
                query += " AND a.format = ?"
                params.append(formats[0])
            elif len(formats) > 1:
                placeholders = ','.join('?' * len(formats))
                query += f" AND a.format IN ({placeholders})"
                params.extend(formats)
            
        if 'year_from' in filters and filters['year_from']:
            query += " AND a.release_year >= ?"
            params.append(int(filters['year_from']))
            
        if 'year_to' in filters and filters['year_to']:
            query += " AND a.release_year <= ?"
            params.append(int(filters['year_to']))
            
        if 'include_adult' in filters and not filters['include_adult']:
            query += " AND a.is_adult = 0"
            
        if 'has_cover' in filters and filters['has_cover']:
            query += " AND a.cover_local_path IS NOT NULL"

    # Ordenar por año de estreno y título para un índice coherente
    query += " ORDER BY a.release_year DESC, a.title ASC"
    
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

def log_sync(conn, provider, started_at, finished_at, page_start, page_end, processed, created, updated, errors, status, message=None):
    """Registra una ejecución de sincronización."""
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sync_logs (
        provider, started_at, finished_at, page_start, page_end, 
        records_processed, records_created, records_updated, errors, status, message
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (provider, started_at, finished_at, page_start, page_end, processed, created, updated, errors, status, message))
    conn.commit()

def log_error(conn, process, external_id, error_type, message):
    """Registra un error detallado durante cualquier proceso."""
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO error_logs (process, external_id, error_type, message, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (process, external_id, error_type, message, now))
    conn.commit()

def get_last_processed_page(conn, provider):
    """Determina la última página procesada con éxito a partir de los logs."""
    cursor = conn.cursor()
    cursor.execute("""
    SELECT page_end FROM sync_logs 
    WHERE provider = ? AND status = 'SUCCESS' 
    ORDER BY finished_at DESC LIMIT 1
    """, (provider,))
    row = cursor.fetchone()
    return row[0] if row else 0
