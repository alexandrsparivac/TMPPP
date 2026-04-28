# Testare completă a flow-ului

from src.models.task import Task
from src.adapters.local_storage_adapter import LocalStorageAdapter
from src.adapters.cloud_storage_adapter import CloudStorageAdapter
from src.facades.attachment_facade import TaskAttachmentFacade

# Facem un Mock pentru repository
class MongoDBTaskRepositoryMock:
    def __init__(self):
        self._tasks = {}
        
    def add(self, task: Task):
        self._tasks[task.id] = task
        
    def update(self, task: Task):
        self._tasks[task.id] = task

    def get_by_id(self, task_id: str) -> Task:
        return self._tasks.get(task_id)

def run_feature_test():
    print("========= Testare Funcționalitate Atașamente (Varianta 2) =========\n")
    
    # 1. Inițializăm un sistem de stocare (Adapter)
    # Poate fi ușor schimbat între `LocalStorageAdapter` sau `CloudStorageAdapter`
    storage_adapter = CloudStorageAdapter()
    # storage_adapter = LocalStorageAdapter("/tmp/test_uploads")
    
    # 2. Mock pentru repository și Facade
    repo = MongoDBTaskRepositoryMock()
    facade = TaskAttachmentFacade(task_repo=repo, storage_adapter=storage_adapter)

    # 3. Crearea unui task 
    print("-> Crearea unui Task...")
    new_task = Task(id="1", title="Planificare arhitectură", user_id="u123")
    repo.add(new_task)

    # 4. Inserarea fișierelor utilizând pur și simplu FAȚADA (Facade)
    print("\n-> Adăugare fișier doc 1...")
    facade.upload_file_to_task(
        task_id="1",
        file_name="cerințe_arhitectură.pdf",
        content=b"Cerinte complete sistem bla bla...", # Mărime 36 bytes
        folder_path="Docs"
    )

    print("\n-> Adăugare imagine 1 (cu cloud adapter prefațat)...")
    facade.upload_file_to_task(
        task_id="1",
        file_name="schema_bazei_de_date.png",
        content=b"Imagine PNG...", # Mărime 14 bytes
        folder_path="Docs/Imagini"
    )

    print("\n-> Adăugare imagine 2 (la rădăcină)...")
    facade.upload_file_to_task(
        task_id="1",
        file_name="logo_proiect.jpg",
        content=b"Logo..", # Mărime 6 bytes
        folder_path=""
    )

    # 5. Calcularea automată a mărimii prin COMPOSITE
    task = repo.get_by_id("1")
    print("\n========= Rezultate Finale =========")
    print(f"Task: {task.title}")
    
    # Adunăm mărimea tuturor folderelor și fișierelor din rădăcină
    total_size = task.attachments_root.get_size()
    print(f"Dimensiunea totală a fișierelor atașate este de: {total_size} byți")
    
    # Afișarea sumară a dosarelor
    print("Structura folderelor atașate:")
    def print_tree(folder, indent=0):
        for child in folder.children:
            print("  " * indent + "- " + child.get_name() + f" ({child.get_size()} b)")
            # Dacă este din nou FolderItem (Composite), verificăm adânc
            if child.__class__.__name__ == "FolderItem":
                print_tree(child, indent + 1)
                
    print_tree(task.attachments_root)
    print("================================================================")

if __name__ == "__main__":
    run_feature_test()
