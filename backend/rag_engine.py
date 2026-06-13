import os
from dotenv import load_dotenv

load_dotenv()

# Ensure TensorFlow does not conflict with HuggingFace on Windows
os.environ['USE_TF'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Configuration
CHROMA_PATH = "uploads/chroma_db"
os.makedirs(CHROMA_PATH, exist_ok=True)

class RagEngine:
    def __init__(self):
        # We use a lightweight open-source embedding model for fast local processing
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(persist_directory=CHROMA_PATH, embedding_function=self.embeddings)
        
        # Initialize Groq LLM if API key is present
        self.llm = None
        if "GROQ_API_KEY" in os.environ:
            self.llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
            
    def index_document(self, file_path: str):
        """Loads a PDF, splits it into chunks, and stores it in the Vector DB."""
        print(f"Indexing {file_path}...")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(pages)
        
        # Add metadata (filename)
        filename = os.path.basename(file_path)
        for chunk in chunks:
            chunk.metadata["source_file"] = filename
            
        # Add to ChromaDB
        self.vector_store.add_documents(chunks)
        self.vector_store.persist()
        return len(chunks)

    def ask_question(self, query: str):
        """Retrieves relevant chunks and generates an answer."""
        if not self.llm:
            return {
                "answer": "System Error: GROQ_API_KEY environment variable is not set. Please set it to enable the AI Agent.",
                "sources": []
            }

        # Create the Retrieval Chain using LCEL directly
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        
        # System prompt instructing the AI to use context
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
        
        # Manually execute to avoid deprecated langchain.chains dependencies
        docs = retriever.invoke(query)
        context_str = "\n\n".join(doc.page_content for doc in docs)
        
        prompt_value = prompt.invoke({"context": context_str, "input": query})
        response = self.llm.invoke(prompt_value)
        
        # Extract unique sources for citations
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
