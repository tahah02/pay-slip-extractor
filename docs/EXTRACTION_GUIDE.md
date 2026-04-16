# Payslip Extraction Guide

## Overview

Complete guide to understanding and extending the payslip extraction logic.

## Extraction Flow

```
Input: PDF Document
  ↓
Step 1: PDF Type Detection
  ↓
Step 2: Text Extraction (Digital or OCR)
  ↓
Step 3: Field Extraction (Spatial + Regex)
  ↓
Step 4: Data Validation & Calculation
  ↓
Output: Structured JSON
```

## Step-by-Step Process

### Step 1: PDF Type Detection

**File**: `core/pdfplumber_engine.py`

**Method**: `can_extract_text()`

**Logic**:
```python
1. Open PDF with pdfplumber
2. Extract text from first page
3. Check text length >= 100 chars
4. Return True (digital) or False (scanned)
```

**Decision**:
- Digital PDF → Fast path (pdfplumber)
- Scanned PDF → OCR path (EasyOCR)

### Step 2: Text Extraction

#### Path A: Digital PDF (pdfplumber)

**File**: `core/pdfplumber_engine.py`

**Method**: `extract_text_from_pdf()`

**Process**:
```python
1. Open PDF page
2. Extract text: page.extract_text()
3. Extract words with coordinates: page.extract_words()
4. Build tokens list with bbox, confidence=1.0
5. Return (text, tokens)
```

**Speed**: 1-2 seconds per page

**Accuracy**: 99-100% (native text)

#### Path B: Scanned PDF (OCR)

**Files**: 
- `utils/pdf_processor.py` - PDF to images
- `utils/image_preprocessor.py` - Image enhancement
- `core/ocr_engine.py` - OCR extraction

**Process**:
```python
1. Convert PDF to images (300 DPI)
   - PyMuPDF: page.get_pixmap()
   
2. Preprocess images
   - Grayscale conversion
   - Noise reduction: cv2.fastNlMeansDenoising()
   - Contrast: cv2.createCLAHE()
   - Binarization: cv2.threshold(OTSU)
   - Sharpening: cv2.filter2D()
   
3. OCR extraction
   - EasyOCR: reader.readtext()
   - Extract text + coordinates + confidence
   
4. Return text
```

**Speed**: 8-15 seconds per page

**Accuracy**: 85-95% (depends on quality)

### Step 3: Field Extraction

**File**: `extractors/payslip_extractor.py`

**Entry Point**: `extract_payslip_fields(text, tokens, page)`

#### Extraction Strategy

**Two-tier approach**:
1. **Primary**: Spatial extraction (position-based)
2. **Fallback**: Regex extraction (pattern-based)

#### 3.1 Spatial Extraction

**File**: `utils/spatial_extractor.py`

**Method**: `extract_field_by_position(page, label, direction)`

**Logic**:
```python
1. Search for label text in page
2. Get label bounding box
3. Extract value in specified direction (right/below)
4. Return cleaned value
```

**Example**:
```
Label: "Jumlah Pendapatan"  [x0, y0, x1, y1]
Direction: right
Search area: [x1, y0, x1+200, y1]
Extract: "9,252.92"
```

**Advantages**:
- More reliable than regex
- Handles OCR errors better
- Position-based, not text-dependent

#### 3.2 Regex Extraction

**Method**: `_extract_currency_field(text, field_name)`

**Logic**:
```python
1. Load field config (keywords, patterns, exclusions)
2. Try each pattern in order
3. Check exclusion keywords in context
4. Mark token as used (prevent reuse)
5. Return first valid match
```

**Pattern Structure**:
```json
{
  "gross_income": {
    "keywords": ["jumlah pendapatan", "junlah pendapatan"],
    "fallback_patterns": [
      "(?:Jumlah|Junlah)\\s*Pendapatan\\s*([\\d\\s,]+[\\.-]?\\s*\\d{2})"
    ],
    "exclusion_keywords": ["bersih", "potongan"]
  }
}
```

