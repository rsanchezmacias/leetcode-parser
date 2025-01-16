
class AppConfig:
    """
    Represents the application's configuration settings.
    Stores paths and user-specific configuration data such as directories and profile names.
    """

    def __init__(self, user_data_directory=None, profile_name=None, questions_path_directory=None):
        """
        Initializes the AppConfig instance with optional parameters.

        Args:
            user_data_directory (str, optional): Path to the user's data directory. Defaults to None.
            profile_name (str, optional): Name of the user's profile. Defaults to None.
            questions_path_directory (str, optional): Path to the questions directory. Defaults to None.
        """
        self.user_data_directory = user_data_directory
        self.profile_name = profile_name
        self.questions_path_directory = questions_path_directory
        