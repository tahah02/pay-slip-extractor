import os
from pathlib import Path

HOST = os.getenv("PAYSLIP_HOST", "0.0.0.0")
PORT = int(os.getenv("PAYSLIP_PORT", 8005))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = UPLOAD_DIR / "processed"
RAW_DIR = UPLOAD_DIR / "raw"
OUTPUT_DIR = Path("output")
JSON_OUTPUT_DIR = OUTPUT_DIR / "json"
LOG_DIR = OUTPUT_DIR / "logs"

for directory in [UPLOAD_DIR, PROCESSED_DIR, RAW_DIR, OUTPUT_DIR, JSON_OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "docx", "doc"}

REQUEST_TIMEOUT = 300
PROCESSING_TIMEOUT = 300

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOG_DIR / "payslip_app.log"

DEFAULT_TEMPLATE = "payslip"
EXTRACTION_CONFIG = "config/payslip_extraction_config.json"

APP_NAME = "Payslip Extraction System"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "FastAPI-based payslip extraction system using OCR"
