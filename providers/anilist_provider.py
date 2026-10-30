import httpx
from providers.base_provider import BaseProvider

class AniListProvider(BaseProvider):
    """
    Implementación del proveedor de datos para la API GraphQL de AniList.
    """
    
    URL = "https://graphql.anilist.co"
    
    def fetch_page(self, page: int, per_page: int = 50) -> dict:
        query = """
        query ($page: Int, $perPage: Int) {
          Page (page: $page, perPage: $perPage) {
            pageInfo {
              total
              currentPage
              lastPage
              hasNextPage
              perPage
            }
            media (type: ANIME, sort: POPULARITY_DESC) {
              id
              title {
                romaji
                english
                native
              }
              startDate {
                year
                month
                day
              }
              format
              episodes
              duration
              status
              season
              description
              coverImage {
                large
              }
              bannerImage
              genres
              studios(isMain: true) {
                nodes {
                  name
                }
              }
              isAdult
              averageScore
              siteUrl
            }
          }
        }
        """
        
        variables = {
            "page": page,
            "perPage": per_page
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.URL,
                    json={"query": query, "variables": variables},
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Error de red al consultar AniList: {e}")
            
        if "data" not in data or "Page" not in data["data"]:
            raise ValueError(f"Respuesta inesperada de AniList: {data}")
            
        page_data = data["data"]["Page"]
        
        page_info = {
            "total": page_data["pageInfo"]["total"],
            "current_page": page_data["pageInfo"]["currentPage"],
            "last_page": page_data["pageInfo"]["lastPage"],
            "has_next_page": page_data["pageInfo"]["hasNextPage"],
            "per_page": page_data["pageInfo"]["perPage"]
        }
        
        records = []
        for media in page_data["media"]:
            if not media:
                continue
                
            # Formatear la fecha de estreno
            year = media["startDate"].get("year")
            month = media["startDate"].get("month")
            day = media["startDate"].get("day")
            
            release_date = None
            if year and month and day:
                release_date = f"{year:04d}-{month:02d}-{day:02d}"
            elif year:
                release_date = f"{year:04d}"
                
            # Determinar títulos
            title_en = media["title"].get("english")
            title_ro = media["title"].get("romaji")
            title_na = media["title"].get("native")
            
            # Prioridad de título: Inglés -> Romaji -> Nativo
            main_title = title_en or title_ro or title_na or f"Anime ID {media['id']}"
            original_title = title_na or title_ro or title_en
            
            # Mapear estudios
            studios = []
            if media.get("studios") and media["studios"].get("nodes"):
                studios = [
                    node["name"] for node in media["studios"]["nodes"] 
                    if node and node.get("name")
                ]
                
            # Ajustar la puntuación (escala 0-100 a 0-10)
            score = None
            if media.get("averageScore") is not None:
                score = round(float(media["averageScore"]) / 10.0, 2)
                
            normalized = {
                "provider": "ANILIST",
                "external_id": str(media["id"]),
                "title": main_title,
                "title_original": original_title,
                "title_english": title_en,
                "title_romaji": title_ro,
                "title_native": title_na,
                "release_year": year,
                "release_date": release_date,
                "format": media.get("format"),
                "episodes": media.get("episodes"),
                "duration_minutes": media.get("duration"),
                "status": media.get("status"),
                "season": media.get("season"),
                "synopsis": media.get("description"),
                "synopsis_es": None,
                "cover_url": media.get("coverImage", {}).get("large") if media.get("coverImage") else None,
                "cover_local_path": None,
                "banner_url": media.get("bannerImage"),
                "rating": None,
                "is_adult": 1 if media.get("isAdult") else 0,
                "score": score,
                "source_url": media.get("siteUrl"),
                "genres": media.get("genres") or [],
                "studios": studios
            }
            records.append(normalized)
            
        return {
            "page_info": page_info,
            "records": records
        }
