"""
Payslip-specific field extraction logic
Handles extraction of payslip fields with payslip-specific patterns and validation
"""

import logging
import re
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class PayslipExtractor:
    """Extracts payslip-specific fields from text"""
    
    def __init__(self, config_path: str = "config/payslip_extraction_config.json"):
        self.config = self._load_config(config_path)
        self.used_tokens = set()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load payslip extraction configuration"""
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found: {config_path}, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def extract_payslip_fields(self, text: str, tokens: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract payslip fields from text
        
        Args:
            text: Extracted text from OCR
            tokens: Optional token data with coordinates
            
        Returns:
            Dictionary with extracted payslip fields
        """
        self.used_tokens = set()
        return self._extract_payslip_with_regex(text)
    
    def _extract_payslip_with_regex(self, text: str) -> Dict[str, Any]:
        """Extract payslip fields using regex patterns"""
        self.used_tokens = set()
        
        payslip_config = self.config.get("payslip", {})
        
        extracted_name = self._extract_field(text, "name", payslip_config)
        extracted_id = self._extract_field(text, "id_number", payslip_config)
        extracted_gross = self._extract_currency_field(text, "gross_income", payslip_config)
        extracted_net = self._extract_currency_field(text, "net_income", payslip_config)
        extracted_deduction = self._extract_currency_field(text, "total_deduction", payslip_config)
        
        if not extracted_deduction:
            calculated_deduction = self._calculate_total_deduction(text, payslip_config)
            if calculated_deduction:
                logger.info(f"Using calculated deduction from items: {calculated_deduction}")
                extracted_deduction = calculated_deduction
        
        extracted_month_year = self._extract_field(text, "month_year", payslip_config)
        
        extracted = {
            "name": extracted_name,
            "id_number": extracted_id,
            "gross_income": self._clean_currency(extracted_gross),
            "net_income": self._clean_currency(extracted_net),
            "total_deduction": self._clean_currency(extracted_deduction),
            "month_year": extracted_month_year
        }
        
        # Calculate net income if not found
        net_income_cleaned = self._clean_currency(extracted["net_income"])
        if net_income_cleaned == "0.00" or not extracted["net_income"]:
            try:
                gross = float(extracted["gross_income"])
                deduction = float(extracted["total_deduction"])
                calculated_net = gross - deduction
                extracted["net_income"] = f"{calculated_net:.2f}"
                logger.info(f"Calculated net_income: {extracted['net_income']}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not calculate net_income: {str(e)}")
                extracted["net_income"] = net_income_cleaned
        else:
            extracted["net_income"] = net_income_cleaned
        
        return extracted
    
    def _extract_field(self, text: str, field_name: str, config: Dict[str, Any]) -> Optional[str]:
        """Extract field using keywords and patterns"""
        field_config = config.get(field_name, {})
        keywords = field_config.get("keywords", [])
        pattern = field_config.get("pattern")
        fallback_patterns = field_config.get("fallback_patterns", [])
        
        # Try keywords first
        for keyword in keywords:
            if pattern:
                match = re.search(rf'{keyword}[:\s]*({pattern})', text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            else:
                match = re.search(rf'{keyword}[:\s]*([^\n]+)', text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        # Try fallback patterns
        for pattern in fallback_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_currency_field(self, text: str, field_name: str, config: Dict[str, Any]) -> Optional[str]:
        """Extract currency field with validation"""
        field_config = config.get(field_name, {})
        patterns = field_config.get("fallback_patterns", [])
        exclusion_keywords = field_config.get("exclusion_keywords", [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                matched_text = match.group(0)
                value_str = match.group(1).strip()
                
                if value_str in self.used_tokens:
                    logger.debug(f"Skipping already used token for {field_name}: {value_str}")
                    continue
                
                # Check exclusion keywords
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end].lower()
                
                if any(keyword in context for keyword in exclusion_keywords):
                    logger.info(f"Rejected {field_name} - exclusion keyword found")
                    continue
                
                self.used_tokens.add(value_str)
                logger.info(f"Extracted {field_name}: {value_str}")
                return value_str
        
        return None
    
    def _calculate_total_deduction(self, text: str, config: Dict[str, Any]) -> Optional[str]:
        """Calculate total deduction from individual deduction items"""
        deduction_config = config.get("total_deduction", {})
        item_patterns = deduction_config.get("deduction_item_patterns", [])
        
        if not item_patterns:
            return None
        
        total = 0.0
        found_items = []
        
        for pattern in item_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                value_str = match.group(1).strip()
                numeric_value = self._parse_number(value_str)
                
                if numeric_value and numeric_value > 0:
                    total += numeric_value
                    found_items.append(f"{match.group(0)}: {numeric_value}")
                    logger.debug(f"Found deduction item: {numeric_value}")
        
        if total > 0 and len(found_items) >= 2:
            logger.info(f"Calculated total deduction: {total:.2f} from {len(found_items)} items")
            return f"{total:.2f}"
        
        return None
    
    def _parse_number(self, value_str: str) -> Optional[float]:
        """Parse number from string"""
        try:
            cleaned = value_str.replace(",", "").replace("RM", "").strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _clean_currency(self, value: Optional[str]) -> str:
        """Clean and format currency value"""
        if not value:
            return "0.00"
        
        try:
            cleaned = value.replace(",", "").replace("RM", "").strip()
            numeric = float(cleaned)
            return f"{numeric:.2f}"
        except (ValueError, AttributeError):
            return "0.00"
    
    def calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted payslip data"""
        required_fields = ["name", "id_number", "gross_income", "net_income", "total_deduction", "month_year"]
        
        filled_fields = sum(1 for field in required_fields if extracted_data.get(field) and extracted_data.get(field) != "0.00")
        confidence = filled_fields / len(required_fields)
        
        logger.info(f"Payslip confidence: {confidence:.2f} ({filled_fields}/{len(required_fields)} fields)")
        return round(confidence, 2)
