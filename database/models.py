def initialize_database(conn):
    """
    Inicializa las tablas de la base de datos y crea los índices 
    necesarios para búsquedas y paginación eficientes.
    """
    cursor = conn.cursor()

    # Tabla principal: anime
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anime (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider VARCHAR(50) NOT NULL,
        external_id VARCHAR(100) NOT NULL,
        title VARCHAR(500) NOT NULL,
        title_original VARCHAR(500),
        title_english VARCHAR(500),
        title_romaji VARCHAR(500),
        title_native VARCHAR(500),
        release_year INTEGER,
        release_date VARCHAR(20),
        format VARCHAR(50),
        episodes INTEGER,
        duration_minutes INTEGER,
        status VARCHAR(100),
        season VARCHAR(50),
        synopsis TEXT,
        synopsis_es TEXT,
        cover_url TEXT,
        cover_local_path TEXT,
        banner_url TEXT,
        rating VARCHAR(50),
        is_adult BOOLEAN DEFAULT 0,
        score REAL,
        source_url TEXT,
        created_at DATETIME,
        updated_at DATETIME,
        last_synced_at DATETIME,
        UNIQUE(provider, external_id)
    );
    """)

    # Tabla: genres
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(150) UNIQUE NOT NULL
    );
    """)

    # Relación: anime-géneros (M:N)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anime_genres (
        anime_id INTEGER NOT NULL,
        genre_id INTEGER NOT NULL,
        PRIMARY KEY (anime_id, genre_id),
        FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
        FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
    );
    """)

    # Tabla: studios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS studios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(250) UNIQUE NOT NULL
    );
    """)

    # Relación: anime-estudios (M:N)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anime_studios (
        anime_id INTEGER NOT NULL,
        studio_id INTEGER NOT NULL,
        PRIMARY KEY (anime_id, studio_id),
        FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
        FOREIGN KEY (studio_id) REFERENCES studios(id) ON DELETE CASCADE
    );
    """)

    # Registro de sincronizaciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sync_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider VARCHAR(50),
        started_at DATETIME,
        finished_at DATETIME,
        page_start INTEGER,
        page_end INTEGER,
        records_processed INTEGER,
        records_created INTEGER,
        records_updated INTEGER,
        errors INTEGER,
        status VARCHAR(50),
        message TEXT
    );
    """)

    # Registro de errores detallados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS error_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        process VARCHAR(100),
        external_id VARCHAR(100),
        error_type VARCHAR(100),
        message TEXT,
        created_at DATETIME
    );
    """)

    # Índices optimizados para ordenamiento e índices del PDF
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_anime_year_title ON anime(release_year, title);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_anime_format ON anime(format);")

    conn.commit()
