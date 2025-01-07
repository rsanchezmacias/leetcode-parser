from file_manager import FileManager
from leetcode_parser import LeetcodeParser
from exceptions import InvalidInputException
from terminal_input import TerminalInput
from url_validator import URLValidator
from yaml import YAMLError

# Initialize terminal input handler 
terminal = TerminalInput()

# Validate URL input from the user
url_validator = URLValidator()

# File manager for laoding user configurations
file_manager = FileManager()

# Function to clean up app state 
def clean_up():
    exit()

# Main function
def main():
    try:
        raw_url = terminal.get_first_input()
        url_validator.validate_url(raw_url)
        driver_config = file_manager.get_driver_config()
    except (InvalidInputException, YAMLError) as e:
        print(e)
        clean_up()
    
    try:
        parser = LeetcodeParser(config=driver_config)
        question = parser.parse(url=raw_url)
        demo = input("waiting...")
        
    finally:
        clean_up()

if __name__ == "__main__":
    main()