**Pattern Explanation**:
- `(?:Jumlah|Junlah)`: Match either spelling (OCR typo)
- `\\s*`: Optional whitespace
- `Pendapatan`: Keyword
- `([\\d\\s,]+[\\.-]?\\s*\\d{2})`: Capture amount
  - `[\\d\\s,]+`: Digits, spaces, commas
  - `[\\.-]?`: Optional dot or dash (decimal)
  - `\\s*\\d{2}`: Two decimal digits

**Exclusion Logic**:
```python
1. Extract 100 chars before and after match
2. Check if exclusion keywords present
3. If found, skip this match
4. Prevents: "Gaji Bersih" matching "gross_income"
```

### Step 4: Field-Specific Extraction

#### 4.1 Name Extraction

**Method**: `_extract_name_from_text(text)`

**Logic**:
```python
1. Split text into lines
2. Take first 5 lines only
3. For each line:
   - Check length 10-100 chars
   - Match pattern: [A-Z][a-z]+ (bin|binti) [A-Z][a-z]+
   - Validate 3-6 words
4. Return first valid match
```

**Example**:
```
Input: "Ahmad Zuhairi Bin Hj Zakaria"
Pattern: ^([A-Z][a-z]+(?:\s+(?:bin|binti)\s+[A-Z][a-z]+)*)
Match: "Ahmad Zuhairi Bin Hj Zakaria"
```

#### 4.2 ID Number Extraction

**Spatial**:
```python
1. Find "No. K/P" or "No KP" label
2. Extract value to the right
3. Return if matches format
```

**Regex**:
```python
Pattern: \d{6}-\d{2}-\d{4}
Example: 680414-01-5125
```

#### 4.3 Amount Extraction (Gross/Net/Deduction)

**Spatial**:
```python
1. Find label: "Jumlah Pendapatan"
2. Extract right-aligned value
3. Clean: remove spaces, commas
4. Return numeric string
```

**Regex with Typo Handling**:
```python
Patterns for "Jumlah Pendapatan":
- "Jumlah Pendapatan"  (correct)
- "Junlah Pendapatan"  (OCR typo)
- "Surlah Pepdapatan"  (OCR error)
- "Sumlah Pepdapatan"  (OCR error)

All patterns capture: [\d\s,]+[\\.-]?\s*\d{2}
```

**Exclusion Strategy**:
```python
gross_income excludes: ["bersih", "potongan"]
net_income excludes: ["jumlah pendapatan", "potongan"]
total_deduction excludes: ["bersih", "pendapatan"]
```

**Token Reuse Prevention**:
```python
1. Mark extracted value in used_tokens set
2. Skip if already used
3. Ensures each amount used once
```

#### 4.4 Deduction Calculation

**Method**: `_calculate_total_deduction(text)`

**Logic**:
```python
1. Search for deduction items:
   - KWSP/EPF
   - Perkeso/SOCSO
   - Cukai/Tax
   - PIIN/Perumahan
   
2. Extract each amount
3. Sum all items
4. Return if >= 2 items found
5. Use as fallback if direct extraction fails
```

**Example**:
```
Text:
  "KWSP 548.45"
  "PIIN 250.00"
  "Perumahan 700.00"
  
Calculation: 548.45 + 250.00 + 700.00 = 1498.45
```

#### 4.5 Month/Year Extraction

**Method**: `_extract_field(text, "month_year")`

**Logic**:
```python
1. Find "M/S: 1/1" pattern
2. Extract month (pad to 2 digits)
3. Search nearby for 4-digit year
4. Combine: "01/2025"
5. Fallback: Use current year
```

**Format Conversion**:
```python
Input: "M/S: 1/1" + "2025" nearby
Output: "01/2025"

Input: "Januari 2025"
Output: "01/2025"
```

### Step 5: Data Cleaning

**Method**: `_clean_currency(value)`

