from models.question import Question
from typing import Tuple


class QuestionFormatter:
    """
    Utility class to format and process questions parsed from LeetCode.
    For example, it separates the question number and title.
    """
    
    def format_question(self, question: Question) -> Question:
        """
        Formats a raw question by extracting and assigning its number and title.

        Args:
            question (Question): The raw question object.

        Returns:
            Question: A new Question object with formatted title and number.

        Raises:
            ValueError: If the question title format is invalid.
        """
        formatted_question = question.copy_from_raw()

        # Add number and title
        try:
            number, title = self.get_title_and_number(question.title)
            formatted_question.title = title
            formatted_question.number = number
        except ValueError as e:
            raise ValueError(f"Failed to format question title: {question.title}. Error: {e}")

        return formatted_question

    def get_title_and_number(self, raw_title: str) -> Tuple[str, str]:
        """
        Extracts the question number and title from the raw title string.

        Args:
            raw_title (str): The raw title string in the format "1. Two Sum".

        Returns:
            Tuple[str, str]: A tuple containing the question number and title.

        Raises:
            ValueError: If the title format is not "number. title".
        """
        if "." not in raw_title:
            raise ValueError(f"Invalid question title format: {raw_title}")

        components = raw_title.split(".", 1)  # Split only at the first dot
        number, title = components[0].strip(), components[1].strip()

        if not number.isdigit() or not title:
            raise ValueError(f"Invalid question title format: {raw_title}")

        return number, title
