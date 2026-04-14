# Payslip Extractor - Quick Start Guide

## 🚀 Start the API

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
```

API will run on: **http://localhost:8005**

## 📋 2 Endpoints Only

### 1️⃣ Upload Payslip PDF
**POST** `http://localhost:8005/api/upload`

Upload a PDF file and get an `upload_id`.

**Using cURL:**
```bash
curl -X POST "http://localhost:8005/api/upload" \
  -F "file=@/path/to/payslip.pdf"
```

**Response:**
```json
{
  "status": "processing",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully. Processing started."
}
```

### 2️⃣ Get Results
**GET** `http://localhost:8005/api/result/{upload_id}`

Get extraction results using the `upload_id` from step 1.

**Using cURL:**
```bash
curl -X GET "http://localhost:8005/api/result/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_type": "pdf",
  "total_documents": 1,
  "documents": [
    {
      "document_number": 1,
      "document_type": "payslip",
      "extracted_data": {
        "name": "John Doe",
        "id_number": "123456-12-1234",
        "gross_income": "5000.00",
        "net_income": "4000.00",
        "total_deduction": "1000.00",
        "month_year": "01/2024"
      },
      "confidence_score": 0.95,
      "text_length": 1500
    }
  ],
  "summary": {
    "payslips": 1,
    "other": 0,
    "average_confidence": 0.95
  },
  "processing_completed_at": "2024-01-15T10:30:00",
  "original_file": "raw/550e8400-e29b-41d4-a716-446655440000.pdf",
  "total_text_length": 1500
}
```

## 🧪 Using Postman

1. Import `Postman_Collection.json` into Postman
2. Use "1. Upload Payslip PDF" request
3. Select your PDF file
4. Send and copy the `upload_id`
5. Use "2. Get Extraction Results" request
6. Replace `upload_id` in URL with your copied ID
7. Send and get results

## ⚙️ Configuration

### Change OCR Language
Edit `app/api/routes.py` line ~115:

```python
# For Malay (default)
ocr_engine = get_ocr_engine("paddleocr", language="ms")

# For English
ocr_engine = get_ocr_engine("paddleocr", language="en")

# For Chinese
ocr_engine = get_ocr_engine("paddleocr", language="ch")
```

### Add Custom Keywords
Edit `config/payslip_extraction_config.json`:

```json
{
  "payslip": {
    "name": {
      "keywords": [
        "name",
        "nama",
        "your_custom_keyword"
      ]
    }
  }
}
```

## 📁 File Structure

```
pay-slip-extractor/
├── app/
│   ├── api/
│   │   ├── routes.py          # 2 endpoints
│   │   └── schemas.py         # Response models
│   └── main.py                # FastAPI app (port 8005)
├── core/
│   └── ocr_engine.py          # OCR engines
├── extractors/
│   └── payslip_extractor.py   # Extraction logic
├── utils/
│   ├── pdf_processor.py       # PDF handling
│   └── text_cleaner.py        # Text preprocessing
├── config/
│   └── payslip_extraction_config.json
├── uploads/
│   ├── raw/                   # Original PDFs
│   └── processed/             # Converted images
├── output/
│   └── json/                  # Results
├── requirements.txt
├── Postman_Collection.json
└── QUICK_START.md
```

## 🔧 Troubleshooting

### Port 8005 already in use
```bash
# Use different port
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8006
```

### PaddleOCR not found
```bash
pip install paddleocr
```

### PDF conversion fails
```bash
pip install pymupdf
```

### Still processing error (202)
- Wait a few seconds and try again
- Processing time depends on PDF size and OCR engine

## 📊 Extracted Fields

- **Name**: Employee name
- **ID Number**: NRIC/IC format (123456-12-1234)
- **Gross Income**: Total salary before deductions
- **Net Income**: Take-home salary
- **Total Deduction**: Sum of all deductions
- **Month/Year**: Payslip period (MM/YYYY)

## ✅ Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 202 | Still processing |
| 400 | Bad request / Processing failed |
| 404 | Upload not found |
| 500 | Server error |

---

**Ready to use!** 🎉
