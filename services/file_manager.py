import os
import sys
import yaml
from jinja2 import Environment, FileSystemLoader
from models.constants import Configs, FilesInfo, TemplateInfo
from models.driver_config import AppConfig
from models.language import Language
from models.question import Question

# Persistent data directory used when running as a compiled app bundle.
BUNDLE_DATA_DIR = os.path.join(
    os.path.expanduser("~"), "Library", "Application Support", "LeetCodeFormatter"
)

# Sentinel written into config on first launch — signals "not yet configured".
PLACEHOLDER_QUESTIONS_DIR = "/path/to/store/questions"

# Default config written on first launch of the app bundle.
DEFAULT_CONFIG_TEMPLATE = """\
config:
  questions_home_directory: "{placeholder}"
""".format(placeholder=PLACEHOLDER_QUESTIONS_DIR)


def _is_bundled() -> bool:
    """Returns True when running inside a py2app .app bundle."""
    return getattr(sys, "frozen", False)


class FileManager:
    """
    Handles file operations, including setting working directories, reading configuration files,
    and writing questions to templates in the appropriate format.
    """

    def set_working_directory(self):
        """
        Script mode : changes CWD to the project root so relative paths resolve correctly.
        Bundle mode : no-op — paths are resolved explicitly via _config_path / _templates_dir.
        """
        if not _is_bundled():
            current_module_directory = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_module_directory)
            os.chdir(parent_dir)

    # ------------------------------------------------------------------ #
    #  Path helpers
    # ------------------------------------------------------------------ #

    def _config_path(self) -> str:
        """Returns the absolute path to config.yaml for the current run mode."""
        if _is_bundled():
            return os.path.join(BUNDLE_DATA_DIR, "config.yaml")
        return Configs.CONFIG_FILE

    def _templates_dir(self) -> str:
        """Returns the absolute path to the templates directory for the current run mode."""
        if _is_bundled():
            # py2app places data files in Contents/Resources/
            return os.path.join(os.environ.get("RESOURCEPATH", ""), "templates")
        return FilesInfo.TEMPLATES_DIRECTORY

    def _ensure_bundle_data_dir(self):
        """
        Creates ~/Library/Application Support/LeetCodeFormatter/ and a starter
        config.yaml on the first launch of the app bundle.
        """
        os.makedirs(BUNDLE_DATA_DIR, exist_ok=True)
        config_path = self._config_path()
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                f.write(DEFAULT_CONFIG_TEMPLATE)

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def get_app_config(self) -> AppConfig:
        """
        Reads the application configuration from a YAML file and creates an AppConfig object.

        Returns:
            AppConfig: An instance populated with the configuration values from the file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If there is an error parsing the configuration file.
        """
        if _is_bundled():
            self._ensure_bundle_data_dir()

        config_path = self._config_path()

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")

        with open(config_path, "r") as file:
            data = yaml.safe_load(file)

        configuration = data.get(Configs.CONFIG_FIELD, {})
        app_config = AppConfig()
        app_config.questions_path_directory = os.path.expanduser(
            configuration.get(Configs.CONFIG_QUESTIONS_HOME_PATH_FIELD, "")
        )

        return app_config

    def is_questions_dir_configured(self, config: AppConfig) -> bool:
        """
        Returns True if questions_home_directory is set to a real path.
        Returns False if it is empty or still the first-launch placeholder.
        """
        path = config.questions_path_directory
        return bool(path) and path != PLACEHOLDER_QUESTIONS_DIR

    def save_questions_dir(self, new_path: str):
        """
        Writes a new questions_home_directory value into config.yaml,
        preserving all other existing settings.

        Args:
            new_path (str): The absolute path chosen by the user.
        """
        config_path = self._config_path()
        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}

        data.setdefault(Configs.CONFIG_FIELD, {})[Configs.CONFIG_QUESTIONS_HOME_PATH_FIELD] = new_path

        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

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
        env = Environment(loader=FileSystemLoader(self._templates_dir()))
        template = env.get_template(language.template_file())

        context = {
            TemplateInfo.NUMBER: question.number,
            TemplateInfo.TITLE: question.title,
            TemplateInfo.DESCRIPTION: question.description,
            TemplateInfo.CODE: question.code,
        }

        difficulty_directory = os.path.join(path, question.difficulty_directory())
        self.create_directory_if_needed(difficulty_directory)

        question_directory = os.path.join(difficulty_directory, FilesInfo.QUESTION_PREFIX + question.number)
        self.create_directory_if_needed(question_directory)

        filled_content = template.render(context)
        filename = FilesInfo.QUESTION_PREFIX + question.camelCaseTitle() + language.file_extension()
        return self.write_file(filled_content, question_directory, filename)

    def write_file(self, content: str, directory: str, filename: str) -> str:
        """
        Writes content to a file. Creates the directory if it does not exist.

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
        """Creates a directory if it does not already exist."""
        os.makedirs(directory, exist_ok=True)
