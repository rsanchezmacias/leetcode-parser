
class Question:
    """
    Represents a programming question with attributes for its URL, title, difficulty,
    description, constraints, and associated code. Provides utility methods for
    transforming and copying question data.
    """

    def __init__(self):
        """
        Initializes a new instance of the Question class with default values.
        """
        self.url = None  # URL of the question
        self.title = None  # Title of the question
        self.number = None  # Number associated with the question (if applicable)
        self.difficulty = None  # Difficulty level (e.g., "Easy", "Medium", "Hard")
        self.description = None  # Description of the question
        self.constraints = None  # Constraints or rules for the question
        self.code = None  # Code associated with the question

    def camelCaseTitle(self) -> str:
        """
        Converts the title of the question to camel case format.

        Returns:
            str: The title in camel case format. Returns an empty string if the title is None.
        """
        if not self.title:
            return ""
        components = self.title.split()
        return ''.join(component.capitalize() for component in components)

    def difficulty_directory(self) -> str:
        """
        Converts the difficulty level to a lowercase directory-friendly string.

        Returns:
            str: The difficulty level in lowercase. Returns an empty string if difficulty is None.
        """
        return self.difficulty.lower() if self.difficulty else ""

    def copy_from_raw(self):
        """
        Creates a new Question instance and copies attributes that are consistent
        across transformations (URL, difficulty, code, and description).

        Returns:
            Question: A new Question object with the copied attributes.
        """
        copy_question = Question()
        copy_question.url = self.url
        copy_question.difficulty = self.difficulty
        copy_question.code = self.code
        copy_question.description = self.description
        return copy_question
