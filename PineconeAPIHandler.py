from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone
import io
import os

class VectorDBProcessor:
    def __init__(self, api_keys, index_name='stormbrainer'):
        self.index_name = index_name
        self.api_keys = api_keys
        self.pc = Pinecone(api_key=api_keys[0])
        self.index = None
        self.embedding_model = self.set_embedding_model()
        
    def set_embedding_model(self):
        os.environ["GOOGLE_API_KEY"] = self.api_keys[1]
        em = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        return em
        
    def check_and_create_index(self):
        """
        Checks if a Pinecone index exists and creates it if it does not.

        Args:
            api_key (str): The API key for Pinecone.
            index_name (str): The name of the index to check/create.
            dimension (int): The dimension of the vectors for the index.

        Returns:
            bool: True if the index exists or was successfully created, False otherwise.
        """
        if self.index == None:
            try:
                existing_indexes = self.pc.list_indexes()
                if self.index_name in existing_indexes:
                    print(f"Index '{self.index_name}' already exists.")
                    self.pc.Index(self.index_name)
                    return True
                print(f"Index '{self.index_name}' does not exist. Creating it...")
                self.pc.create_index(name=self.index_name, dimension=1536)
                self.pc.Index(self.index_name)
                print(f"Index '{self.index_name}' created successfully.")
                return True
            except Exception as e:
                print(f"Error checking or creating index: {e}")
                return False
        else:
            return self.index

    @staticmethod
    def verifier(api_key):
        try:
            Pinecone(api_key=api_key)
            return True
        except:
            return False

    def extract_and_embed_pages(self, file):
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        pdf_content = io.BytesIO(file.read())
        loader = PyPDFLoader(pdf_content)
        pages = loader.load_and_split()
        self.check_and_create_index()
        for page in pages:
            self.vectorize_and_upload(file.filename, page.page_content)
        return True

    def vectorize_and_upload(self, pdf_name, page_content):
        embedding = self.embedding_model.embed_query(page_content)
        metadata = {'source': pdf_name}
        self.index.upsert([(pdf_name, embedding, metadata)])
        print(f"Uploaded and Embedded {pdf_name}")

    def query_pinecone(self, query, top_k=10):
        query_embedding = self.embedding_model.embed_query(query)
        results = self.index.query(vector=query_embedding, top_k=top_k)
        
        matches = results['matches']
        sorted_results = sorted(
            [(res['score'], res['id']) for res in matches],
            reverse=True
        )
        return {id: score for score, id in sorted_results}