import time

from models.constants import DOMLabels
from models.driver_config import AppConfig
from models.language import Language
from models.question import Question
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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

        # Ensure the user is logged in before proceeding
        self._ensure_logged_in(url)

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

    def _is_logged_in(self) -> bool:
        """
        Checks whether the user is currently logged into LeetCode by looking
        for a login-page URL redirect or a visible Sign In button in the nav.

        Returns:
            bool: True if logged in, False otherwise.
        """
        # Redirected to the login page
        if "/accounts/login" in self.driver.current_url:
            return False

        # Sign In button visible in the nav — only present when logged out
        try:
            self.driver.find_element(
                By.XPATH,
                "//*[self::a or self::button][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]"
            )
            return False
        except NoSuchElementException:
            return True

    def _ensure_logged_in(self, url: str) -> None:
        """
        If not logged in, pauses and prompts the user to log in manually
        in the open Chrome window, then re-navigates to the problem URL.

        Args:
            url (str): The original problem URL to return to after login.

        Raises:
            Exception: If the user is still not logged in after the manual login attempt.
        """
        if self._is_logged_in():
            return

        print("\n⚠️  Not logged in to LeetCode.")
        print("Please log in inside the Chrome window that just opened.")
        input("Press Enter here once you are logged in...")

        # Navigate back to the problem and wait for the page to settle
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            lambda d: "/accounts/login" not in d.current_url
        )

        if not self._is_logged_in():
            self.clean_up()
            raise Exception(
                "Still not logged in after manual login. "
                "Please re-run the script and try again."
            )

    def clean_up(self):
        """
        Closes the WebDriver and cleans up resources.
        """
        self.driver.quit()
