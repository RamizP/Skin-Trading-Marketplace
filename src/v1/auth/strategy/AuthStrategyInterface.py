from abc import ABC, abstractmethod

class AuthStrategyInterface(ABC):
    """
    Interface for authentication strategies.
    """
    @abstractmethod
    def login(self):
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def register(self):
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def logout(self):
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def current_user(self, token: str, db = None):
        raise NotImplementedError("Subclasses must implement this method.")