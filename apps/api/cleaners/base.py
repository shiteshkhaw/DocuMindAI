from abc import ABC, abstractmethod

class BaseCleaner(ABC):
    @abstractmethod
    def clean(self, text: str) -> str:
        """Cleans the given text and returns the normalized/cleaned string."""
        pass
