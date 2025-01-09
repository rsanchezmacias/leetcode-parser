
class Question: 
    
    def __init__(self):
        self.url = None
        self.title = None
        self.number = None  
        self.difficulty = None 
        self.description = None 
        self.constraints = None 
        self.code = None
            
    def copy_from_raw(self):
        """
        Copy the current instance with fields that are constant between transformations.

        Returns:
            Question: A new Question object with copied attributes.
        """
        copy_question = Question()
        copy_question.url = self.url
        copy_question.difficulty = self.difficulty
        copy_question.code = self.code
        copy_question.description = self.description

        return copy_question