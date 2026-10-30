# PLAN DE DESARROLLO POR FASES  
## Catálogo personal de anime en PDF mediante API

---

## 1. Descripción general del proyecto

El proyecto consiste en desarrollar una aplicación local capaz de consultar una API de anime, descargar los registros disponibles y generar uno o varios archivos PDF con fichas individuales.

Cada ficha podrá contener:

- Nombre principal del anime.
- Título original o japonés.
- Año de estreno.
- Sinopsis.
- Imagen de portada.
- Tipo de producción.
- Cantidad de episodios.
- Estado.
- Géneros.
- Estudio de animación.
- Fuente de los datos.
- Fecha de actualización.

El sistema estará orientado a uso personal y funcionará como un generador automático de catálogo.

---

## 2. Objetivo general

Desarrollar una aplicación que permita descargar información de anime desde una API, almacenarla localmente, procesar las imágenes de portada y generar catálogos PDF organizados por año, década, tipo o cantidad de registros.

---

## 3. Objetivos específicos

1. Seleccionar una API de anime.
2. Diseñar una base de datos local.
3. Descargar todos los registros disponibles.
4. Evitar duplicados.
5. Descargar y optimizar las imágenes.
6. Limpiar las sinopsis.
7. Organizar los animes por categorías.
8. Generar fichas visuales.
9. Crear archivos PDF por volúmenes.
10. Permitir futuras actualizaciones del catálogo.
11. Generar un índice general.
12. Registrar errores y elementos incompletos.

---

## 4. Alcance inicial

La primera versión incluirá:

- Aplicación local.
- Consulta automática de API.
- Base de datos SQLite.
- Descarga de portadas.
- Generación de PDF.
- División del catálogo en volúmenes.
- Filtro por tipo.
- Filtro por año.
- Exclusión opcional de contenido adulto.
- Registro de errores.
- Actualización incremental.

La primera versión no requiere:

- Plataforma web.
- Registro de usuarios.
- Publicación pública.
- Venta de libros.
- Aplicación móvil.
- Sistema de pagos.
- Edición manual avanzada.

---

# FASE 0. DEFINICIÓN Y PREPARACIÓN

## Etapa 0.1. Definir el contenido de cada ficha

### Campos mínimos

```text
Nombre
Título original
Año
Sinopsis
Imagen de portada
```

### Campos recomendados

```text
Tipo
Episodios
Duración
Estado
Temporada
Géneros
Estudios
Clasificación
Fuente
Fecha de actualización
```

### Entregable

Documento con la lista definitiva de campos.

### Criterio de aceptación

Todos los campos que aparecerán en el PDF deben estar definidos antes de comenzar la programación.

---

## Etapa 0.2. Definir el alcance del catálogo

Seleccionar una de las siguientes modalidades:

### Modalidad A. Catálogo completo

Incluye:

- Series de televisión.
- Películas.
- OVA.
- ONA.
- Especiales.
- Cortos.
- Videos musicales.
- Producciones promocionales.

### Modalidad B. Solo series de televisión

Incluye únicamente registros clasificados como TV.

### Modalidad C. Catálogo personalizado

Permite seleccionar los formatos que serán incluidos.

### Recomendación

Desarrollar el sistema para soportar todas las modalidades mediante filtros.

---

## Etapa 0.3. Definir el idioma

Opciones:

- Conservar la sinopsis original de la API.
- Traducir automáticamente al español.
- Guardar sinopsis original y traducción.
- Utilizar “Sinopsis no disponible” cuando no exista descripción.

### Recomendación inicial

Conservar la sinopsis original y dejar preparada una columna para traducción al español.

---

## Etapa 0.4. Definir el formato de salida

Opciones:

- Un único PDF.
- PDF por década.
- PDF por año.
- PDF por tipo.
- PDF por bloques de 250 registros.
- PDF por bloques de 500 registros.
- PDF por bloques de 1.000 registros.

### Recomendación

Generar volúmenes de 500 registros y, adicionalmente, permitir división por década.

