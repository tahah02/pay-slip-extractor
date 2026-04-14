import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self):
        self.extra_spaces_pattern = re.compile(r'\s+')
        self.special_chars_pattern = re.compile(r'[^\w\s\-./:%]')
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = self.extra_spaces_pattern.sub(' ', text)
        text = text.strip()
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        text = self._correct_ocr_errors(text)
        
        return text
    
    def _correct_ocr_errors(self, text: str) -> str:
        ocr_corrections = {
            'O': '0',
            'l': '1',
            'S': '5',
            'Z': '2',
            'B': '8',
            'I': '1',
        }
        
        for pattern in [r'(\d{6})[O0l1S5Z2B8I]{2}(\d{4})', r'[\d,]*[O0l1S5Z2B8I]{2}(?=\.\d{2})']:
            def fix_match(match):
                text_match = match.group(0)
                for wrong, correct in ocr_corrections.items():
                    text_match = text_match.replace(wrong, correct)
                return text_match
            
            text = re.sub(pattern, fix_match, text)
        
        return text
    
    def clean_field_value(self, value: str) -> str:
        if not value:
            return ""
        
        value = self.extra_spaces_pattern.sub(' ', value).strip()
        return value
    
    def extract_lines(self, text: str) -> list:
        lines = text.split('\n')
        return [line.strip() for line in lines if line.strip()]
    
    def normalize_currency(self, value: str) -> Optional[str]:
        if not value:
            return None
        
        value = value.replace('RM', '').replace('rm', '').strip()
        value = value.replace(',', '')
        match = re.search(r'[\d,]+\.?\d*', value)
        if match:
            return match.group(0).replace(',', '')
        
        return None
    
    def normalize_id_number(self, value: str) -> Optional[str]:
        if not value:
            return None
        
        value = value.replace(' ', '').replace('-', '')
        
        if len(value) == 12 and value.isdigit():
            return f"{value[:6]}-{value[6:8]}-{value[8:]}"
        
        return value
    
    def normalize_date(self, value: str) -> Optional[str]:
        if not value:
            return None
        
        match = re.search(r'(\d{1,2})/(\d{4})', value)
        if match:
            month = match.group(1).zfill(2)
            year = match.group(2)
            return f"{month}/{year}"
        
        return None
