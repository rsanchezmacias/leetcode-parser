from models.constants import Configs
from models.driver_config import DriverConfig
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
    