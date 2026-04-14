import logging
import re
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SpatialExtractor:
    
    def __init__(self):
        self.tolerance_y = 10
        self.tolerance_x = 5
    
    def extract_field_by_position(self, page, label_text: str, search_direction: str = "right") -> Optional[str]:
        try:
            text = page.get_text()
            
            pattern = rf'{re.escape(label_text)}\s*:?\s*([^\n]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value and len(value) > 0:
                    return value
            
            blocks = page.get_text("dict")["blocks"]
            text_blocks = [b for b in blocks if b.get("type") == 0]
            
            label_bbox = None
            label_line = None
            
            for block in text_blocks:
                for line in block.get("lines", []):
                    line_text = "".join([span["text"] for span in line.get("spans", [])])
                    if label_text.lower() in line_text.lower():
                        label_bbox = line["bbox"]
                        label_line = line
                        break
                if label_bbox:
                    break
            
            if not label_bbox:
                logger.debug(f"Label not found: {label_text}")
                return None
            
            if search_direction == "right":
                return self._find_value_right(text_blocks, label_bbox)
            elif search_direction == "below":
                return self._find_value_below(text_blocks, label_bbox)
            
            return None
            
        except Exception as e:
            logger.error(f"Spatial extraction error for {label_text}: {str(e)}")
            return None
    
    def _find_value_right(self, text_blocks: List[Dict], label_bbox: tuple) -> Optional[str]:
        candidates = []
        
        for block in text_blocks:
            for line in block.get("lines", []):
                line_bbox = line["bbox"]
                
                if abs(line_bbox[1] - label_bbox[1]) < self.tolerance_y:
                    if line_bbox[0] > label_bbox[2] + self.tolerance_x:
                        line_text = "".join([span["text"] for span in line.get("spans", [])])
                        candidates.append({
                            "text": line_text,
                            "distance": line_bbox[0] - label_bbox[2]
                        })
        
        if candidates:
            closest = min(candidates, key=lambda x: x["distance"])
            value = closest["text"].strip()
            value = value.lstrip(":").strip()
            return value if value else None
        
        return None
    
    def _find_value_below(self, text_blocks: List[Dict], label_bbox: tuple) -> Optional[str]:
        candidates = []
        
        for block in text_blocks:
            for line in block.get("lines", []):
                line_bbox = line["bbox"]
                
                if line_bbox[1] > label_bbox[3]:
                    if abs(line_bbox[0] - label_bbox[0]) < 50:
                        line_text = "".join([span["text"] for span in line.get("spans", [])])
                        candidates.append({
                            "text": line_text,
                            "distance": line_bbox[1] - label_bbox[3]
                        })
        
        if candidates:
            closest = min(candidates, key=lambda x: x["distance"])
            return closest["text"].strip()
        
        return None
    
    def extract_name_from_page(self, page) -> Optional[str]:
        try:
            text = page.get_text()
            
            name_patterns = [
                r'Nama\s*:\s*([A-Z][a-z]+(?:\s+(?:bin|binti)\s+[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+)*)',
                r'Nama\s*:\s*([A-Z\s]+(?:BIN|BINTI)\s+[A-Z\s]+)',
                r'Nama\s*:\s*([A-Z][A-Za-z\s]+?)(?:\s+No\.|\s+Jawatan)',
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    if name and len(name) > 3 and name not in ["Nama", "No", "Pendapatan", "Potongan"]:
                        return name
            
            return None
            
        except Exception as e:
            logger.error(f"Name extraction error: {str(e)}")
            return None
    
    def clean_numeric_value(self, value: str) -> Optional[str]:
        if not value:
            return None
        
        cleaned = re.sub(r'\s+', '', value)
        cleaned = cleaned.replace(',', '')
        
        match = re.search(r'([\d]+\.[\d]{2})', cleaned)
        if match:
            return match.group(1)
        
        return None
