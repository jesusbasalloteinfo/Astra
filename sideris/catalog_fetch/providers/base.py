from abc import ABC, abstractmethod
from typing import List, Any
from catalog_fetch.network import NetworkMixin

class BaseCatalogProvider(ABC, NetworkMixin):

    @abstractmethod
    def run(self) -> List[Any]:
        """Runs the entire provider pipeline (fetch, clean, normalize) and returns standardized objects."""
        pass
        
    @abstractmethod
    def fetch(self) -> Any:
        pass

    @abstractmethod
    def clean(self, raw_data: Any) -> Any:
        pass

    @abstractmethod
    def normalize(self, cleaned_data: Any) -> List[Any]:
        pass
