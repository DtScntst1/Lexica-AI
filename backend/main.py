from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os

from rag_engine import rag_engine

app = FastAPI(title="Lexica-AI Backend")

# Allow Next.js frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/docs", exist_ok=True)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Lexica-AI API is running"}

import tempfile

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # Create a temporary file to store the upload (Serverless compatible)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            
        # Index the document using the temp file
        chunks_indexed = rag_engine.index_document(temp_file_path, file.filename)
        
        # Instantly delete the file to save cloud memory
        os.remove(temp_file_path)
        
        return {
            "message": "Document successfully indexed to Cloud Vector Database.",
            "filename": file.filename,
            "chunks_processed": chunks_indexed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

@app.post("/api/ask")
async def ask_question(request: QueryRequest):
    try:
        response = rag_engine.ask_question(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")
