from services.file_manager import FileManager
from services.leetcode_parser import LeetcodeParser
from services.question_formatter import QuestionFormatter
from errors.exceptions import InvalidInputException
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
        driver_config = file_manager.get_driver_config()
    except InvalidInputException as e: 
        print(e)
        clean_up() 
    
    try:
        parser = LeetcodeParser(config=driver_config)
        raw_question = parser.parse(url=raw_url, language=language)
        formatted_question = question_formatter.format_question(raw_question)
        file_manager.write_question_to_template(formatted_question)
        demo = input("waiting...")
        
    finally:
        clean_up()

if __name__ == "__main__":
    main()
