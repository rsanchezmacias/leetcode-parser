from urllib.parse import urlparse
from exceptions import InvalidInputException
from constants import UserMessages

class URLValidator:
    
    def __init__(self):
        return 
    
    def validate_url(self, url: str) -> bool:
        try: 
            parsed_url = urlparse(url)
            is_valid = all([parsed_url.scheme, parsed_url.netloc])
            
            if not is_valid:
                raise InvalidInputException(UserMessages.INVALID_INPUT_TYPE)
            
        except ValueError:
            raise InvalidInputException(UserMessages.INVALID_INPUT_TYPE)
        