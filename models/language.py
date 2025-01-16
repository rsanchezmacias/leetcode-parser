from enum import Enum
from models.constants import FilesInfo

class Language(Enum):
    """
    Enum representing supported programming languages. Provides mappings
    for site language names, template files, and file extensions.
    """
    PYTHON = "-p"
    SWIFT = "-s"

    def site_language(self):
        """
        Returns the site-specific language name for the current language.

        Returns:
            str: The site language name.
        """
        mapping = {
            Language.PYTHON: "Python3",
            Language.SWIFT: "Swift"
        }
        return mapping.get(self)

    def template_file(self):
        """
        Returns the template file name for the current language.

        Returns:
            str: The template file name.
        """
        mapping = {
            Language.PYTHON: FilesInfo.PYTHON_TEMPLATE,
            Language.SWIFT: FilesInfo.SWIFT_TEMPLATE
        }
        return mapping.get(self)

    def file_extension(self):
        """
        Returns the file extension for the current language.

        Returns:
            str: The file extension.
        """
        mapping = {
            Language.PYTHON: FilesInfo.PYTHON_EXTENSION,
            Language.SWIFT: FilesInfo.SWIFT_EXTENSION
        }
        return mapping.get(self)
