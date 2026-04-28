import os
from src.models.attachment import FileItem, FolderItem
from src.adapters.storage_adapter import IStorageAdapter
from src.repositories.mongodb_task_repository import MongoTaskRepository

class TaskAttachmentFacade:
    """
    Facade care simplifică procesul de adăugare și organizare a atașamentelor
    într-un task. Ascunde complexitatea interacțiunii dintre modelele Composite,
    adaptoarele de stocare, și baza de date.
    """
    
    def __init__(self, task_repo: MongoTaskRepository, storage_adapter: IStorageAdapter):
        self.task_repo = task_repo
        self.storage_adapter = storage_adapter

    def upload_file_to_task(self, task_id: str, file_name: str, content: bytes, folder_path: str = "") -> dict:
        """
        Metodă unificată pentru adăugarea unui fișier.
        - Salviază pe disk/cloud (Adapter)
        - Adaugă în structura Composite (Models)
        - Actualizeaza baza de date (Repository)
        """
        # Gasim taskul în DB.
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Taskul cu ID-ul {task_id} nu a fost găsit!")
            
        print(f"[Facade] Task gasit: '{task.title}'. Incep procesul de upload...")

        # 1. Salvează fișierul fizic folosind adaptorul selectat
        saved_path = self.storage_adapter.save_file(file_name, content)
        size_bytes = len(content)

        # 2. Creează elementul Composite "Frunză" (Leaf)
        new_file = FileItem(file_name, size_bytes)
        
        # 3. Găsește sau creează Folderul (Composite) unde salvam fișierul
        target_folder = self._resolve_target_folder(task.attachments_root, folder_path)
        
        # 4. Adaugă elementul creat
        target_folder.add(new_file)
        print(f"[Facade] Fișier '{file_name}' (Mărime: {size_bytes} byți) a fost adăugat în mapa '{target_folder.get_name()}'")

        # 5. Salvează task-ul actualizat cu noile metadate în BD
        # In mod real, MongoDB driver serializeaza asta într-un BSON.
        # Pentru moment simulăm un update
        self.task_repo.update(task)
        print("[Facade] Arborele Composite a fost actualizat în baza de date cu succes.")
        
        return {
            "file_name": file_name,
            "path": saved_path,
            "size": size_bytes,
            "total_task_attachments_size": task.attachments_root.get_size() # Apelează metoda Composite
        }

    def _resolve_target_folder(self, root: FolderItem, path: str) -> FolderItem:
        """Helper func: Parcurge (și creează dacă nu există) ierarhia de foldere."""
        if not path or path == "/":
            return root

        current = root
        parts = path.strip("/").split("/")
        
        for part in parts:
            if not part:
                continue
                
            next_folder = current.get_child(part)
            if next_folder is None:
                next_folder = FolderItem(part)
                current.add(next_folder)
                print(f"[Facade] A fost creat folderul nou: '{part}' sub nivelul '{current.get_name()}'")
            elif not isinstance(next_folder, FolderItem):
                raise ValueError(f"'{part}' există și este un fișier, nu dosar!")
            
            # Pășim adânc în ierarhie
            current = next_folder

        return current