**Logic**:
```python
1. Remove spaces: "9 , 252 . 92" → "9,252.92"
2. Remove commas: "9,252.92" → "9252.92"
3. Remove "RM": "RM 9252.92" → "9252.92"
4. Replace dash with dot: "9252-92" → "9252.92"
5. Convert to float: 9252.92
6. Format: "9252.92"
```

### Step 6: Validation & Calculation

**Method**: `_validate_extracted_data(data)`

**Validation Rules**:

1. **Numeric Range**:
```python
gross_income: 0 - 999999.99
net_income: 0 - 999999.99
total_deduction: 0 - 999999.99
```

2. **Format Validation**:
```python
id_number: \d{6}-\d{2}-\d{4}
month_year: \d{2}/\d{4}
```

3. **Math Validation**:
```python
Check: gross - deduction ≈ net (tolerance: ±1.00)
If mismatch: Log warning, don't fail
```

4. **Missing Field Calculation**:
```python
If net_income == 0.00:
  net_income = gross_income - total_deduction
  
If total_deduction == 0.00:
  total_deduction = sum(deduction_items)
```

### Step 7: Confidence Calculation

**Method**: `calculate_confidence(extracted_data)`

**Logic**:
```python
Required fields: [name, id_number, gross_income, 
                  net_income, total_deduction, month_year]

filled_fields = count(field != null and field != "0.00")
confidence = filled_fields / 6

Examples:
- All fields: 6/6 = 1.00 (100%)
- 4 fields: 4/6 = 0.67 (67%)
- 2 fields: 2/6 = 0.33 (33%)
```

## Configuration Guide

### Adding New Pattern

**File**: `config/extraction_config.json`

**Example**: Add pattern for "Total Earnings"

```json
{
  "gross_income": {
    "keywords": [
      "jumlah pendapatan",
      "total earnings"  // NEW
    ],
    "fallback_patterns": [
      "(?:Jumlah|Junlah)\\s*Pendapatan\\s*([\\d\\s,]+[\\.-]?\\s*\\d{2})",
      "Total\\s+Earnings\\s+([\\d\\s,]+[\\.-]?\\s*\\d{2})"  // NEW
    ]
  }
}
```

### Adding OCR Typo Variation

**Example**: "Jumlah" → "Jumlsh" (OCR error)

```json
{
  "keywords": [
    "jumlah pendapatan",
    "jumlsh pendapatan"  // NEW typo
  ],
  "fallback_patterns": [
    "(?:Jumlah|Junlah|Jumlsh)\\s*Pendapatan\\s*([\\d\\s,]+[\\.-]?\\s*\\d{2})"
  ]
}
```

### Adding Exclusion Keyword

**Example**: Prevent "Gaji Pokok" matching "gross_income"

```json
{
  "gross_income": {
    "exclusion_keywords": [
      "bersih",
      "potongan",
      "pokok"  // NEW
    ]
  }
}
```

## Troubleshooting

### Issue: Field not extracting

**Debug Steps**:

1. **Check raw OCR text**:
```python
# Add logging in routes.py
logger.info(f"OCR Text: {text}")
```

2. **Check pattern match**:
```python
# Test pattern in Python
import re
pattern = r"Jumlah\s+Pendapatan\s+([\d\s,]+[\\.-]?\s*\d{2})"
match = re.search(pattern, text, re.IGNORECASE)
print(match.group(1) if match else "No match")
```

3. **Check exclusions**:
```python
# Verify exclusion keywords not present
context = text[match.start()-100:match.end()+100]
print("Context:", context)
```

4. **Check token reuse**:
```python
# Log used tokens
logger.info(f"Used tokens: {self.used_tokens}")
```

### Issue: Wrong field extracted

**Solution**: Add exclusion keyword

```json
{
  "net_income": {
    "exclusion_keywords": [
      "gross",
      "jumlah pendapatan",
      "total earnings"  // Add conflicting keywords
    ]
  }
}
```

