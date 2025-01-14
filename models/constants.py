from dataclasses import dataclass

@dataclass(frozen=True)
class UserMessages: 
    INVALID_INPUT_SIZE = "Please enter a URL for the question you want to answer and a language preference (swift or python)"
    INVALID_INPUT_TYPE = "Please enter a valid URL for the question"
    INVALID_INPUT_LANGUAGE = "Please a valid language (-s for swift, or -p python)"
    VALID_INPUT_EXAMPLE = "Example: python -s main.py www.valid_question_url.com"

@dataclass(frozen=True)
class DOMLabels:
    # Title string is inside a link inside a div class
    TITLE = "text-title"
    DIFFICULTY = "text-difficulty"
    DESCRIPTION_BODY = "description_content"
    EXAMPLE = "example"
    CODE_LINES_CONTENT = "lines-content"
    
    # Tags 
    TAG_PARAGRAPH = 'p'
    TAG_UNSORTED_LIST = 'u'
    
    # Code languages model class. It may change in the future
    CODE_LANGUAGE_MODAL = "z-modal"
    
    # Avaiable languages 
    CODE_LANGUAGES = ["C++", "Java", "Python", "Python3", "Swift"]
    
@dataclass(frozen=True)
class Configs: 
    CONFIG_FILE = "resources/config.yaml"
    CONFIG_FIELD = "config"
    CONFIG_DRIVER_USER_DATA_FIELD = "user_data_dir"
    CONFIG_DRIVER_PROFILE_NAME_FIELD = "profile_directory"
    
@dataclass(frozen=True)
class FilesInfo:
    TEMPLATES_DIRECTORY = "templates"
    PYTHON_TEMPLATE = "base_py.j2"
    SWIFT_TEMPLATE = "base_swift.j2"
    
    # Constants to construct filename
    QUESTION_PREFIX = "q"
    PYTHON_EXTENSION = ".py"
    SWIFT_EXTENSION = ".swift"
    
    OUTPUT_HOME_DIRECTORY = "generated/"
    
@dataclass(frozen=True)
class TemplateInfo:
    NUMBER = "number"
    TITLE = "title"
    DESCRIPTION = "description"
    CODE = "code"
    