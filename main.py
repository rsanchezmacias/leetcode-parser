from services.app_launcher import AppLauncher
from services.file_manager import FileManager
from services.leetcode_parser import LeetcodeParser
from services.question_formatter import QuestionFormatter
from errors.exceptions import InvalidInputException, FilePathNotFound, FailedToOpenException
from models.constants import UserMessages
from utility.terminal_input import TerminalInput
from utility.url_validator import URLValidator
from yaml import YAMLError

# Initialize terminal input handler 
terminal = TerminalInput()

# Validate URL input from the user
url_validator = URLValidator()

# File manager for laoding user configurations
file_manager = FileManager()

# Utility service to format the question information 
question_formatter = QuestionFormatter()

# Service to launch the output file
app_launcher = AppLauncher()

# Function to clean up app state 
def clean_up():
    exit()

# Main function
def main():
    try:
        raw_url = terminal.get_url_input()
        language = terminal.get_language_preference()
    except (InvalidInputException, ValueError) as e:
        print(e)
        print(UserMessages.VALID_INPUT_EXAMPLE)
        clean_up()
    except YAMLError as e: 
        print(e)
        clean_up() 
        
    try: 
        url_validator.validate_url(raw_url)
        app_config = file_manager.get_app_config()
    except InvalidInputException as e: 
        print(e)
        clean_up() 
    
    try:
        parser = LeetcodeParser(config=app_config)
        raw_question = parser.parse(url=raw_url, language=language)
        formatted_question = question_formatter.format_question(raw_question)
        output_path = file_manager.write_question_to_template(
            formatted_question,
            language=language,
            path=app_config.questions_path_directory
        )
    except Exception as e:
        print(e)
        clean_up()
        
    try: 
        app_launcher.open(path=output_path, language=language)
    except (FilePathNotFound, FailedToOpenException) as e: 
        print(e)
        clean_up()
    
    # Close the driver 
    clean_up()

if __name__ == "__main__":
    main()
