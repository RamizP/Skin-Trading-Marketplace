from abc import ABC, abstractmethod

class AuthStrategyInterface(ABC):
    """
    Interface for authentication strategies.
    """
    @abstractmethod
    def login(self):
        """
        Authenticate the user based on the request.

        :param request: The request object containing authentication data.
        :return: User object if authentication is successful, otherwise None.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def register(self):
        """
        Register a new user with the provided user data.

        :param user_data: Data required for user registration.
        :return: User object if registration is successful, otherwise raises an exception.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def logout(self):
        """
        Log out the user by clearing the authentication token.

        :return: Response indicating successful logout.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def current_user(self):
        """
        Retrieve the current user based on the authentication token.

        :param token: The authentication token.
        :param db: Database session.
        :return: User object if the token is valid, otherwise raises an exception.
        """
        raise NotImplementedError("Subclasses must implement this method.")