---

# FASE 1. SELECCIÓN DE LA FUENTE DE DATOS

## Etapa 1.1. Evaluar las APIs

Fuentes candidatas:

- AniList.
- Jikan.
- Kitsu.
- MyAnimeList API.
- Otra API compatible.

### Variables a evaluar

| Variable | Descripción |
|---|---|
| Cobertura | Cantidad de registros disponibles |
| Portadas | Calidad y disponibilidad |
| Sinopsis | Nivel de detalle |
| Idioma | Idioma predominante |
| Paginación | Facilidad para recorrer registros |
| Límites | Solicitudes permitidas |
| Autenticación | Necesidad de credenciales |
| Estabilidad | Continuidad del servicio |
| Licencia | Condiciones de uso |
| Campos | Datos disponibles por anime |

---

## Etapa 1.2. Definir la fuente principal

La aplicación debe utilizar una fuente principal configurable.

Ejemplo:

```env
ANIME_API_PROVIDER=ANILIST
```

También puede dejarse preparada una fuente secundaria para completar campos faltantes.

```env
ANIME_API_FALLBACK=JIKAN
```

---

## Etapa 1.3. Crear una capa de adaptación

La aplicación no debe depender directamente de la estructura de una sola API.

Se utilizará una interfaz común:

```python
class AnimeProvider:
    def get_page(self, page: int) -> list:
        pass

    def get_anime_detail(self, anime_id: int) -> dict:
        pass

    def get_total_pages(self) -> int:
        pass
```

### Entregable

Adaptador funcional para la API seleccionada.

### Criterio de aceptación

El sistema debe transformar la respuesta externa a un formato interno uniforme.

---

# FASE 2. DISEÑO DE LA ARQUITECTURA

## Etapa 2.1. Definir la tecnología

### Propuesta recomendada

```text
Python 3.12+
SQLite
httpx o requests
SQLAlchemy
Pillow
ReportLab
BeautifulSoup o html2text
tqdm
python-dotenv
```

### Justificación

Python permite:

- Consumir APIs.
- Descargar imágenes.
- Procesar textos.
- Manejar una base de datos local.
- Generar archivos PDF.
- Automatizar tareas por lotes.

---

## Etapa 2.2. Diseñar la estructura de carpetas

```text
anime-catalog-pdf/
│
├── README.md
├── requirements.txt
├── .env.example
├── main.py
│
├── config/
│   ├── settings.py
│   └── logging_config.py
│
├── providers/
│   ├── base_provider.py
│   ├── anilist_provider.py
│   ├── jikan_provider.py
│   └── kitsu_provider.py
│
├── database/
│   ├── connection.py
│   ├── models.py
│   ├── repositories.py
│   └── migrations/
│
├── services/
│   ├── importer_service.py
│   ├── image_service.py
│   ├── text_service.py
│   ├── deduplication_service.py
│   ├── catalog_service.py
│   └── pdf_service.py
│
├── templates/
│   ├── ficha_clasica.py
│   ├── ficha_compacta.py
│   └── portada_volumen.py
│
├── storage/
│   ├── database/
│   ├── covers/
│   ├── cache/
│   ├── logs/
│   └── exports/
│
├── tests/
│   ├── test_providers.py
│   ├── test_database.py
│   ├── test_images.py
│   └── test_pdf.py
│
└── scripts/
    ├── import_all.py
    ├── update_catalog.py
    ├── generate_pdf.py
    └── validate_data.py
```

---

## Etapa 2.3. Definir el flujo principal

```text
API
 │
 ▼
Proveedor de datos
 │
 ▼
Normalización
 │
 ▼
Validación
 │
 ▼
Base de datos SQLite
 │
 ├── Descarga de portadas
 ├── Limpieza de sinopsis
 ├── Eliminación de duplicados
 └── Clasificación
 │
 ▼
Generador de PDF
 │
 ▼
Volúmenes finales
```

---

# FASE 3. DISEÑO DE LA BASE DE DATOS

