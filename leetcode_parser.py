from driver_config import DriverConfig
from constants import DOMLabels
from question import Question
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

class LeetcodeParser:
    
    def __init__(self, config: DriverConfig):
        # Initialize browser options to driver
        options = webdriver.ChromeOptions() 
        options.add_argument(f"--user-data-dir={config.user_data_directory}")
        options.add_argument(f"--profile-directory={config.profile_name}")
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=options)  # Use the appropriate driver for your browser
        self.driver.implicitly_wait(0.5)
    
    def parse(self, url: str) -> Question:
        question = Question()
        
        self.driver.get(url)
        
        # Relative xpath for a div with a class value that contains title
        title = self.driver.find_element(By.XPATH, f"//div[contains(@class, '{DOMLabels.TITLE}')]").text
        # Relative xpath for a div with a class value that contains the question difficulty 
        difficulty = self.driver.find_element(By.XPATH, f"//div[contains(@class, '{DOMLabels.DIFFICULTY}')]").text
        # Get the content without examples nor follow-up
        description_content = self.get_description_content()
        
        return question
    
    def get_description_content(self) -> str:
        description_content = self.driver.find_element(By.XPATH, f"//div[@data-track-load='{DOMLabels.DESCRIPTION_BODY}']")
        
        filtered_elements = []
        children_elements = description_content.find_elements(By.XPATH, "./*")
        
        for element in children_elements:
            try: 
                if element.tag_name != DOMLabels.TAG_PARAGRAPH and element.tag_name != DOMLabels.TAG_UNSORTED_LIST:
                    continue
                
                strong_element = element.find_element(By.XPATH, f"./strong[@class='{DOMLabels.EXAMPLE}']")
                if strong_element:
                    continue
                
                filtered_elements.append(element)
            except NoSuchElementException:
                filtered_elements.append(element)
            
        raw_description = ""
        for element in filtered_elements:
            raw_description += element.text
            
        return raw_description
    
    def clean_up(self):
        self.driver.quit()