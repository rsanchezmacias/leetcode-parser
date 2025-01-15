from models.driver_config import AppConfig
from models.constants import DOMLabels
from models.language import Language
from models.question import Question
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from services.language_selector import LanguageSelector

class LeetcodeParser:
    
    def __init__(self, config: AppConfig):
        # Initialize browser options to driver
        options = webdriver.ChromeOptions() 
        options.add_argument(f"--user-data-dir={config.user_data_directory}")
        options.add_argument(f"--profile-directory={config.profile_name}")
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=options)  # Use the appropriate driver for your browser
        self.driver.implicitly_wait(0.5)
        
        # Utility helper 
        self.language_selector = LanguageSelector()
    
    def parse(self, url: str, language: Language) -> Question:
        question = Question()
        
        self.driver.get(url)
        self.language_selector.swap_to_correct_language(driver=self.driver, language=language)
        
        # Relative xpath for a div with a class value that contains title
        title = self.driver.find_element(By.XPATH, f"//div[contains(@class, '{DOMLabels.TITLE}')]").text
        # Relative xpath for a div with a class value that contains the question difficulty 
        difficulty = self.driver.find_element(By.XPATH, f"//div[contains(@class, '{DOMLabels.DIFFICULTY}')]").text
        # Get the content without examples nor follow-up
        description_content = self.get_description_content()
        # Get the code from the editor 
        code_template = self.driver.find_element(By.CLASS_NAME, DOMLabels.CODE_LINES_CONTENT)
        
        question.title = title
        question.difficulty = difficulty
        question.description = description_content
        question.code = code_template.text
        
        return question
    
    def get_description_content(self) -> str:
        description_content = self.driver.find_element(By.XPATH, f"//div[@data-track-load='{DOMLabels.DESCRIPTION_BODY}']")
        return description_content.text
        
    def clean_up(self):
        self.driver.quit()
    