from enum import Enum
from models.constants import FilesInfo

class Language(Enum):
    PYTHON = "-p"
    SWIFT = "-s"
    
    def site_language(self):
        mapping = {
            Language.PYTHON: "Python3",
            Language.SWIFT: "Swift"
        }
        return mapping[self]
    
    def template_file(self):
        mapping = {
            Language.PYTHON: FilesInfo.PYTHON_TEMPLATE,
            Language.SWIFT: FilesInfo.SWIFT_TEMPLATE
        }
        return mapping[self]
    
    def file_extension(self):
        mapping = {
            Language.PYTHON: FilesInfo.PYTHON_EXTENSION,
            Language.SWIFT: FilesInfo.SWIFT_EXTENSION
        }
        return mapping[self]