### Issue: OCR accuracy low

**Solutions**:

1. **Enable preprocessing**:
```json
{
  "preprocessing": {
    "contrast_enhancement": true,
    "noise_reduction": true,
    "binarization": true
  }
}
```

2. **Increase DPI**:
```python
# In pdf_processor.py
dpi = 600  # Default: 300
```

3. **Try different OCR engine**:
```json
{
  "default_engine": "paddleocr"  // or "easyocr" or "tesseract"
}
```

## Performance Tips

### Speed Optimization

1. **Use pdfplumber for digital PDFs** (10x faster)
2. **Disable preprocessing** if accuracy acceptable
3. **Lower DPI** for faster processing (200 DPI)
4. **Cache OCR models** (already implemented)

### Accuracy Optimization

1. **Enable all preprocessing** options
2. **Increase DPI** to 600
3. **Use EasyOCR** (best accuracy)
4. **Add more pattern variations**
5. **Use spatial extraction** (more reliable)

## Best Practices

### Pattern Design

1. **Start specific, add variations**:
```python
# Good
"Jumlah Pendapatan"  # Exact
"Junlah Pendapatan"  # Common typo
"Sumlah Pepdapatan"  # OCR error

# Bad
".*Pendapatan.*"  # Too broad
```

2. **Use non-capturing groups**:
```python
# Good
(?:Jumlah|Junlah)  # Don't capture alternatives

# Bad
(Jumlah|Junlah)  # Captures group
```

3. **Handle spacing flexibly**:
```python
\\s*  # Zero or more spaces
\\s+  # One or more spaces
```

### Exclusion Strategy

1. **Add conflicting keywords**
2. **Check 100 char context**
3. **Test with real data**

### Validation

1. **Always validate ranges**
2. **Check format patterns**
3. **Verify math relationships**
4. **Calculate missing fields**

## Extension Guide

### Adding New Field

**Step 1**: Add to config
```json
{
  "employee_code": {
    "keywords": ["no pekerja", "employee code"],
    "pattern": "\\d{6}",
    "required": false,
    "fallback_patterns": [
      "(?:No|Employee)\\s+(?:Pekerja|Code)[:\\s]+(\\d{6})"
    ]
  }
}
```

**Step 2**: Update extractor (if custom logic needed)
```python
def extract_payslip_fields(self, text, tokens, page):
    # ... existing code ...
    extracted["employee_code"] = self._extract_field(text, "employee_code")
    return extracted
```

**Step 3**: Update schema
```python
class ExtractionResult(BaseModel):
    # ... existing fields ...
    employee_code: Optional[str] = None
```

### Adding New OCR Engine

**Step 1**: Create engine class
```python
class MyOCREngine(OCREngine):
    def __init__(self, language: str = "en"):
        # Initialize engine
        pass
    
    def extract_text(self, image_path: str) -> str:
        # Extract text
        pass
    
    def extract_text_with_coordinates(self, image_path: str) -> List[Dict]:
        # Extract with coords
        pass
```

**Step 2**: Add to factory
```python
def get_ocr_engine(engine_name: str, language: str) -> OCREngine:
    if engine_name == "myocr":
        return MyOCREngine(language)
    # ... existing engines ...
```

**Step 3**: Update config
```json
{
  "default_engine": "myocr",
  "engines": {
    "myocr": {
      "enabled": true,
      "language": "en"
    }
  }
}
```

## Summary

**Extraction Pipeline**:
1. Detect PDF type (digital vs scanned)
2. Extract text (pdfplumber or OCR)
3. Extract fields (spatial + regex)
4. Validate and calculate
5. Return structured data

**Key Techniques**:
- Hybrid approach (fast + accurate)
- Two-tier extraction (spatial + regex)
- OCR typo handling
- Token reuse prevention
- Math validation
- Missing field calculation

**Configuration-driven**:
- No code changes for new patterns
- Easy to extend
- Maintainable
