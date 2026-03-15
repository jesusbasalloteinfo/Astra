from typing import List, Any

class CatalogRegistry:
    """
    Registry pattern to register and instantiate catalog providers.
    """
    def __init__(self):
        self._providers = []

    def register(self, provider) -> None:
        """Register an instance of a catalog provider."""
        self._providers.append(provider)

    def get_providers(self) -> List[Any]:
        """Return the list of registered providers."""
        return self._providers
