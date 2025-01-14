from enum import Enum

class Language(Enum):
    PYTHON = "-p"
    SWIFT = "-s"
    
    def site_language(self):
        mapping = {
            Language.PYTHON: "Python3",
            Language.SWIFT: "Swift"
        }
        return mapping[self]
    
