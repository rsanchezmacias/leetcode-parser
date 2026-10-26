from errors.exceptions import InvalidInputException
from models.constants import UserMessages
from utility.slug_extractor import extract_slug


class URLValidator:
    """
    Validates URLs to ensure they are properly formatted and meet required criteria.
    """
    
    def validate_url(self, url: str) -> bool:
        """
        Validates the given URL.

        Args:
            url (str): The URL to validate.

        Returns:
            bool: True if the URL is valid, otherwise raises an exception.

        Raises:
            InvalidInputException: If the URL is invalid or improperly formatted.
        """
        try:
            extract_slug(url)
            return True
        except ValueError:
            raise InvalidInputException(UserMessages.INVALID_INPUT_TYPE)
