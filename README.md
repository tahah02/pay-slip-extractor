# Payslip Extractor API

A FastAPI-based service for extracting payslip information from PDF documents using OCR technology. Supports multiple languages including English and Malay.

## Features

- **PDF Upload**: Upload payslip PDFs for processing
- **Multi-Language OCR**: Supports English and Malay text extraction
- **Field Extraction**: Automatically extracts:
  - Employee Name
  - ID Number (NRIC/IC)
  - Gross Income
  - Net Income
  - Total Deductions
  - Month/Year Period
- **Async Processing**: Background processing with status tracking
- **Multiple OCR Engines**: PaddleOCR, EasyOCR, Tesseract support
- **Confidence Scoring**: Provides confidence scores for extracted data

## Installation

### Prerequisites
- Python 3.13+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pay-slip-extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
pip list | grep -E "numpy|paddleocr|fastapi"
```

## Configuration

The extraction patterns and keywords are configured in `config/payslip_extraction_config.json`. This file includes:

- **Keywords**: In English and Malay for field identification
- **Regex Patterns**: For matching specific field formats
- **Fallback Patterns**: Alternative patterns for field extraction
- **Exclusion Keywords**: To avoid false matches
- **OCR Settings**: Language and preprocessing options

### Supported Languages
- English (en)
- Malay (ms)
- Chinese (ch)
- Multi-language (en, ms)

## Running the API

### Development Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Upload Payslip
**POST** `/api/upload`

Upload a PDF payslip for processing.

**Request:**
- Content-Type: multipart/form-data
- Body: PDF file

**Response:**
```json
{
  "status": "processing",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully. Processing started."
}
```

### 2. Get Results
**GET** `/api/result/{upload_id}`

Retrieve extraction results using the upload_id.

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

### 3. Check Status
**GET** `/api/status/{upload_id}`

Check the processing status of an upload.

**Response:**
```json
{
  "status": "processing",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Status: processing"
}
```

### 4. Health Check
**GET** `/api/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "type": "payslip-extractor"
}
```

## Using Postman

A Postman collection is included: `Postman_Collection.json`

### Import Steps:
1. Open Postman
2. Click "Import"
3. Select `Postman_Collection.json`
4. Use the pre-configured requests

### Workflow:
1. **Upload Payslip**: Upload a PDF file
2. **Copy upload_id** from response
3. **Get Results**: Use the upload_id to retrieve extracted data

## Project Structure

```
pay-slip-extractor/
├── app/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   ├── schemas.py         # Pydantic models
│   │   └── __init__.py
│   ├── main.py                # FastAPI app
│   └── __init__.py
├── core/
│   ├── ocr_engine.py          # OCR implementations
│   └── __init__.py
├── extractors/
│   ├── payslip_extractor.py   # Payslip field extraction
│   └── __init__.py
├── utils/
│   ├── pdf_processor.py       # PDF to image conversion
│   ├── text_cleaner.py        # Text preprocessing
│   └── __init__.py
├── config/
│   └── payslip_extraction_config.json  # Extraction patterns
├── uploads/
│   ├── raw/                   # Original PDFs
│   └── processed/             # Converted images
├── output/
│   └── json/                  # Extraction results
├── requirements.txt
├── Postman_Collection.json
└── README.md
```

## Supported OCR Engines

### PaddleOCR (Default)
- Best for Asian languages (Malay, Chinese)
- Faster processing
- Lower memory usage

### EasyOCR
- Good multilingual support
- Higher accuracy for some languages

### Tesseract
- Traditional OCR engine
- Requires system installation

## Configuration Examples

### Change OCR Engine
In `app/api/routes.py`, modify the `_process_payslip` function:

```python
# Use EasyOCR instead
ocr_engine = get_ocr_engine("easyocr", language="ms")

# Use Tesseract
ocr_engine = get_ocr_engine("tesseract", language="msa")
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

## Troubleshooting

### PaddleOCR Issues
```bash
# Clear cache
rm -rf ~/.paddleocr

# Reinstall
pip install --upgrade paddleocr
```

### PDF Processing Errors
- Ensure PDF is not corrupted
- Check file permissions
- Verify PDF is readable

### Memory Issues
- Reduce DPI in `config/payslip_extraction_config.json`
- Process smaller PDFs
- Use EasyOCR instead of PaddleOCR

## Performance Tips

1. **Batch Processing**: Process multiple files sequentially
2. **Image Quality**: Higher DPI = better accuracy but slower
3. **Language Selection**: Specify correct language for faster processing
4. **Caching**: OCR models are cached after first use

## License

MIT License

## Support

For issues or questions, please create an issue in the repository.
