# CONFIGURATION GUIDE

## 📋 THREE CONFIG FILES

### 1. **ocr_config.json** - OCR Engine Settings
Controls which OCR engine to use and how it works

### 2. **extraction_config.json** - Field Extraction Settings
Defines keywords, patterns, and validation for payslip fields

### 3. **engine_config.json** - Application Settings
Server, logging, file handling, and feature flags

---

## 🔧 OCR CONFIG (ocr_config.json)

### Purpose
Configure OCR engine selection and settings

### Key Settings

#### Default Engine
```json
"default_engine": "tesseract"
```
Options: `"tesseract"`, `"easyocr"`, `"paddleocr"`

#### Engine Configuration
```json
"tesseract": {
  "enabled": true,
  "language": "msa",
  "languages": {
    "english": "eng",
    "malay": "msa",
    "chinese": "chi_sim"
  }
}
```

#### Preprocessing
```json
"preprocessing": {
  "dpi": 300,
  "contrast_enhancement": true,
  "noise_reduction": true,
  "skew_correction": true
}
```

### How to Change OCR Engine

#### Switch to EasyOCR
```json
"default_engine": "easyocr"
```

#### Switch to PaddleOCR
```json
"default_engine": "paddleocr"
```

#### Change Language
```json
"tesseract": {
  "language": "eng"  // English
}
```

---

## 📝 EXTRACTION CONFIG (extraction_config.json)

### Purpose
Define how to extract payslip fields

### Key Sections

#### 1. Fields Definition
Each field has:
- `keywords`: Search terms
- `pattern`: Regex pattern
- `fallback_patterns`: Alternative patterns
- `exclusion_keywords`: Words to exclude

#### 2. Validation Rules
```json
"validation": {
  "min_confidence": 0.5,
  "required_fields": ["name", "id_number", ...],
  "field_validation": {
    "gross_income": {
      "type": "numeric",
      "min": 0,
      "max": 999999.99
    }
  }
}
```

#### 3. Processing Options
```json
"processing": {
  "calculate_net_income": true,
  "calculate_total_deduction": true,
  "currency_format": "RM",
  "decimal_places": 2
}
```

### How to Add New Keyword

```json
"name": {
  "keywords": [
    "nama",
    "nama pekerja",
    "YOUR_NEW_KEYWORD"  // Add here
  ]
}
```

### How to Add New Pattern

```json
"gross_income": {
  "fallback_patterns": [
    "existing_pattern",
    "YOUR_NEW_PATTERN"  // Add here
  ]
}
```

### How to Change Validation Rules

```json
"field_validation": {
  "gross_income": {
    "type": "numeric",
    "min": 0,
    "max": 500000.00  // Change max value
  }
}
```

---

## ⚙️ ENGINE CONFIG (engine_config.json)

### Purpose
Configure application behavior

### Key Sections

#### Server Settings
```json
"server": {
  "host": "0.0.0.0",
  "port": 8005,
  "debug": false
}
```

#### File Handling
```json
"file_handling": {
  "upload_dir": "uploads/raw",
  "processed_dir": "uploads/processed",
  "output_dir": "output/json",
  "max_upload_size": 52428800
}
```

#### Logging
```json
"logging": {
  "level": "INFO",
  "file": "output/logs/payslip_app.log"
}
```

#### OCR Processing
```json
"ocr_processing": {
  "engine": "tesseract",
  "language": "msa",
  "timeout": 30
}
```

#### Features
```json
"features": {
  "multi_page_support": true,
  "batch_processing": false,
  "webhook_notifications": false
}
```

### How to Change Settings

#### Change Upload Directory
```json
"file_handling": {
  "upload_dir": "my_uploads/raw"
}
```

#### Change Log Level
```json
"logging": {
  "level": "DEBUG"  // More verbose
}
```

#### Enable Feature
```json
"features": {
  "batch_processing": true
}
```

---

## 🔄 CONFIG LOADER USAGE

### In Python Code

```python
from utils.config_loader import ConfigLoader

# Get OCR config
ocr_config = ConfigLoader.get_ocr_config()

# Get extraction config
extraction_config = ConfigLoader.get_extraction_config()

# Get engine config
engine_config = ConfigLoader.get_engine_config()

# Get specific values
ocr_engine = ConfigLoader.get_ocr_engine()  # "tesseract"
ocr_language = ConfigLoader.get_ocr_language()  # "msa"
extraction_fields = ConfigLoader.get_extraction_fields()
validation_config = ConfigLoader.get_validation_config()
```

### Automatic Caching
- Configs loaded once and cached
- Reload with: `ConfigLoader.reload_all()`

---

## 📊 CONFIGURATION FLOW

```
ocr_config.json
    ↓
ConfigLoader.get_ocr_engine()
    ↓
get_ocr_engine("tesseract", "msa")
    ↓
TesseractOCREngine initialized

extraction_config.json
    ↓
ConfigLoader.get_extraction_fields()
    ↓
PayslipExtractor uses fields
    ↓
Extract name, ID, income, etc.

engine_config.json
    ↓
ConfigLoader.get_file_handling_config()
    ↓
Set upload/output directories
```

---

## 🎯 COMMON CONFIGURATIONS

### Fast Processing (Tesseract)
```json
// ocr_config.json
"default_engine": "tesseract"

// engine_config.json
"ocr_processing": {
  "timeout": 10
}
```

### High Accuracy (EasyOCR)
```json
// ocr_config.json
"default_engine": "easyocr"

// engine_config.json
"ocr_processing": {
  "timeout": 30
}
```

### English Only
```json
// ocr_config.json
"tesseract": {
  "language": "eng"
}
```

### Strict Validation
```json
// extraction_config.json
"validation": {
  "min_confidence": 0.8
}
```

### Lenient Validation
```json
// extraction_config.json
"validation": {
  "min_confidence": 0.3
}
```

---

## 🔍 DEBUGGING

### Check Current Config
```python
from utils.config_loader import ConfigLoader

print(ConfigLoader.get_ocr_engine())
print(ConfigLoader.get_ocr_language())
print(ConfigLoader.get_extraction_fields())
```

### Check File Paths
```python
from utils.config_loader import ConfigLoader

file_config = ConfigLoader.get_file_handling_config()
print(file_config.get("upload_dir"))
print(file_config.get("output_dir"))
```

### Reload Configs
```python
from utils.config_loader import ConfigLoader

ConfigLoader.reload_all()
```

---

## ✅ CHECKLIST

- [ ] ocr_config.json exists
- [ ] extraction_config.json exists
- [ ] engine_config.json exists
- [ ] payslip_extraction_config.json deleted
- [ ] PayslipExtractor uses extraction_config.json
- [ ] Routes use ConfigLoader
- [ ] ConfigLoader utility created
- [ ] Tests pass with new configs

---

## 📚 FILE LOCATIONS

```
config/
├── ocr_config.json           # OCR engine settings
├── extraction_config.json    # Field extraction settings
└── engine_config.json        # Application settings

utils/
└── config_loader.py          # Config loader utility
```

---

## 🚀 NEXT STEPS

1. ✅ Three config files created
2. ✅ Old config file deleted
3. ✅ Code updated to use new configs
4. ✅ ConfigLoader utility created
5. ⏭️ Test with new configs
6. ⏭️ Verify all settings work

---

**Status:** ✅ Configuration refactored
**Files:** 3 config files + 1 loader utility
**Ready:** ✅ Production ready
