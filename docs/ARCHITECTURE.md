# Payslip Extraction System - Architecture

## System Overview

Payslip extraction system that processes PDF documents using hybrid approach (pdfplumber + OCR) to extract structured data from Malaysian payslips.

## Architecture Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP POST /api/upload
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  ┌───────────────────────────────────┐  │
│  │      Upload Handler               │  │
│  │  - Validate PDF                   │  │
│  │  - Generate UUID                  │  │
│  │  - Save to uploads/raw/           │  │
│  │  - Trigger async processing       │  │
│  └───────────┬───────────────────────┘  │
└──────────────┼──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      Processing Pipeline                 │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  1. PDF Type Detection             │ │
│  │     (PDFPlumber Engine)            │ │
│  │     - Check extractable text       │ │
│  │     - Digital vs Scanned           │ │
│  └────────┬───────────────────────────┘ │
│           │                              │
│     ┌─────┴─────┐                       │
│     │           │                       │
│  Digital     Scanned                    │
│     │           │                       │
│     ▼           ▼                       │
│  ┌─────┐   ┌─────────────────────────┐ │
│  │Fast │   │   OCR Pipeline          │ │
│  │Path │   │                         │ │
│  └──┬──┘   │  ┌──────────────────┐  │ │
│     │      │  │ PDF → Images     │  │ │
│     │      │  │ (PyMuPDF 300DPI) │  │ │
│     │      │  └────────┬─────────┘  │ │
│     │      │           │             │ │
│     │      │           ▼             │ │
│     │      │  ┌──────────────────┐  │ │
│     │      │  │ Preprocessing    │  │ │
│     │      │  │ - Grayscale      │  │ │
│     │      │  │ - Noise removal  │  │ │
│     │      │  │ - Contrast boost │  │ │
│     │      │  │ - Binarization   │  │ │
│     │      │  │ - Sharpening     │  │ │
│     │      │  └────────┬─────────┘  │ │
│     │      │           │             │ │
│     │      │           ▼             │ │
│     │      │  ┌──────────────────┐  │ │
│     │      │  │ OCR Engine       │  │ │
│     │      │  │ (EasyOCR/Paddle) │  │ │
│     │      │  └────────┬─────────┘  │ │
│     │      └───────────┘             │ │
│     │                                 │ │
│     └──────────┬────────────────────┘ │
│                │                       │
│                ▼                       │
│  ┌──────────────────────────────────┐ │
│  │     Text Extraction              │ │
│  │  - Clean text                    │ │
│  │  - Extract tokens with coords    │ │
│  └────────┬─────────────────────────┘ │
│           │                            │
│           ▼                            │
│  ┌──────────────────────────────────┐ │
│  │   Field Extraction               │ │
│  │                                  │ │
│  │  ┌────────────────────────────┐ │ │
│  │  │ Spatial Extraction         │ │ │
│  │  │ (PyMuPDF page objects)     │ │ │
│  │  │ - Name from top area       │ │ │
│  │  │ - ID by position           │ │ │
│  │  │ - Amounts by labels        │ │ │
│  │  └──────────┬─────────────────┘ │ │
│  │             │                    │ │
│  │             ▼                    │ │
│  │  ┌────────────────────────────┐ │ │
│  │  │ Regex Pattern Matching     │ │ │
│  │  │ (Fallback)                 │ │ │
│  │  │ - Keywords search          │ │ │
│  │  │ - Pattern matching         │ │ │
│  │  │ - OCR typo handling        │ │ │
│  │  └──────────┬─────────────────┘ │ │
│  └─────────────┼───────────────────┘ │
│                │                      │
│                ▼                      │
│  ┌──────────────────────────────────┐ │
│  │   Data Validation                │ │
│  │  - Numeric range checks          │ │
│  │  - Format validation             │ │
│  │  - Math validation               │ │
│  │  - Calculate missing fields      │ │
│  └────────┬─────────────────────────┘ │
└───────────┼──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│      Result Storage                  │
│  - Save JSON to output/json/         │
│  - Update processing state           │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│   Client polls GET /api/result/{id}  │
│   Returns extracted data             │
└──────────────────────────────────────┘
```

## Core Components

### 1. API Layer (`app/api/`)

**routes.py**
- Upload endpoint: Receives PDF, generates UUID, triggers processing
- Result endpoint: Returns extraction results
- Async processing: Non-blocking document processing

**schemas.py**
- Request/response models
- Data validation with Pydantic

### 2. PDF Processing (`core/`)

**pdfplumber_engine.py**
- Digital PDF detection
- Fast text extraction (1-2 sec)
- Token extraction with coordinates
- Table extraction support

**ocr_engine.py**
- Multiple OCR engines: EasyOCR, PaddleOCR, Tesseract
- Abstract base class for extensibility
- Coordinate-based text extraction
- Confidence scores

### 3. Image Processing (`utils/`)

**pdf_processor.py**
- PDF to image conversion (PyMuPDF)
- DPI configuration (default 300)
- Preprocessing integration

**image_preprocessor.py**
- Grayscale conversion
- Noise reduction (fastNlMeansDenoising)
- Contrast enhancement (CLAHE)
- Binarization (Otsu's method)
- Sharpening filter

**text_cleaner.py**
- Unicode normalization
- Whitespace cleanup
- Special character handling

### 4. Extraction Logic (`extractors/`)

**payslip_extractor.py**

Main extraction methods:
- `extract_payslip_fields()`: Entry point
- `_extract_with_spatial()`: Uses PyMuPDF page objects
- `_extract_payslip_with_regex()`: Fallback regex patterns
- `_extract_currency_field()`: Amount extraction with exclusions
- `_calculate_total_deduction()`: Sum individual deductions
- `_validate_extracted_data()`: Data validation

**spatial_extractor.py** (`utils/`)
- Position-based extraction
- Label-value pair detection
- Coordinate-based field extraction

### 5. Configuration (`config/`)

**ocr_config.json**
- OCR engine selection
- Language settings
- Preprocessing options
- Performance tuning

**extraction_config.json**
- Field definitions
- Keywords (multilingual)
- Regex patterns
- OCR typo variations
- Validation rules

**engine_config.json**
- Server settings
- File paths
- Logging configuration

## Data Flow

### 1. Upload Phase
```
Client → FastAPI → Validate → Save → Generate UUID → Return 202
```

### 2. Processing Phase (Async)
```
PDF File
  ↓
