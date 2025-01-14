import sys
from models.constants import UserMessages
from models.language import Language
from errors.exceptions import InvalidInputException

VALID_INPUT_LENGHT = 3

class TerminalInput: 
    
    def __init__(self):
        return 
    
    def get_url_input(self) -> str: 
        arguments = sys.argv
        count = len(arguments)
        
        if count == VALID_INPUT_LENGHT:
            return sys.argv[2]
        else:
            raise InvalidInputException(UserMessages.INVALID_INPUT_SIZE)
        
    def get_language_preference(self) -> Language: 
        arguments = sys.argv
        count = len(arguments)
        
        if count != VALID_INPUT_LENGHT:
            raise InvalidInputException(UserMessages.INVALID_INPUT_SIZE)
        try:
            language = Language(value=sys.argv[1])
        except: 
            raise ValueError("Invalid language")
        
        return language
    