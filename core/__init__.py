"""Core extraction modules"""

from .ocr_engine import get_ocr_engine, OCREngine, PaddleOCREngine, EasyOCREngine, TesseractOCREngine

__all__ = [
    'get_ocr_engine',
    'OCREngine',
    'PaddleOCREngine',
    'EasyOCREngine',
    'TesseractOCREngine'
]
