from models.question import Question
from typing import Tuple

class QuestionFormatter:
    """
    Utility class to format the question parsed from Leetcode. For example, it separates the question number and title
    """
    
    def format_question(self, question: Question) -> Question:
        formatted_question = question.copy_from_raw()
        
        # Add number and title
        number, title = self.get_title_and_number(question.title)
        formatted_question.title = title
        formatted_question.number = number
        
        return formatted_question
    
    def get_title_and_number(self, raw_title: str) -> Tuple[str, str]:
        components = raw_title.split(".")
        number, title = components[0].strip(), components[1].strip()
        return (number, title)
    