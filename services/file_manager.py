from jinja2 import Environment, FileSystemLoader
from models.constants import Configs, FilesInfo, TemplateInfo
from models.driver_config import DriverConfig
from models.question import Question
import os
from pathlib import Path
import yaml

class FileManager: 
    
    def get_driver_config(self) -> DriverConfig:
        home = Path.home()
        with open(Configs.CONFIG_FILE, "r") as file: 
            data = yaml.safe_load(file)
            configuration = data[Configs.CONFIG_FIELD]
        
        driver_config = DriverConfig()
        driver_config.user_data_directory = configuration[Configs.CONFIG_DRIVER_USER_DATA_FIELD]
        driver_config.profile_name = configuration[Configs.CONFIG_DRIVER_PROFILE_NAME_FIELD]
        
        return driver_config
    
    def write_question_to_template(self, question: Question):
        # Load templates directory 
        env = Environment(loader=FileSystemLoader(FilesInfo.TEMPLATES_DIRECTORY))
        
        # Load the specified template
        template = env.get_template(FilesInfo.PYTHON_TEMPLATE)
        
        # Fill the template 
        context = {
            TemplateInfo.NUMBER: question.number,
            TemplateInfo.TITLE: question.title,
            TemplateInfo.DESCRIPTION: question.description,
            TemplateInfo.CODE: question.code,
        }
        
        filled_content = template.render(context)
        filename = FilesInfo.QUESTION_PREFIX + question.camelCaseTitle() + FilesInfo.PYTHON_EXTENSION
        self.write_file(content=filled_content, directory=FilesInfo.OUTPUT_HOME_DIRECTORY, filename=filename)
        
    def write_file(self, content: str, directory: str, filename: str):
        self.create_directory_if_needed(directory)
        output_path = os.path.join(directory, filename)
        with open(output_path, 'w') as output_file:
            output_file.write(content)
        
    def create_directory_if_needed(self, directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory)
        