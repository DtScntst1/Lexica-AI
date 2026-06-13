import os
from dotenv import load_dotenv

load_dotenv()

# Prevent local tensorflow crashing transformers import
os.environ['USE_TF'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class RagEngine:
    def __init__(self):
        self.index_name = "lexica-v2"
        pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        
        # Initialize Embeddings using Pinecone Serverless Inference API
        self.embeddings = PineconeEmbeddings(
            model="multilingual-e5-large",
            pinecone_api_key=pinecone_api_key
        )
        
        # Initialize Pinecone
        pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        # Auto-create index if it doesn't exist
        from pinecone import ServerlessSpec
        if self.index_name not in self.pc.list_indexes().names():
            print(f"Creating Pinecone index '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            
        # Initialize Vector Store
        self.vector_store = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings
        )
        
        # Initialize Groq LLM
        self.llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
            
    def index_document(self, file_path: str, filename: str):
        """Loads a PDF from a temporary path, splits it, and pushes vectors to Pinecone."""
        print(f"Indexing {filename} to Pinecone...")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(pages)
        
        # Add metadata (filename)
        for chunk in chunks:
            chunk.metadata["source_file"] = filename
            
        # Add to Pinecone Vector Database
        self.vector_store.add_documents(chunks)
        return len(chunks)

    def ask_question(self, query: str):
        """Retrieves relevant chunks from Pinecone and generates an answer."""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        
        system_prompt = (
            "You are Lexica-AI, an expert document analysis assistant.\n"
            "Use the following pieces of retrieved context to answer the question.\n"
            "If you don't know the answer, just say that you don't know. Do not hallucinate.\n\n"
            "{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        docs = retriever.invoke(query)
        context_str = "\n\n".join(doc.page_content for doc in docs)
        
        prompt_value = prompt.invoke({"context": context_str, "input": query})
        response = self.llm.invoke(prompt_value)
        
        sources = []
        for doc in docs:
            source_info = {
                "page": doc.metadata.get("page", 0),
                "file": doc.metadata.get("source_file", "Unknown"),
                "content_preview": doc.page_content[:150] + "..."
            }
            if source_info not in sources:
                sources.append(source_info)
                
        return {
            "answer": response.content,
            "sources": sources
        }

rag_engine = RagEngine()
