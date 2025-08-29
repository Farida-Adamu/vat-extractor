from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
import json
from datetime import datetime
import pandas as pd
from io import BytesIO

app = FastAPI(title="VAT Document Extractor")

@app.get("/")
def read_root():
    return {"message": "VAT extraction API is running!"}

@app.post("/extract")
async def extract_document(file: UploadFile = File(...), output_format: str = "json"):
    """
    Extract VAT data and return as JSON or Excel
    output_format: "json" or "excel"
    """
    contents = await file.read()
    
    # This is where you'll add real extraction logic
    # For now, mock data based on Luxembourg VAT form structure
    extracted_data = {
        # Company Information
        "vat_number": "LU12345678",
        "company_name": "Example Company SA",
        "address": "123 Route d'Arlon",
        "country_code": "LU",
        "postal_code": "1234",
        "city": "Luxembourg",
        
        # Return Period
        "year": "2025",
        "period_from": "01/01/2025",
        "period_to": "31/12/2025",
        
        # Key fields from the form (matching the actual field numbers)
        "field_012_overall_turnover": 500000.00,
        "field_001_inhouse_manufactured": 300000.00,
        "field_002_goods_not_manufactured": 200000.00,
        "field_004_services": 0.00,
        "field_013_intracommunity_supply": 50000.00,
        "field_014_exports": 75000.00,
        "field_022_taxable_turnover": 375000.00,
        
        # Tax calculations
        "field_037_taxable_17_percent": 375000.00,
        "field_046_tax_17_percent": 63750.00,
        "field_076_total_tax_due": 63750.00,
        
        # Deductible tax
        "field_077_vat_invoiced": 45000.00,
        "field_093_total_input_tax": 45000.00,
        "field_102_total_deductible": 45000.00,
        
        # Final calculation
        "field_105_amount_due_or_refund": 18750.00,
        
        # Metadata
        "extraction_timestamp": datetime.now().isoformat(),
        "filename": file.filename,
        "confidence": 0.95
    }
    
    if output_format == "excel":
        # Convert to DataFrame (single row)
        df = pd.DataFrame([extracted_data])
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Extracted_Data', index=False)
            
            # Add a mapping sheet showing field numbers to descriptions
            field_mapping = pd.DataFrame({
                'Field_Number': ['012', '001', '002', '013', '014', '022', '037', '046', '076', '093', '102', '105'],
                'Description': [
                    'Overall Turnover',
                    'Inhouse Manufactured Goods',
                    'Goods Not Manufactured Inhouse',
                    'Intra-Community Supply',
                    'Exports',
                    'Taxable Turnover',
                    'Taxable Amount at 17%',
                    'Tax at 17%',
                    'Total Tax Due',
                    'Total Input Tax',
                    'Total Deductible Tax',
                    'Amount Due/Refund'
                ]
            })
            field_mapping.to_excel(writer, sheet_name='Field_Mapping', index=False)
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                "Content-Disposition": f"attachment; filename=vat_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    
    else:  # Default JSON response
        return extracted_data

@app.post("/extract-batch")
async def extract_batch(files: list[UploadFile] = File(...)):
    """
    Process multiple VAT returns and return as single Excel with one row per document
    This mimics your PwC workflow but automated
    """
    all_extractions = []
    
    for file in files:
        contents = await file.read()
        
        # Extract each document (mock data for now)
        extraction = {
            "filename": file.filename,
            "vat_number": f"LU{hash(file.filename) % 100000000:08d}",
            "company_name": f"Company from {file.filename}",
            "year": "2025",
            "overall_turnover": 500000.00,
            "taxable_turnover": 375000.00,
            "total_tax_due": 63750.00,
            "total_deductible": 45000.00,
            "net_position": 18750.00,
            "extraction_timestamp": datetime.now().isoformat()
        }
        all_extractions.append(extraction)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_extractions)
    
    # Create Excel file
    output = BytesIO()
    df.to_excel(output, sheet_name='VAT_Returns', index=False)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            "Content-Disposition": f"attachment; filename=vat_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )

@app.get("/example-excel")
def get_example_excel():
    """
    Download an example of what the extracted Excel looks like
    """
    # Create sample data
    sample_data = {
        "vat_number": "LU12345678",
        "company_name": "Example Company SA",
        "year": "2025",
        "period": "Annual",
        "overall_turnover": 1000000.00,
        "taxable_turnover": 750000.00,
        "vat_rate": 0.17,
        "total_tax_due": 127500.00,
        "total_deductible": 95000.00,
        "net_vat_position": 32500.00,
        "status": "To Pay"
    }
    
    df = pd.DataFrame([sample_data])
    
    output = BytesIO()
    df.to_excel(output, sheet_name='Example_VAT_Extract', index=False)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            "Content-Disposition": "attachment; filename=example_vat_extract.xlsx"
        }
    )