## Etapa 3.1. Tabla principal de anime

```sql
CREATE TABLE anime (
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
```

---

## Etapa 3.2. Tablas relacionadas

### Géneros

```sql
CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(150) UNIQUE NOT NULL
);
```

### Relación anime-género

```sql
CREATE TABLE anime_genres (
    anime_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    PRIMARY KEY (anime_id, genre_id)
);
```

### Estudios

```sql
CREATE TABLE studios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(250) UNIQUE NOT NULL
);
```

### Relación anime-estudio

```sql
CREATE TABLE anime_studios (
    anime_id INTEGER NOT NULL,
    studio_id INTEGER NOT NULL,
    PRIMARY KEY (anime_id, studio_id)
);
```

### Registro de sincronización

```sql
CREATE TABLE sync_logs (
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
```

### Registro de errores

```sql
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process VARCHAR(100),
    external_id VARCHAR(100),
    error_type VARCHAR(100),
    message TEXT,
    created_at DATETIME
);
```

---

## Etapa 3.3. Definir reglas de integridad

- No permitir duplicados por proveedor e identificador externo.
- No generar fichas sin título.
- Permitir registros sin año.
- Permitir registros sin sinopsis.
- Permitir registros sin portada.
- Guardar la URL original y la ruta local.
- Registrar la fecha de sincronización.
- No borrar automáticamente registros antiguos.

---

# FASE 4. DESARROLLO DEL IMPORTADOR

## Etapa 4.1. Implementar paginación

El importador debe:

1. Consultar una página.
2. Leer los registros.
3. Normalizar los campos.
4. Guardarlos en la base de datos.
5. Esperar el intervalo necesario.
6. Continuar con la siguiente página.
7. Registrar el progreso.
8. Reintentar errores temporales.

---

## Etapa 4.2. Controlar límites de solicitudes

Configurar:

```env
REQUEST_DELAY_SECONDS=1
MAX_RETRIES=5
RETRY_DELAY_SECONDS=10
REQUEST_TIMEOUT_SECONDS=30
```

El tiempo debe poder modificarse sin cambiar el código.

---

## Etapa 4.3. Implementar reintentos

Casos:

- Error de conexión.
- Tiempo de espera agotado.
- Error HTTP temporal.
- Límite de solicitudes.
- Respuesta incompleta.
- Error de decodificación.

### Estrategia

```text
Intento 1 → Esperar 10 segundos
Intento 2 → Esperar 20 segundos
Intento 3 → Esperar 40 segundos
Intento 4 → Esperar 80 segundos
Intento 5 → Registrar error y continuar
```

---

## Etapa 4.4. Guardar el progreso

El sistema debe poder continuar desde la última página procesada.

Ejemplo:

```json
{
  "provider": "ANILIST",
  "last_completed_page": 325,
  "last_external_id": "123456",
  "updated_at": "2026-07-14T12:00:00"
}
```

---

## Etapa 4.5. Ejecutar una prueba controlada

Primera prueba:

```text
Cantidad: 100 registros
Formato: TV
Portada: Sí
Sinopsis: Sí
Contenido adulto: No
```

### Criterio de aceptación

Los 100 registros deben almacenarse sin duplicados y con información legible.

---

# FASE 5. NORMALIZACIÓN Y LIMPIEZA DE DATOS

## Etapa 5.1. Normalizar títulos

Prioridad sugerida:

1. Título en español, cuando exista.
2. Título en inglés.
3. Título romaji.
4. Título nativo.
5. Primer título disponible.

---

## Etapa 5.2. Limpiar sinopsis

Operaciones:

- Eliminar etiquetas HTML.
- Convertir entidades HTML.
- Eliminar espacios repetidos.
- Eliminar saltos innecesarios.
- Limitar caracteres inválidos.
- Conservar párrafos.
- Evitar cortar palabras.

---

## Etapa 5.3. Manejar campos faltantes

Valores predeterminados:

