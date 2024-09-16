# The `VectorDBProcessor` class is designed to process PDF files, extract and embed text content into
# a Pinecone index using Google Generative AI embeddings, and provide methods for querying the indexed
# data.
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone, ServerlessSpec
import PyPDF2
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
                existing_indexes = self.pc.list_indexes().names()
                if self.index_name in existing_indexes:
                    print(f"Index '{self.index_name}' already exists.")
                    self.index = self.pc.Index(self.index_name)
                    return True
                print(f"Index '{self.index_name}' does not exist. Creating it...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                    deletion_protection="enabled"  
                )
                self.index = self.pc.Index(self.index_name)
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

    
    def extract_and_embed_pages(self, file_path):
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            small_chunks = []
            
            for page in pages:
                page_content = page.page_content.split('\n')
                small_chunks.extend(
                    [''.join(page_content[i:i+5]) for i in range(0, len(page_content), 5)]
                )
            self.check_and_create_index()
            count = 0
            for chunk in small_chunks:
                count=count+1
                self.vectorize_and_upload(os.path.basename(file_path), chunk, count)
            return True
        except Exception as e:
            print(f"Error processing file: {e}")
            return False
        

    def vectorize_and_upload(self, pdf_name, chunk_content, count):
        embedding = self.embedding_model.embed_query(chunk_content)
        metadata = {'filename': pdf_name, 'part_count': count, 'chunk': chunk_content}
        self.index.upsert([(f"{pdf_name}.part.{count}", embedding, metadata)])
        print(f"Uploaded and Embedded {pdf_name}.part.{count}")

    def query_vectordb(self, query, top_k=10):
        self.check_and_create_index()
        query_embedding = self.embedding_model.embed_query(query)
        results = self.index.query(vector=query_embedding, top_k=top_k)
        matches = results['matches']
        
        # Return results sorted by score in descending order
        # sorted_results = sorted(
        #     [(res['score'], res['id'], res['metadata']['filename'], res['chunk']) for res in matches],
        #     reverse=True
        # )
        
        return matches
