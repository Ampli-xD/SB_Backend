#write a class and add constructor to it
class Gemini:
    def __init__(self, room_code, room_name, gemini_key, pinecone_key):
        self.room_code = room_code
        self.room_name = room_name
        self.gemini_key = gemini_key
        self.pinecone_key = pinecone_key
        self.users = []
        self.messages = []
        self.online_users = []
        self.uploaded_data = []
        