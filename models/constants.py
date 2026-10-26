from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class UserMessages:
    """
    Holds constant strings for user-facing messages related to input validation and examples.
    These messages are used to provide feedback to users when inputs are invalid.
    """
    INVALID_INPUT_SIZE: str = "Please enter a URL for the question you want to answer and a language preference (swift or python)"
    INVALID_INPUT_TYPE: str = "Please enter a valid URL for the question"
    INVALID_INPUT_LANGUAGE: str = "Please provide a valid language (-s for swift, or -p for python)"
    INVALID_PROBLEM_URL: str = "Please enter a LeetCode problem URL, e.g. https://leetcode.com/problems/two-sum/"
    VALID_INPUT_EXAMPLE: str = "Example: python main.py -s https://leetcode.com/problems/two-sum/"

@dataclass(frozen=True)
class Configs:
    """
    Contains configuration file details and related fields.
    These constants help manage file paths and configuration keys.
    """
    CONFIG_FILE: str = "resources/config.yaml"  # Path to the configuration file
    CONFIG_FIELD: str = "config"  # Root field name in the configuration
    CONFIG_QUESTIONS_HOME_PATH_FIELD: str = "questions_home_directory"  # Key for questions' home directory

@dataclass(frozen=True)
class FilesInfo:
    """
    Defines constants for handling template files and output filenames.
    These constants are used to construct file paths and names dynamically.
    """
    TEMPLATES_DIRECTORY: str = "templates"  # Directory where templates are stored
    PYTHON_TEMPLATE: str = "base_py.j2"  # Filename for the Python template
    SWIFT_TEMPLATE: str = "base_swift.j2"  # Filename for the Swift template

    # Filename construction constants
    QUESTION_PREFIX: str = "q"  # Prefix for question files
    PYTHON_EXTENSION: str = ".py"  # File extension for Python files
    SWIFT_EXTENSION: str = ".swift"  # File extension for Swift files

@dataclass(frozen=True)
class TemplateInfo:
    """
    Defines fields used in templates for generating code files.
    These fields are placeholders in templates to be replaced with actual data.
    """
    NUMBER: str = "number"  # Placeholder for the question number
    TITLE: str = "title"  # Placeholder for the question title
    DESCRIPTION: str = "description"  # Placeholder for the question description
    CODE: str = "code"  # Placeholder for the code content
