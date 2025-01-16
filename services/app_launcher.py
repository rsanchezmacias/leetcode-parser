import os
import subprocess

from errors.exceptions import FailedToOpenException, FilePathNotFound
from models.language import Language


class AppLauncher:
    """
    Handles launching files in appropriate applications based on the file's language.
    """

    def open(self, path: str, language: Language):
        """
        Opens a file in an application based on the specified programming language.

        Args:
            path (str): The file path to open.
            language (Language): The programming language associated with the file.

        Raises:
            FilePathNotFound: If the specified file path does not exist.
            FailedToOpenException: If the application fails to open the file.
        """
        try:
            if language == Language.SWIFT:
                self.open_with_xcode(file_path=path)
            elif language == Language.PYTHON:
                self.open_with_visual_studio(file_path=path)
            else:
                raise ValueError("Unsupported language provided.")
        except Exception as e:
            raise e

    def open_with_xcode(self, file_path: str):
        """
        Opens a .swift file in Xcode.

        Args:
            file_path (str): The path to the .swift file to open.

        Raises:
            FilePathNotFound: If the file path does not exist.
            FailedToOpenException: If Xcode fails to open the file.
        """
        if not os.path.exists(file_path):
            raise FilePathNotFound(f"Question filepath {file_path} does not exist")

        try:
            subprocess.run(["open", "-a", "Xcode", file_path], check=True)
        except subprocess.SubprocessError:
            raise FailedToOpenException(f"Failed to open file {file_path} in Xcode.")

    def open_with_visual_studio(self, file_path: str):
        """
        Opens a file in Visual Studio Code.

        Args:
            file_path (str): The path to the file to open.

        Raises:
            FilePathNotFound: If the file path does not exist.
            FailedToOpenException: If Visual Studio Code fails to open the file.
        """
        if not os.path.exists(file_path):
            raise FilePathNotFound(f"Question filepath {file_path} does not exist")

        try:
            subprocess.run(["code", file_path], check=True)  # 'code' is the VS Code CLI tool
        except subprocess.SubprocessError:
            raise FailedToOpenException(f"Failed to open file {file_path} in Visual Studio Code.")
