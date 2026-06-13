<div align="center">
  <h1>🚀 Lexica-AI</h1>
  <h3>Enterprise-Grade Retrieval-Augmented Generation (RAG) System</h3>
  
  <p>
    <b>A Full-Stack AI application that allows users to upload massive PDF documents and interact with them in real-time, backed by exact page and document citations.</b>
  </p>

  <div>
    <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain" />
  </div>
</div>

<div align="center">
  <img src="./assets/lexica_mockup.png" alt="Lexica-AI Application Interface" width="800"/>
</div>

---

## 🌟 Key Features

- **🧠 Advanced RAG Engine:** Leverages LangChain Expression Language (LCEL) to natively connect Vector Databases to Large Language Models.
- **📚 Multi-Document Ingestion:** Instantly parses and semantically chunks large PDF files using `RecursiveCharacterTextSplitter`.
- **☁️ Serverless Vector Database:** Uses **Pinecone** to permanently store and retrieve vectorized documents with lightning speed.
- **⚡ Ultra-Fast Inference:** Integrated with the Groq API (LLaMA-3 70B) for lightning-fast natural language generation.
- **🎯 Precise Citations:** An engineered extraction pipeline that completely eliminates AI hallucination by citing the exact source file and page number.
- **💎 Premium Glassmorphism UI:** A sleek, modern, dark-mode web interface built entirely from scratch with Vanilla CSS and React.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[User Uploads PDF] -->|Next.js Vercel| B[FastAPI Backend on Render]
    B --> C{LangChain Splitter}
    C -->|Semantic Chunks| D[Pinecone Inference Embeddings]
    D --> E[(Pinecone Serverless DB)]
    
    F[User Asks Question] -->|Next.js Frontend| G[FastAPI Backend]
    G --> H{Query Vectorization}
    H -->|Similarity Search| E
    E -->|Top-K Context Chunks| I[LLaMA-3 70B via Groq]
    I -->|Generates Answer & Citations| G
    G -->|JSON Response| F
```

---

## 🛠️ Tech Stack

**Frontend (Vercel):**
- Next.js (App Router)
- React.js
- Custom Glassmorphism Vanilla CSS

**Backend (Render):**
- Python 3.11
- FastAPI / Uvicorn
- LangChain (LCEL Pipeline)
- Pinecone (Cloud Vector Store)
- Pinecone Inference API (Embeddings)
- Groq API (Inference)

---

## 🚀 Getting Started

### 1. Start the Backend API
Navigate to the `backend` directory and start the Uvicorn server:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Start the Frontend Application
Open a new terminal, navigate to the `frontend` directory, and start the Next.js app:
```bash
cd frontend
npm install
npm run dev
```

### 3. Open the App
Visit `http://localhost:3000` in your web browser. Drag and drop a PDF into the glowing panel, and start chatting with your data!

---
*Built with ❤️ for modern ML Engineering portfolios.*
