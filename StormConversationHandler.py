import google.generativeai as genai
import os

class GenAiProcessor:
    def __init__(self, api_key: str, model_name="models/gemini-1.5-pro"):
        """Initialize the GenAiProcessor with the API key and model name."""
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self.chat_session = None
        self.initialize_model()

    @staticmethod
    def verifier():
        """Verify the API key."""
        try:
            genai.configure(api_key=self.api_key)
            genai.GenerativeModel(model_name='models/gemini-1.5-pro')
            return True
        except Exception as e:
            return
    
    def initialize_model(self):
        """Configure the model with the API key and initialize it."""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)
        
    def start_chat_session(self):
        """Start a new chat session if not already active."""
        if self.chat_session is None:
            self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)
        return self.chat_session

    def chat(self, message: str, prompt: str) -> str:
        """Send a message along with a prompt to the chat session and get the response."""
        session = self.start_chat_session()
        full_message = message + " " + prompt
        response = session.send_message(full_message)
        return response.text

