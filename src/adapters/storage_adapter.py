from abc import ABC, abstractmethod

class IStorageAdapter(ABC):
    """Interfața pentru serviciile de stocare (Target) - Adaptor Pattern"""
    
    @abstractmethod
    def save_file(self, file_name: str, content: bytes) -> str:
        """
        Salvează fișierul și returnează un URL sau o cale de acces.
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Șterge un fișier pe baza căii"""
        pass