```text
Año: No disponible
Sinopsis: Sinopsis no disponible
Portada: Imagen no disponible
Episodios: No informado
Estudio: No informado
Estado: No informado
```

---

## Etapa 5.4. Detectar duplicados

Criterios:

- Identificador externo.
- Título normalizado.
- Año.
- Formato.
- Número de episodios.

No deben fusionarse automáticamente:

- Temporadas diferentes.
- Remakes.
- Películas.
- OVA.
- Especiales.
- Versiones alternativas.

---

## Etapa 5.5. Clasificar registros

Clasificaciones sugeridas:

```text
Por década
Por año
Por tipo
Por género
Por estudio
Por estado
Por temporada
```

---

# FASE 6. DESCARGA Y PROCESAMIENTO DE PORTADAS

## Etapa 6.1. Crear la estructura de imágenes

```text
storage/covers/
│
├── 1900-1969/
├── 1970-1979/
├── 1980-1989/
├── 1990-1999/
├── 2000-2009/
├── 2010-2019/
├── 2020-2029/
└── unknown-year/
```

---

## Etapa 6.2. Definir nombres de archivos

Formato:

```text
{provider}_{external_id}_{slug}.jpg
```

Ejemplo:

```text
anilist_1_cowboy-bebop.jpg
```

---

## Etapa 6.3. Validar imágenes

El sistema debe comprobar:

- Código de respuesta válido.
- Tipo de contenido.
- Tamaño mínimo.
- Imagen corrupta.
- Formato compatible.
- Dimensiones.
- Orientación.

---

## Etapa 6.4. Optimizar portadas

Parámetros sugeridos:

```text
Formato: JPEG
Ancho máximo: 500 px
Alto máximo: 750 px
Calidad: 75 %
Modo: RGB
Peso objetivo: 50 KB a 150 KB
```

---

## Etapa 6.5. Imagen predeterminada

Crear una portada genérica con el texto:

```text
PORTADA NO DISPONIBLE
```

Se utilizará cuando:

- La API no tenga imagen.
- La descarga falle.
- El archivo esté corrupto.
- El formato no sea compatible.

---

# FASE 7. DISEÑO DE LAS FICHAS

## Etapa 7.1. Ficha clásica

Una ficha por página.

### Distribución

```text
┌───────────────────────────────────────────┐
│ TÍTULO                                    │
│ Título original                           │
├───────────────┬───────────────────────────┤
│               │ Año                       │
│   PORTADA     │ Tipo                      │
│               │ Episodios                 │
│               │ Estado                    │
│               │ Géneros                   │
│               │ Estudio                   │
├───────────────┴───────────────────────────┤
│ SINOPSIS                                  │
│                                           │
├───────────────────────────────────────────┤
│ Fuente | ID | Fecha de actualización      │
└───────────────────────────────────────────┘
```

---

## Etapa 7.2. Ficha compacta

Dos fichas por página.

Adecuada para reducir la cantidad total de páginas.

---

## Etapa 7.3. Ficha resumida

Cuatro fichas por página.

Contendrá:

- Portada pequeña.
- Título.
- Año.
- Tipo.
- Sinopsis corta.

---

## Etapa 7.4. Seleccionar diseño predeterminado

Recomendación:

- Ficha clásica para volúmenes especiales.
- Ficha compacta para el catálogo general.
- Ficha resumida para índices visuales.

---

## Etapa 7.5. Diseñar portada del volumen

Debe incluir:

```text
CATÁLOGO PERSONAL DE ANIME
Volumen XX
Periodo o rango
Cantidad de registros
Fecha de generación
Fuente de datos
```

---

# FASE 8. GENERACIÓN DE PDF

## Etapa 8.1. Crear el generador base

Funciones principales:

```python
create_cover_page()
create_table_of_contents()
create_anime_card()
create_page_number()
create_volume_footer()
generate_pdf()
```

---

## Etapa 8.2. Incluir metadatos del documento

```text
Título
Autor
Asunto
Palabras clave
Fecha de creación
Aplicación generadora
Versión del catálogo
```

