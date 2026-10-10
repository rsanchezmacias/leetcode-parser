from enum import Enum
from models.constants import FilesInfo

class Language(Enum):
    """
    Enum representing supported programming languages. Provides mappings
    for site language names, template files, and file extensions.
    """
    PYTHON = "-p"
    SWIFT = "-s"

    def snippet_slug(self):
        """
        Returns LeetCode's identifier for this language in a question's codeSnippets.

        Returns:
            str: The language slug, e.g. "python3".
        """
        mapping = {
            Language.PYTHON: "python3",
            Language.SWIFT: "swift"
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
