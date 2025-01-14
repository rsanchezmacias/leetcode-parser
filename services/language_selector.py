from models.constants import DOMLabels
from models.language import Language
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class LanguageSelector:
    
    def swap_to_correct_language(self, driver: webdriver.Chrome, language: Language) -> None:
        language_label = language.site_language()
        
        # Find the select-language popover button 
        code_language_dropdown = driver.find_element(By.XPATH, self.build_xpath_query_to_find_code_language_button())
        
        try:
            code_language_dropdown.click()
        except Exception as e: 
            print(e)
            return 
        
        try:
            code_languages_popover = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.XPATH, f'//div[contains(@class, "{DOMLabels.CODE_LANGUAGE_MODAL}")]'))
            )
        except TimeoutException as e:
            print(e)
            return
        
        try: 
            code_language_element = code_languages_popover.find_element(By.XPATH, f'//div[contains(text(), "{language_label}")]') 
            code_language_element.click()
        except (NoSuchElementException, ElementNotInteractableException) as e:
            print(e)
            return 
        
    def build_xpath_query_to_find_code_language_button(self) -> str: 
        language_conditions = [f'text()="{language}"' for language in DOMLabels.CODE_LANGUAGES]
        language_conditions_joined = " or ".join(language_conditions)
        button_query = f"//button[{language_conditions_joined}]"
        return button_query
