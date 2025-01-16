from urllib.parse import urlparse
from errors.exceptions import InvalidInputException
from models.constants import UserMessages


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
            parsed_url = urlparse(url)
            is_valid = all([parsed_url.scheme, parsed_url.netloc])

            if not is_valid:
                raise InvalidInputException(UserMessages.INVALID_INPUT_TYPE)

            return True
        except ValueError:
            raise InvalidInputException(UserMessages.INVALID_INPUT_TYPE)