Check Type (pdfplumber)
  ↓
├─ Digital PDF
│   ↓
│   Extract text directly
│   Extract tokens with coords
│   ↓
└─ Scanned PDF
    ↓
    Convert to images (300 DPI)
    ↓
    Preprocess images
    ↓
    OCR extraction
    ↓
Extract Fields
  ↓
├─ Spatial extraction (primary)
│   - Name from top area
│   - ID by label position
│   - Amounts by label-value pairs
│   ↓
└─ Regex extraction (fallback)
    - Pattern matching
    - Keyword search
    - Typo handling
    ↓
Validate & Calculate
  ↓
Save JSON result
```

### 3. Retrieval Phase
```
Client → GET /api/result/{id} → Return JSON
```

## Field Extraction Strategy

### Name Extraction
1. Spatial: Extract from top 20% of page
2. Regex: Match pattern `[A-Z][a-z]+ (bin|binti) [A-Z][a-z]+`
3. Validation: 3-6 words, proper case

### ID Number Extraction
1. Spatial: Find "No. K/P" label, extract right value
2. Regex: Pattern `\d{6}-\d{2}-\d{4}`
3. Validation: Format check

### Amount Extraction (Gross/Net/Deduction)
1. Spatial: Find label, extract right-aligned value
2. Regex: Multiple patterns with OCR typo variations
   - "Jumlah Pendapatan" / "Junlah Pendapatan" / "Surlah Pepdapatan"
   - "Gaji Bersih" / "Gaj: Bersil" / "Gaji Bersin"
   - "Jumlah Potongan" / "Sulab Pcrorgan"
3. Exclusion: Prevent cross-field contamination
4. Calculation: If missing, calculate from other fields
5. Validation: Range 0-999999.99, math check

### Month/Year Extraction
1. Regex: "M/S: \d{1,2}/\d{1,2}" + nearby year
2. Format: Convert to MM/YYYY
3. Validation: Month 1-12, Year 2000-2099

## Configuration System

### Hierarchical Config Loading
```
config_loader.py
  ↓
Load JSON configs
  ↓
Cache in memory
  ↓
Provide typed accessors
```

### Config Types
- **OCR Config**: Engine, language, preprocessing
- **Extraction Config**: Fields, patterns, validation
- **Engine Config**: Server, paths, logging

## Error Handling

### Levels
1. **Validation errors**: Return 400 with details
2. **Processing errors**: Mark as failed, log details
3. **OCR errors**: Fallback to alternative engine
4. **Extraction errors**: Return partial data with low confidence

### Logging
- INFO: Processing milestones
- WARNING: Validation issues, fallbacks
- ERROR: Critical failures with stack traces

## Performance Optimization

### Speed Improvements
1. **Hybrid approach**: Digital PDFs bypass OCR (10x faster)
2. **Async processing**: Non-blocking uploads
3. **Config caching**: Load once, reuse
4. **Preprocessing**: Optional, configurable

### Accuracy Improvements
1. **Image preprocessing**: Noise reduction, contrast boost
2. **Multiple patterns**: Handle OCR variations
3. **Spatial extraction**: Position-based, more reliable
4. **Validation**: Math checks, format validation
5. **Calculation fallbacks**: Derive missing fields

## Extensibility

### Adding New OCR Engine
1. Extend `OCREngine` base class
2. Implement `extract_text()` and `extract_text_with_coordinates()`
3. Add to `get_ocr_engine()` factory
4. Update config

### Adding New Field
1. Add to `extraction_config.json`:
   - Keywords
   - Patterns
   - Validation rules
2. Update `PayslipExtractor` if custom logic needed
3. Update response schema

### Adding New Preprocessing
1. Add method to `ImagePreprocessor`
2. Add config option
3. Update preprocessing pipeline

## Deployment Considerations

### Requirements
- Python 3.11+
- OpenCV for image processing
- PyMuPDF for PDF handling
- EasyOCR/PaddleOCR for OCR
- FastAPI for API server

### Environment Variables
- Server host/port
- Upload directories
- Log levels
- OCR engine selection

### Scaling
- Async processing handles concurrent uploads
- Stateless design allows horizontal scaling
- File-based storage (can migrate to S3/database)

## Security

### Input Validation
- File type check (PDF only)
- File size limits
- Sanitize filenames (UUID-based)

### Data Privacy
- Temporary file storage
- Configurable retention
- No external API calls (local OCR)

## Future Enhancements

1. **LLM Integration**: GPT/Claude for complex extraction
2. **Multi-format Support**: Images, Word docs
3. **Batch Processing**: Multiple files at once
4. **Real-time Streaming**: WebSocket updates
5. **Database Storage**: PostgreSQL for results
6. **Caching**: Redis for processed results
7. **Monitoring**: Prometheus metrics
8. **API Authentication**: JWT tokens
