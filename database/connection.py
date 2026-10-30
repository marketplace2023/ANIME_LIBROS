import sqlite3
from config.settings import DB_FILE_PATH

def get_connection():
    """
    Retorna una conexión a la base de datos SQLite con soporte para 
    llaves foráneas y mapeo de filas a diccionarios.
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn
