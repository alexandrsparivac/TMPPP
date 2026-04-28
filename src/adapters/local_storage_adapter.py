from .storage_adapter import IStorageAdapter
import os
import uuid

class LocalStorageAdapter(IStorageAdapter):
    """Implementare de test/locala a adaptorului de stocare"""
    
    def __init__(self, base_path: str = "/tmp/uploads"):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)
            
    def save_file(self, file_name: str, content: bytes) -> str:
        # Generăm un nume unic pentru a evita suprascrierea
        unique_name = f"{uuid.uuid4()}_{file_name}"
        full_path = os.path.join(self.base_path, unique_name)
        
        with open(full_path, "wb") as f:
            f.write(content)
            
        print(f"[Adapter::Local] Fișier salvat local la: {full_path}")
        return full_path

    def delete_file(self, file_path: str) -> bool:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[Adapter::Local] Fișier șters local: {file_path}")
            return True
        return False
