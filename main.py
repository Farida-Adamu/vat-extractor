from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import json
from datetime import datetime

# Create your API
app = FastAPI(title="VAT Document Extractor")

# Your first endpoint - just to test if API is running
@app.get("/")
def read_root():
    return {"message": "Your VAT extraction API is running!"}

# The main endpoint - accepts a file upload
@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    # Read the uploaded file
    contents = await file.read()
    
    # For now, we're just detecting what type of file it is
    # Later you'll add real OCR/extraction here
    if file.filename.endswith('.pdf'):
        # Fake "extracted" data for PDFs (you'll replace with real OCR)
        return {
            "status": "success",
            "document_type": "VAT Return",
            "filename": file.filename,
            "size_bytes": len(contents),
            "extracted_data": {
                "vat_number": "LU12345678",
                "company": "Example Company",
                "total_vat": 15000.00,
                "period": "Q3 2024",
                "extracted_at": datetime.now().isoformat()
            },
            "confidence": 0.92,
            "message": "PDF processed successfully (mock data for now)"
        }
    else:
        # For non-PDF files
        return {
            "status": "received",
            "filename": file.filename,
            "size_bytes": len(contents),
            "file_type": file.content_type,
            "message": "File received - OCR not yet implemented for this type",
            "timestamp": datetime.now().isoformat()
        }

# Example endpoint to show what the API will return when fully built
@app.get("/example")
def show_example_output():
    return {
        "info": "This is what your API will return when fully built",
        "vat_return": {
            "vat_number": "LU12345678",
            "company_name": "Example Company SA",
            "period": "Q3 2024",
            "total_sales": 150000.00,
            "vat_collected": 25500.00,
            "vat_paid": 12000.00,
            "net_vat": 13500.00,
            "extracted_fields": 15,
            "confidence": 0.95
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "api_version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }