import sys
from errors.exceptions import InvalidInputException
from models.constants import UserMessages
from models.language import Language

VALID_INPUT_LENGTH = 3


class TerminalInput:
    """
    Handles parsing and validation of terminal input arguments for URL and language preference.
    """

    def get_url_input(self) -> str:
        """
        Retrieves the URL input from terminal arguments.

        Returns:
            str: The URL provided in the terminal arguments.

        Raises:
            InvalidInputException: If the number of arguments is incorrect.
        """
        arguments = sys.argv
        if len(arguments) == VALID_INPUT_LENGTH:
            return arguments[2]
        raise InvalidInputException(UserMessages.INVALID_INPUT_SIZE)

    def get_language_preference(self) -> Language:
        """
        Retrieves the language preference from terminal arguments.

        Returns:
            Language: The language preference as a Language enum value.

        Raises:
            InvalidInputException: If the number of arguments is incorrect.
            ValueError: If the language input does not match any valid Language enum value.
        """
        arguments = sys.argv
        if len(arguments) != VALID_INPUT_LENGTH:
            raise InvalidInputException(UserMessages.INVALID_INPUT_SIZE)

        try:
            return Language(arguments[1])  # Match the input to the Language enum
        except ValueError:
            raise InvalidInputException(UserMessages.INVALID_INPUT_LANGUAGE)
