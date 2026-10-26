class AppConfig:
    """
    Represents the application's configuration settings.
    """

    def __init__(self, questions_path_directory=None):
        """
        Args:
            questions_path_directory (str, optional): Path to the questions directory. Defaults to None.
        """
        self.questions_path_directory = questions_path_directory
