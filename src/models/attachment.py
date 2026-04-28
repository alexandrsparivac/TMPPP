from abc import ABC, abstractmethod
from typing import List

class AttachmentComponent(ABC):
    """Componenta de bază pentru pattern-ul Composite"""
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_size(self) -> int:
        pass
    
    def add(self, component: 'AttachmentComponent'):
        raise NotImplementedError("Această acțiune nu este permisă pe forma de Leaf (frunză).")

    def remove(self, component: 'AttachmentComponent'):
        raise NotImplementedError("Această acțiune nu este permisă pe forma de Leaf (frunză).")

    def get_name(self) -> str:
        return self.name

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @staticmethod
    def from_dict(data: dict) -> 'AttachmentComponent':
        if data.get('type') == 'file':
            return FileItem(data['name'], data['size'])
        elif data.get('type') == 'folder':
            folder = FolderItem(data['name'])
            if 'children' in data:
                for child_data in data['children']:
                    folder.add(AttachmentComponent.from_dict(child_data))
            return folder
        return None

class FileItem(AttachmentComponent):
    """Leaf (Frunză) - Reprezintă un fișier individual"""
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self._size = size

    def get_size(self) -> int:
        return self._size

    def to_dict(self) -> dict:
        return {
            'type': 'file',
            'name': self.name,
            'size': self._size
        }

class FolderItem(AttachmentComponent):
    """Composite - Reprezintă un folder care poate conține alte fișiere sau foldere"""
    def __init__(self, name: str):
        super().__init__(name)
        self.children: List[AttachmentComponent] = []

    def add(self, component: AttachmentComponent):
        self.children.append(component)

    def remove(self, component: AttachmentComponent):
        if component in self.children:
            self.children.remove(component)

    def get_size(self) -> int:
        # Calculează dimensiunea totală recursiv
        return sum(child.get_size() for child in self.children)

    def get_child(self, name: str) -> 'AttachmentComponent':
        for child in self.children:
            if child.get_name() == name:
                return child
        return None

    def to_dict(self) -> dict:
        return {
            'type': 'folder',
            'name': self.name,
            'children': [child.to_dict() for child in self.children]
        }
