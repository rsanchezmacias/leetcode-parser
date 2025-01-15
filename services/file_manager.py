from jinja2 import Environment, FileSystemLoader
from models.constants import Configs, FilesInfo, TemplateInfo
from models.language import Language
from models.driver_config import AppConfig
from models.question import Question
import os
import yaml

class FileManager: 
    
    def get_app_config(self) -> AppConfig:
        with open(Configs.CONFIG_FILE, "r") as file: 
            data = yaml.safe_load(file)
            configuration = data[Configs.CONFIG_FIELD]
        
        app_config = AppConfig()
        app_config.user_data_directory = configuration[Configs.CONFIG_DRIVER_USER_DATA_FIELD]
        app_config.profile_name = configuration[Configs.CONFIG_DRIVER_PROFILE_NAME_FIELD]
        app_config.questions_path_directory = configuration[Configs.CONFIG_QUESTIONS_HOME_PATH_FIELD]
        
        return app_config
    
    def write_question_to_template(self, question: Question, language: Language, path: str) -> str:
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
        
        # Create difficult directory
        difficulty_directory = os.path.join(path, question.difficulty_directory())
        self.create_directory_if_needed(directory=difficulty_directory)
        
        # Create question directory 
        question_directory = os.path.join(difficulty_directory, FilesInfo.QUESTION_PREFIX + question.number)
        self.create_directory_if_needed(directory=question_directory)
        
        # Write file
        filled_content = template.render(context)
        filename = FilesInfo.QUESTION_PREFIX + question.camelCaseTitle() + language.file_extension()
        self.write_file(content=filled_content, directory=question_directory, filename=filename)
        
    def write_file(self, content: str, directory: str, filename: str):
        self.create_directory_if_needed(directory)
        output_path = os.path.join(directory, filename)
        
        if os.path.exists(output_path):
            return
        
        with open(output_path, 'w') as output_file:
            output_file.write(content)
        
    def create_directory_if_needed(self, directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory)
        