from abc import ABC, abstractmethod

class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the tool used for registration."""
        pass

    @abstractmethod
    def run(self, arguments: dict) -> str:
        """Execute the tool using the given arguments."""
        pass