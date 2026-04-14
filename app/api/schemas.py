from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class PayslipData(BaseModel):
    name: Optional[str] = None
    id_number: Optional[str] = None
    gross_income: Optional[str] = None
    net_income: Optional[str] = None
    total_deduction: Optional[str] = None
    month_year: Optional[str] = None


class DocumentExtraction(BaseModel):
    document_number: int
    document_type: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    text_length: int


class ExtractionSummary(BaseModel):
    payslips: int
    other: int
    average_confidence: float


class ExtractionResult(BaseModel):
    upload_id: str
    file_type: str
    total_documents: int
    documents: List[DocumentExtraction]
    summary: ExtractionSummary
    processing_completed_at: datetime
    original_file: str
    total_text_length: int


class UploadResponse(BaseModel):
    status: str
    upload_id: str
    message: str = "File uploaded successfully"


class StatusResponse(BaseModel):
    status: str
    upload_id: str
    message: Optional[str] = None
    detected_language: Optional[str] = None
    language_confidence: Optional[float] = 0.0
    result: Optional[ExtractionResult] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    details: Optional[str] = None
