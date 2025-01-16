from models.constants import DOMLabels
from models.driver_config import AppConfig
from models.language import Language
from models.question import Question
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from services.language_selector import LanguageSelector


class LeetcodeParser:
    """
    Parses question data from a LeetCode problem page using Selenium.
    """

    def __init__(self, config: AppConfig):
        """
        Initializes the LeetcodeParser with browser configuration.

        Args:
            config (AppConfig): Configuration object containing user data and profile information.
        """
        # Initialize browser options
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={config.user_data_directory}")
        options.add_argument(f"--profile-directory={config.profile_name}")

        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=options)  # Use the appropriate driver for your browser
        self.driver.implicitly_wait(0.5)

        # Utility helper
        self.language_selector = LanguageSelector()

    def parse(self, url: str, language: Language) -> Question:
        """
        Parses a LeetCode problem page and extracts question details.

        Args:
            url (str): The URL of the LeetCode problem page.
            language (Language): The programming language for the code editor.

        Returns:
            Question: A populated Question object containing the problem details.

        Raises:
            NoSuchElementException: If required elements are not found on the page.
        """
        question = Question()

        # Open the problem page
        self.driver.get(url)

        # Set the desired programming language
        self.language_selector.swap_to_correct_language(driver=self.driver, language=language)

        # Extract title
        try:
            title_element = self.driver.find_element(By.XPATH, f"//div[contains(@class, '{DOMLabels.TITLE}')]")
            question.title = title_element.text
        except NoSuchElementException:
            raise NoSuchElementException("Failed to locate the question title.")

        # Extract difficulty
        try:
            difficulty_element = self.driver.find_element(By.XPATH, f"//div[contains(@class, '{DOMLabels.DIFFICULTY}')]")
            question.difficulty = difficulty_element.text
        except NoSuchElementException:
            raise NoSuchElementException("Failed to locate the question difficulty.")

        # Extract description content
        question.description = self.get_description_content()

        # Extract code template
        try:
            code_element = self.driver.find_element(By.CLASS_NAME, DOMLabels.CODE_LINES_CONTENT)
            question.code = code_element.text
        except NoSuchElementException:
            raise NoSuchElementException("Failed to locate the code editor content.")

        return question

    def get_description_content(self) -> str:
        """
        Extracts the problem description content from the page.

        Returns:
            str: The description content as plain text.

        Raises:
            NoSuchElementException: If the description element is not found.
        """
        try:
            description_element = self.driver.find_element(By.XPATH, f"//div[@data-track-load='{DOMLabels.DESCRIPTION_BODY}']")
            return description_element.text
        except NoSuchElementException:
            raise NoSuchElementException("Failed to locate the problem description.")

    def clean_up(self):
        """
        Closes the WebDriver and cleans up resources.
        """
        self.driver.quit()
