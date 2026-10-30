from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """
    Clase abstracta base para los proveedores de datos de anime.
    Define el contrato para la normalización de datos externos.
    """

    @abstractmethod
    def fetch_page(self, page: int, per_page: int = 50) -> dict:
        """
        Obtiene una página de registros de la API y los normaliza.
        
        Debe retornar un diccionario con el siguiente formato:
        {
            "page_info": {
                "total": int,
                "current_page": int,
                "last_page": int,
                "has_next_page": bool,
                "per_page": int
            },
            "records": [
                # Lista de diccionarios con formato interno uniforme
            ]
        }
        """
        pass