---

## Etapa 8.3. Incorporar numeración

Formato:

```text
Página 0001 de 1250
```

---

## Etapa 8.4. Crear marcadores internos

Ejemplos:

```text
A
  Akira
  Another
B
  Bleach
  Blue Lock
C
  Cowboy Bebop
```

---

## Etapa 8.5. Crear índice general

El índice debe incluir:

| Campo | Descripción |
|---|---|
| Título | Nombre principal |
| Año | Año de estreno |
| Tipo | TV, película, OVA u otro |
| Volumen | Archivo donde se encuentra |
| Página | Número de página |

---

## Etapa 8.6. Dividir automáticamente los volúmenes

Configuración:

```env
MAX_RECORDS_PER_VOLUME=500
MAX_PAGES_PER_VOLUME=1200
MAX_FILE_SIZE_MB=500
```

Cuando se alcance uno de los límites, debe comenzar un nuevo volumen.

---

## Etapa 8.7. Nombre de los archivos

```text
Anime_Catalogo_Volumen_001.pdf
Anime_Catalogo_Volumen_002.pdf
Anime_Catalogo_Volumen_003.pdf
```

Por década:

```text
Anime_1917_1969.pdf
Anime_1970_1979.pdf
Anime_1980_1989.pdf
Anime_1990_1999.pdf
Anime_2000_2009.pdf
Anime_2010_2019.pdf
Anime_2020_2029.pdf
```

---

# FASE 9. FILTROS Y OPCIONES DE GENERACIÓN

## Etapa 9.1. Filtros básicos

```text
Tipo
Año inicial
Año final
Género
Estudio
Estado
Contenido adulto
Portada disponible
Sinopsis disponible
```

---

## Etapa 9.2. Opciones de línea de comandos

Ejemplo:

```bash
python main.py import
python main.py update
python main.py download-covers
python main.py validate
python main.py generate-pdf
```

Con filtros:

```bash
python main.py generate-pdf --format TV --year-from 1990 --year-to 1999
```

---

## Etapa 9.3. Menú interactivo

```text
================================================
        CATÁLOGO PERSONAL DE ANIME
================================================

1. Descargar catálogo completo
2. Actualizar registros
3. Descargar portadas pendientes
4. Validar base de datos
5. Generar PDF completo
6. Generar PDF por década
7. Generar PDF por tipo
8. Generar índice general
9. Ver estadísticas
0. Salir
```

---

# FASE 10. VALIDACIÓN Y CONTROL DE CALIDAD

## Etapa 10.1. Validar datos

Comprobar:

- Registros sin título.
- Registros duplicados.
- Años inválidos.
- Episodios negativos.
- Portadas faltantes.
- Rutas rotas.
- Sinopsis vacías.
- Identificadores repetidos.

---

## Etapa 10.2. Validar imágenes

Comprobar:

- Archivos dañados.
- Extensiones incorrectas.
- Imágenes demasiado grandes.
- Imágenes con dimensiones cero.
- Archivos duplicados.

---

## Etapa 10.3. Validar los PDF

Comprobar:

- Apertura correcta.
- Número de páginas.
- Marcadores.
- Índice.
- Portadas.
- Sinopsis.
- Saltos de página.
- Caracteres japoneses.
- Tamaño del archivo.
- Calidad de las imágenes.

---

## Etapa 10.4. Pruebas por volumen

Realizar pruebas con:

```text
10 registros
100 registros
500 registros
1.000 registros
Catálogo completo
```

---

## Etapa 10.5. Prueba de recuperación

Interrumpir intencionalmente:

- Importación.
- Descarga de portadas.
- Generación de PDF.

El sistema debe continuar desde el último punto válido.

---

# FASE 11. ACTUALIZACIÓN DEL CATÁLOGO

## Etapa 11.1. Actualización incremental

El sistema debe consultar:

- Nuevos registros.
- Cambios en registros existentes.
- Nuevas portadas.
- Sinopsis actualizadas.
- Cambios de estado.
- Cambios en episodios.

