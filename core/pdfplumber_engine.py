import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFPlumberEngine:
    
    def __init__(self):
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
            logger.info("PDFPlumber initialized successfully")
        except ImportError:
            logger.error("pdfplumber not installed. Install with: pip install pdfplumber")
            raise
    
    def can_extract_text(self, pdf_path: str, min_text_length: int = 100) -> bool:
        try:
            with self.pdfplumber.open(pdf_path) as pdf:
                if not pdf.pages:
                    return False
                
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                if text and len(text.strip()) >= min_text_length:
                    logger.info(f"Digital PDF detected: {len(text)} chars on first page")
                    return True
                
                logger.info("Scanned PDF detected: No extractable text")
                return False
                
        except Exception as e:
            logger.error(f"Error checking PDF type: {str(e)}")
            return False
    
    def extract_text_from_pdf(self, pdf_path: str, page_num: int = 0) -> Tuple[str, List[Dict[str, Any]]]:
        try:
            with self.pdfplumber.open(pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    logger.warning(f"Page {page_num} not found in PDF")
                    return "", []
                
                page = pdf.pages[page_num]
                
                text = page.extract_text() or ""
                
                words = page.extract_words()
                tokens = []
                
                for word in words:
                    token = {
                        'text': word['text'],
                        'bbox': [word['x0'], word['top'], word['x1'], word['bottom']],
                        'x0': word['x0'],
                        'y0': word['top'],
                        'x1': word['x1'],
                        'y1': word['bottom'],
                        'confidence': 1.0,
                        'page': page_num,
                        '_used_by': None
                    }
                    tokens.append(token)
                
                logger.info(f"Extracted {len(tokens)} tokens from page {page_num}")
                return text, tokens
                
        except Exception as e:
            logger.error(f"PDFPlumber extraction error: {str(e)}")
            return "", []
    
    def extract_tables_from_pdf(self, pdf_path: str, page_num: int = 0) -> List[List[List[str]]]:
        try:
            with self.pdfplumber.open(pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    return []
                
                page = pdf.pages[page_num]
                tables = page.extract_tables()
                
                logger.info(f"Extracted {len(tables)} tables from page {page_num}")
                return tables or []
                
        except Exception as e:
            logger.error(f"Table extraction error: {str(e)}")
            return []
