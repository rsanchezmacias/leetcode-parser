from errors.exceptions import FilePathNotFound, FailedToOpenException
from models.language import Language
import subprocess
import os

class AppLauncher:
    
    def open(self, path: str, language: Language):
        try: 
            if language == Language.SWIFT:
                self.open_with_xcode(file_path=path)   
            elif language == Language.PYTHON:
                self.open_with_visual_studio(file_path=path) 
        except Exception as e:
            raise e
        
    
    def open_with_xcode(self, file_path: str):
        """
        Opens a .swift file in Xcode.

        Args:
            file_path (str): The path to the .swift file to open.
        """
        if not os.path.exists(file_path):
            raise FilePathNotFound(f"Question filepath {file_path} does not exist")
        
        try:
            subprocess.run(["open", "-a", "Xcode", file_path], check=True)
        except:
            raise FailedToOpenException(f"Failed to open file {file_path}")
        
    def open_with_visual_studio(self, file_path: str):
        """
        Opens a file in Visual Studio Code.

        Args:
            file_path (str): The path to the file to open.
        """
        if not os.path.exists(file_path):
            raise FilePathNotFound(f"Question filepath {file_path} does not exist")
        
        try:
            subprocess.run(["code", file_path], check=True)  # 'code' is the VS Code command-line tool
            print(f"Opened {file_path} in Visual Studio Code.")
        except:
            raise FailedToOpenException(f"Failed to open file {file_path}")
