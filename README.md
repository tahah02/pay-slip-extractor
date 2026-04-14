# Payslip Extraction System

**Version**: 2.0.0  
**Status**: Development  
**Port**: 8005

A standalone FastAPI-based system for extracting structured data from payslip PDF documents using OCR and intelligent pattern matching.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python -m app.main
```

Server runs on: http://localhost:8005

## API Endpoints

- `POST /api/upload` - Upload payslip PDF
- `GET /api/status/{upload_id}` - Check processing status
- `GET /api/result/{upload_id}` - Get extraction results
- `GET /health` - Health check

## Extracted Fields

1. name - Employee name
2. id_number - NRIC/ID number
3. gross_income - Gross salary
4. net_income - Net salary
5. total_deduction - Total deductions
6. month_year - Pay period (MM/YYYY)

## Documentation

See `docs/` folder for complete documentation.
