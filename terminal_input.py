import sys
from constants import UserMessages
from exceptions import InvalidInputException

VALID_INPUT_LENGHT = 2

class TerminalInput: 
    
    def __init__(self):
        return 
    
    def get_first_input(self) -> str: 
        arguments = sys.argv
        count = len(arguments)
        
        if count == VALID_INPUT_LENGHT:
            return sys.argv[1]
        else:
            raise InvalidInputException(UserMessages.INVALID_INPUT_SIZE)
            