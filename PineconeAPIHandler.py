class VectorDBProcessor:
    def __init__(self, api_key: str, index_name: str):
        self.api_key = api_key
        self.index_name = index_name
    
    def verifier(self):
        return True