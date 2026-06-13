import requests
import json
from fpdf import FPDF
import time

# 1. Create a sample PDF file
print("Creating a sample PDF...")
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
pdf.cell(200, 10, txt="Lexica-AI Test Document", ln=1, align='C')
pdf.cell(200, 10, txt="This document is about Artificial Intelligence and RAG systems.", ln=2, align='L')
pdf.cell(200, 10, txt="The system uses ChromaDB and Groq to process this text.", ln=3, align='L')
pdf.output("sample_test.pdf")

# 2. Test Upload Endpoint
print("\n--- Testing Upload Endpoint ---")
url_upload = "http://127.0.0.1:8000/api/upload"
with open("sample_test.pdf", "rb") as f:
    files = {"file": ("sample_test.pdf", f, "application/pdf")}
    try:
        response = requests.post(url_upload, files=files)
        print("Upload Status Code:", response.status_code)
        print("Upload Response:", response.text)
    except Exception as e:
        print("Failed to connect to backend:", e)

# 3. Test Ask Endpoint
print("\n--- Testing Ask Endpoint ---")
time.sleep(1) # wait a second for indexing
url_ask = "http://127.0.0.1:8000/api/ask"
payload = {"query": "What is this document about?"}
try:
    response = requests.post(url_ask, json=payload)
    print("Ask Status Code:", response.status_code)
    print("Ask Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Failed to connect to backend:", e)