---

## Etapa 11.2. No volver a descargar todo

Antes de descargar una portada:

```text
¿Existe localmente?
    Sí → verificar integridad
    No → descargar
```

Antes de actualizar un registro:

```text
¿Cambió la fecha de actualización?
    Sí → actualizar
    No → omitir
```

---

## Etapa 11.3. Versionar los catálogos

Ejemplo:

```text
catalogo_anime_2026_07/
catalogo_anime_2026_10/
catalogo_anime_2027_01/
```

---

# FASE 12. DOCUMENTACIÓN DEL PROYECTO

## Etapa 12.1. README principal

Debe incluir:

- Descripción.
- Requisitos.
- Instalación.
- Configuración.
- Uso.
- Comandos.
- Estructura.
- Solución de errores.
- Actualización.
- Generación de PDF.

---

## Etapa 12.2. Archivo de configuración

Ejemplo:

```env
ANIME_API_PROVIDER=ANILIST
DATABASE_PATH=storage/database/anime.db
COVERS_PATH=storage/covers
EXPORT_PATH=storage/exports
REQUEST_DELAY_SECONDS=1
MAX_RETRIES=5
MAX_RECORDS_PER_VOLUME=500
PDF_CARD_LAYOUT=COMPACT
INCLUDE_ADULT_CONTENT=false
DOWNLOAD_COVERS=true
TRANSLATE_SYNOPSIS=false
```

---

## Etapa 12.3. Manual de operación

Debe explicar:

1. Cómo instalar Python.
2. Cómo crear el entorno virtual.
3. Cómo instalar dependencias.
4. Cómo configurar la API.
5. Cómo importar registros.
6. Cómo descargar portadas.
7. Cómo generar los PDF.
8. Cómo actualizar el catálogo.
9. Cómo restaurar una copia.
10. Cómo interpretar los registros de errores.

---

# FASE 13. RESPALDO Y CONSERVACIÓN

## Etapa 13.1. Archivos que deben respaldarse

```text
Base de datos SQLite
Portadas descargadas
Configuración
PDF generados
Índice general
Registros de sincronización
Registros de errores
```

---

## Etapa 13.2. Estructura de respaldo

```text
backups/
└── 2026-07-14/
    ├── anime.db
    ├── covers.zip
    ├── exports.zip
    ├── config.zip
    └── logs.zip
```

---

## Etapa 13.3. Integridad del respaldo

Generar hashes:

```text
SHA-256
```

Para:

- Base de datos.
- Archivos PDF.
- Comprimidos.
- Índice general.

---

# FASE 14. MEJORAS FUTURAS

## Etapa 14.1. Interfaz gráfica

Crear una aplicación de escritorio con:

- Botón de descarga.
- Selector de filtros.
- Barra de progreso.
- Vista previa.
- Generación de PDF.
- Registro de errores.

Tecnologías posibles:

- Tkinter.
- PySide.
- PyQt.
- Flet.

---

## Etapa 14.2. Catálogo HTML local

Generar un catálogo navegable sin conexión:

```text
index.html
anime/
genres/
studios/
years/
covers/
```

---

## Etapa 14.3. Formatos adicionales

- EPUB.
- HTML.
- CSV.
- JSON.
- Excel.
- Base de datos portable.
- Archivo ZIP por volumen.

---

## Etapa 14.4. Traducción de sinopsis

Opciones:

- Traducción automática.
- Traducción bajo demanda.
- Traducción por lotes.
- Revisión manual.
- Almacenamiento de original y traducción.

---

## Etapa 14.5. Búsqueda local

Permitir búsquedas por:

- Título.
- Año.
- Género.
- Estudio.
- Tipo.
- Estado.
- Palabras de la sinopsis.

---

# CRONOGRAMA PROPUESTO

