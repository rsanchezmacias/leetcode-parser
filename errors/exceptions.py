
class InvalidInputException(Exception):
    """ Exception raised when there is an issue with the provided user input """
    pass 

class FilePathNotFound(Exception):
    """ Exception raised when the question file path does not exist """
    pass

class FailedToOpenException(Exception):
    """ Exception raised when the app fails to open the requested file """
    pass 
