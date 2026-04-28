from .storage_adapter import IStorageAdapter
import time
import random

class CloudStorageAdapter(IStorageAdapter):
    """
    Adapter pentru un API Cloud terț (simulat).
    Adaptează metodele noastre la API-ul complicat al AWS S3 (prefațat).
    """

    def __init__(self, cdn_url: str = "https://cdn.my-task-app.com"):
        self.cdn = cdn_url
        self._s3_mock_client = self._connect_to_s3()

    def _connect_to_s3(self):
        # Simulează conectarea complexă la AWS S3
        return {"connected": True, "bucket": "task-attachments"}

    def save_file(self, file_name: str, content: bytes) -> str:
        # Aici am transforma un apel simplu la funcțiile noastre 
        # într-o mulțime de requesturi AWS:
        # aws_client.upload_multipart(...) etc.
        
        print(f"[Adapter::Cloud] Initiez upload-ul catre {self._s3_mock_client['bucket']} pentru fișierul: {file_name}")
        time.sleep(0.5) # Simulează delay-ul de rețea
        
        url = f"{self.cdn}/uploads/{random.randint(1000,9999)}_{file_name.replace(' ', '_')}"
        print(f"[Adapter::Cloud] Upload complet! URL extern: {url}")
        
        return url

    def delete_file(self, file_path: str) -> bool:
        # Preluăm ID-ul fisierului din URL și trimitem comanda de delete S3.
        print(f"[Adapter::Cloud] Se sterge fișierul remote via URL: {file_path}")
        return True
