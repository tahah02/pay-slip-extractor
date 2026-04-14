"""
Payslip application configuration
"""

import os
from pathlib import Path

# Server Configuration
HOST = os.getenv("PAYSLIP_HOST", "0.0.0.0")
PORT = int(os.getenv("PAYSLIP_PORT", 8005))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# File Configuration
UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = UPLOAD_DIR / "processed"
RAW_DIR = UPLOAD_DIR / "raw"
OUTPUT_DIR = Path("output")
JSON_OUTPUT_DIR = OUTPUT_DIR / "json"
LOG_DIR = OUTPUT_DIR / "logs"

# Create directories if they don't exist
for directory in [UPLOAD_DIR, PROCESSED_DIR, RAW_DIR, OUTPUT_DIR, JSON_OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "docx", "doc"}

# Processing Configuration
REQUEST_TIMEOUT = 300  # 5 minutes
PROCESSING_TIMEOUT = 300  # 5 minutes

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOG_DIR / "payslip_app.log"

# Template Configuration
DEFAULT_TEMPLATE = "payslip"
EXTRACTION_CONFIG = "config/payslip_extraction_config.json"

# Application Info
APP_NAME = "Payslip Extraction System"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "FastAPI-based payslip extraction system using OCR"
