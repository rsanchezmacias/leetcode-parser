import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from models.constants import DOMLabels
from models.language import Language


class LanguageSelector:
    """
    Handles selecting the correct programming language in a web-based code editor using Selenium.
    """

    def swap_to_correct_language(self, driver: webdriver.Chrome, language: Language) -> None:
        """
        Switches the code editor to the desired programming language.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            language (Language): The programming language to switch to.

        Returns:
            None
        """
        language_label = language.site_language()

        # Find the select-language dropdown button
        try:
            code_language_dropdown = driver.find_element(By.XPATH, self.build_xpath_query_to_find_code_language_button())
            code_language_dropdown.click()
            time.sleep(1)  # Pause to allow dropdown to appear
        except Exception as e:
            print(f"Error clicking language dropdown: {e}")
            return

        # Wait for the language popover to appear
        try:
            code_languages_popover = WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.XPATH, f'//div[contains(@class, "{DOMLabels.CODE_LANGUAGE_MODAL}")]'))
            )
        except TimeoutException as e:
            print(f"Timeout waiting for language popover: {e}")
            return

        # Find and click the desired language
        try:
            code_language_element = code_languages_popover.find_element(By.XPATH, f'//div[contains(text(), "{language_label}")]')
            code_language_element.click()
            time.sleep(1)  # Pause to ensure the language is applied
        except (NoSuchElementException, ElementNotInteractableException) as e:
            print(f"Error selecting language {language_label}: {e}")
            return

    def build_xpath_query_to_find_code_language_button(self) -> str:
        """
        Constructs the XPath query to find the code language dropdown button.

        Returns:
            str: The XPath query string.
        """
        language_conditions = [f'text()="{language}"' for language in DOMLabels.CODE_LANGUAGES]
        language_conditions_joined = " or ".join(language_conditions)
        return f"//button[{language_conditions_joined}]"
