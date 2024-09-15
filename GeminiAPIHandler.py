import google.generativeai as genai

class GenAiProcessor:
    def __init__(self, api_key: str, model_name="models/gemini-1.5-pro"):
        """Initialize the GenAiProcessor with the API key and model name."""
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self.chat_session = None
        self.initialize_model()

    @staticmethod
    def verifier(api_key):
        """Verify the API key."""
        try:
            genai.configure(api_key=api_key)
            genai.GenerativeModel(model_name='models/gemini-1.5-pro')
            return True
        except Exception as e:
            return False
    
    def initialize_model(self):
        """Configure the model with the API key and initialize it."""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)
        
    def start_chat_session(self):
        """Start a new chat session if not already active."""
        if self.chat_session is None:
            self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)
        return self.chat_session

    p = """you are storm an AI brainstorming companion, you are here to help brainstorm 
        ideas for diverse fields, be polite and answer the questions properly. you are developed 
        to ideate and process different ideas for events, hackthons, project planning, startups etc.
        you are a very helpful AI companion create by Dishant, you are here to help the users,
        To make your responses clear and intuitive, use a pseudo-HTML style in your formatting. 
        For example, if you want to emphasize a point, use .b for bold text (e.g., .b This is important). 
        For italic text, use .i (e.g., .i This is noteworthy). When adding emphasis, use .strong and .em. 
        To include a line break, use .br, and for separating sections, use .hr. For lists, start with .ul   
        and use .li for each item (e.g., .ul .li Idea 1 .li Idea 2). Convert commands like .cl to close 
        all tags or .m for adding a marquee. Structure your responses using these tags to help users easily 
        follow and understand the information you provide. Ensure proper usage of these tags to maintain 
        clear and organized output."""
        
    def chat(self, message: str, prompt = p ) -> str:
        """Send a message along with a prompt to the chat session and get the response."""
        session = self.start_chat_session()
        full_message = message + " " + prompt
        response = session.send_message(full_message)
        return response.text
    
    