| Fase | Actividad | Resultado |
|---:|---|---|
| 0 | Definición del alcance | Campos y formatos definidos |
| 1 | Selección de API | Proveedor elegido |
| 2 | Arquitectura | Estructura del proyecto |
| 3 | Base de datos | Modelo funcional |
| 4 | Importador | Registros descargados |
| 5 | Normalización | Datos limpios |
| 6 | Portadas | Imágenes locales optimizadas |
| 7 | Diseño visual | Plantillas aprobadas |
| 8 | PDF | Volúmenes generados |
| 9 | Filtros | Catálogos personalizados |
| 10 | Pruebas | Sistema validado |
| 11 | Actualización | Sincronización incremental |
| 12 | Documentación | Manual completo |
| 13 | Respaldo | Copias verificadas |
| 14 | Mejoras | Funcionalidades futuras |

---

# ORDEN RECOMENDADO DE IMPLEMENTACIÓN

## Primera versión mínima

```text
1. Configuración
2. Conexión con una API
3. Descarga de 100 registros
4. Base de datos SQLite
5. Descarga de portadas
6. Generación de un PDF de prueba
```

## Segunda versión

```text
1. Descarga completa
2. Paginación
3. Reintentos
4. Registro de errores
5. Volúmenes de 500 registros
6. Índice general
```

## Tercera versión

```text
1. Actualización incremental
2. Filtros
3. Varios diseños
4. Traducción opcional
5. Catálogo HTML
6. Interfaz gráfica
```

---

# ENTREGABLES FINALES

```text
01. Código fuente
02. Base de datos local
03. Portadas descargadas
04. PDF por volúmenes
05. Índice general
06. Archivo de configuración
07. Manual de instalación
08. Manual de operación
09. Registro de errores
10. Sistema de actualización
11. Copia de respaldo
12. Archivo README
```

---

# CRITERIOS GENERALES DE ACEPTACIÓN

El proyecto estará completo cuando:

- La aplicación pueda consultar la API.
- Todos los registros obtenidos se almacenen localmente.
- No existan duplicados técnicos.
- Las portadas se descarguen y optimicen.
- Los registros incompletos sean manejados correctamente.
- El catálogo pueda dividirse en volúmenes.
- Cada ficha muestre nombre, año, sinopsis y portada.
- Los PDF puedan abrirse sin errores.
- El índice permita localizar cada anime.
- La actualización no obligue a descargar todo nuevamente.
- El sistema pueda continuar después de una interrupción.
- Exista documentación de instalación y uso.

---

# RIESGOS PRINCIPALES

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Límite de solicitudes | Importación lenta | Esperas y reintentos |
| Cambio de API | Fallo del proveedor | Capa de adaptación |
| Portadas faltantes | Fichas incompletas | Imagen predeterminada |
| PDF demasiado grande | Difícil apertura | División por volúmenes |
| Datos duplicados | Catálogo incorrecto | Identificador único |
| Sinopsis con HTML | Mala presentación | Limpieza de texto |
| Caracteres japoneses | Texto ilegible | Fuente Unicode |
| Descarga interrumpida | Pérdida de progreso | Guardado por página |
| Imágenes pesadas | Archivos gigantes | Compresión automática |
| Registros sin año | Clasificación incompleta | Volumen “Año desconocido” |

---

# RESULTADO ESPERADO

Al finalizar, el usuario dispondrá de una colección local similar a:

```text
CATALOGO_ANIME/
│
├── Base_Datos/
│   └── anime.db
│
├── Portadas/
│   └── miles_de_imagenes.jpg
│
├── PDF/
│   ├── Anime_Catalogo_Volumen_001.pdf
│   ├── Anime_Catalogo_Volumen_002.pdf
│   ├── Anime_Catalogo_Volumen_003.pdf
│   └── ...
│
├── Indices/
│   ├── indice_general.pdf
│   └── indice_general.csv
│
├── Respaldos/
│   └── respaldo_fecha.zip
│
└── Aplicacion/
    └── generador_catalogo.py
```

El sistema permitirá actualizar la base de datos y volver a generar los volúmenes sin reconstruir manualmente cada ficha.
