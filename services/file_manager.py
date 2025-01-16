import os
import yaml
from jinja2 import Environment, FileSystemLoader
from models.constants import Configs, FilesInfo, TemplateInfo
from models.driver_config import AppConfig
from models.language import Language
from models.question import Question

class FileManager:
    """
    Handles file operations, including setting working directories, reading configuration files,
    and writing questions to templates in the appropriate format.
    """

    def set_working_directory(self):
        """
        Sets the working directory to the parent directory of the current module.
        """
        current_module_directory = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_module_directory)
        os.chdir(parent_dir)

    def get_app_config(self) -> AppConfig:
        """
        Reads the application configuration from a YAML file and creates an AppConfig object.

        Returns:
            AppConfig: An instance populated with the configuration values from the file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If there is an error parsing the configuration file.
        """
        if not os.path.exists(Configs.CONFIG_FILE):
            raise FileNotFoundError(f"Configuration file {Configs.CONFIG_FILE} not found.")

        with open(Configs.CONFIG_FILE, "r") as file:
            data = yaml.safe_load(file)
            
        configuration = data.get(Configs.CONFIG_FIELD, {})
        app_config = AppConfig()
        app_config.user_data_directory = configuration.get(Configs.CONFIG_DRIVER_USER_DATA_FIELD, "")
        app_config.profile_name = configuration.get(Configs.CONFIG_DRIVER_PROFILE_NAME_FIELD, "")
        app_config.questions_path_directory = configuration.get(Configs.CONFIG_QUESTIONS_HOME_PATH_FIELD, "")

        return app_config

    def write_question_to_template(self, question: Question, language: Language, path: str) -> str:
        """
        Writes a question to a language-specific template file.

        Args:
            question (Question): The question data to populate the template.
            language (Language): The programming language for the template.
            path (str): The base directory where the file will be saved.

        Returns:
            str: The full path of the created file.
        """
        # Load templates directory
        env = Environment(loader=FileSystemLoader(FilesInfo.TEMPLATES_DIRECTORY))

        # Load the specified template
        template = env.get_template(language.template_file())

        # Fill the template
        context = {
            TemplateInfo.NUMBER: question.number,
            TemplateInfo.TITLE: question.title,
            TemplateInfo.DESCRIPTION: question.description,
            TemplateInfo.CODE: question.code,
        }

        # Prepare directories
        difficulty_directory = os.path.join(path, question.difficulty_directory())
        self.create_directory_if_needed(difficulty_directory)

        question_directory = os.path.join(difficulty_directory, FilesInfo.QUESTION_PREFIX + question.number)
        self.create_directory_if_needed(question_directory)

        # Write the file
        filled_content = template.render(context)
        filename = FilesInfo.QUESTION_PREFIX + question.camelCaseTitle() + language.file_extension()
        return self.write_file(filled_content, question_directory, filename)

    def write_file(self, content: str, directory: str, filename: str) -> str:
        """
        Writes content to a file. Creates the directory if it does not exist.

        Args:
            content (str): The content to write to the file.
            directory (str): The directory where the file will be saved.
            filename (str): The name of the file.

        Returns:
            str: The full path of the created file.
        """
        self.create_directory_if_needed(directory)
        output_path = os.path.join(directory, filename)

        if not os.path.exists(output_path):
            with open(output_path, "w") as output_file:
                output_file.write(content)

        return output_path

    def create_directory_if_needed(self, directory: str):
        """
        Creates a directory if it does not already exist.

        Args:
            directory (str): The directory to create.
        """
        os.makedirs(directory, exist_ok=True)
