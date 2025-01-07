from dataclasses import dataclass

@dataclass(frozen=True)
class UserMessages: 
    INVALID_INPUT_SIZE = "Please just enter a URL for the question you want to answer"
    INVALID_INPUT_TYPE = "Please enter a valid URL for the question"

@dataclass(frozen=True)
class DOMLabels:
    # Title string is inside a link inside a div class
    TITLE = "text-title"
    DIFFICULTY = "text-difficulty"
    DESCRIPTION_BODY = "description_content"
    EXAMPLE = "example"
    
    # Tags 
    TAG_PARAGRAPH = 'p'
    TAG_UNSORTED_LIST = 'u'
    
@dataclass(frozen=True)
class Configs: 
    CONFIG_FILE = "resources/config.yaml"
    CONFIG_FIELD = "config"
    CONFIG_DRIVER_USER_DATA_FIELD = "user_data_dir"
    CONFIG_DRIVER_PROFILE_NAME_FIELD = "profile_directory"