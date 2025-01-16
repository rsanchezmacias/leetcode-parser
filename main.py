from services.app_launcher import AppLauncher
from services.file_manager import FileManager
from services.leetcode_parser import LeetcodeParser
from services.question_formatter import QuestionFormatter
from errors.exceptions import InvalidInputException, FilePathNotFound, FailedToOpenException
from models.constants import UserMessages
from utility.terminal_input import TerminalInput
from utility.url_validator import URLValidator
from yaml import YAMLError

def clean_up(exit_code=1):
    """Cleans up resources and exits the application."""
    exit(exit_code)

def get_user_inputs(terminal, url_validator):
    """Gets and validates user inputs."""
    try:
        raw_url = terminal.get_url_input()
        language = terminal.get_language_preference()
        url_validator.validate_url(raw_url)
        return raw_url, language
    except InvalidInputException as e:
        print(f"Input Error: {e}\n{UserMessages.VALID_INPUT_EXAMPLE}")
        clean_up()
    except YAMLError as e:
        print(f"Configuration Error: {e}")
        clean_up()

def load_configuration(file_manager):
    """Loads application configuration."""
    try:
        return file_manager.get_app_config()
    except YAMLError as e:
        print(f"Configuration Error: {e}")
        clean_up()

def parse_question(parser, raw_url, language, question_formatter, file_manager, app_config):
    """Parses the question and writes it to a template."""
    try:
        raw_question = parser.parse(url=raw_url, language=language)
        formatted_question = question_formatter.format_question(raw_question)
        output_path = file_manager.write_question_to_template(
            question=formatted_question,
            language=language,
            path=app_config.questions_path_directory
        )
        return output_path
    except Exception as e:
        print(f"Error during question parsing or writing: {e}")
        clean_up()

def open_generated_file(app_launcher, output_path, language):
    """Opens the generated file in the appropriate application."""
    try:
        app_launcher.open(path=output_path, language=language)
        print(f"File successfully created and opened: {output_path}")
    except (FilePathNotFound, FailedToOpenException) as e:
        print(f"File Error: {e}")
        clean_up()

def main():
    file_manager = FileManager()
    terminal = TerminalInput()
    url_validator = URLValidator()
    question_formatter = QuestionFormatter()
    app_launcher = AppLauncher()
    
    # Set the working directory
    file_manager.set_working_directory()
    
    raw_url, language = get_user_inputs(terminal, url_validator)
    app_config = load_configuration(file_manager)

    parser = LeetcodeParser(config=app_config)
    output_path = parse_question(parser, raw_url, language, question_formatter, file_manager, app_config)
    open_generated_file(app_launcher, output_path, language)

    # Ensure cleanup after execution
    clean_up(exit_code=0)

if __name__ == "__main__":
    main()
