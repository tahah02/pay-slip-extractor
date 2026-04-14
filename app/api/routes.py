"""
Payslip extraction API routes
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
import asyncio
import json
from pathlib import Path

from app.api.schemas import UploadResponse, StatusResponse, ErrorResponse, ExtractionResult
from extractors.payslip_extractor import PayslipExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["payslip"])

# Global state for processing
processing_state = {}
payslip_extractor = PayslipExtractor()

# File paths
UPLOAD_DIR = Path("uploads/raw")
PROCESSED_DIR = Path("uploads/processed")
OUTPUT_DIR = Path("output/json")

# Create directories
for directory in [UPLOAD_DIR, PROCESSED_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a payslip PDF for extraction
    
    Args:
        file: PDF file to process
        
    Returns:
        Upload response with upload_id
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        import uuid
        upload_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{upload_id}.pdf"
        
        # Save file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File uploaded: {upload_id}")
        
        # Start background processing
        processing_state[upload_id] = "processing"
        asyncio.create_task(_process_payslip(upload_id, str(file_path)))
        
        return UploadResponse(
            status="processing",
            upload_id=upload_id,
            message="File uploaded successfully. Processing started."
        )
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{upload_id}", response_model=StatusResponse)
async def check_status(upload_id: str):
    """
    Check processing status
    
    Args:
        upload_id: Upload ID to check
        
    Returns:
        Status response
    """
    try:
        status = processing_state.get(upload_id, "unknown")
        
        if status == "unknown":
            raise HTTPException(status_code=404, detail="Upload not found")
        
        return StatusResponse(
            status=status,
            upload_id=upload_id,
            message=f"Status: {status}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{upload_id}", response_model=ExtractionResult)
async def get_result(upload_id: str):
    """
    Get extraction results
    
    Args:
        upload_id: Upload ID to retrieve
        
    Returns:
        Extraction result
    """
    try:
        status = processing_state.get(upload_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        if status == "processing":
            raise HTTPException(status_code=202, detail="Still processing")
        
        if status == "failed":
            raise HTTPException(status_code=400, detail="Processing failed")
        
        result_path = OUTPUT_DIR / f"{upload_id}.json"
        
        with open(result_path, 'r') as f:
            result = json.load(f)
        
        return ExtractionResult(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Result retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "type": "payslip-extractor"
    }


async def _process_payslip(upload_id: str, file_path: str):
    """Background task to process payslip"""
    try:
        logger.info(f"Starting payslip processing: {upload_id}")
        
        # Extract text from PDF
        from utils.pdf_processor import PDFProcessor
        from utils.text_cleaner import TextCleaner
        from core.ocr_engine import get_ocr_engine
        
        # Convert PDF to images
        images = PDFProcessor.pdf_to_images(file_path, str(PROCESSED_DIR / upload_id))
        
        # Extract text using OCR
        ocr_engine = get_ocr_engine("paddleocr")
        text_cleaner = TextCleaner()
        
        documents = []
        total_text_length = 0
        confidence_scores = []
        
        for doc_num, image_path in enumerate(images, 1):
            text = ocr_engine.extract_text(image_path)
            text = text_cleaner.clean_text(text)
            total_text_length += len(text)
            
            # Extract payslip fields
            extracted_data = payslip_extractor.extract_payslip_fields(text)
            confidence = payslip_extractor.calculate_confidence(extracted_data)
            confidence_scores.append(confidence)
            
            documents.append({
                "document_number": doc_num,
                "document_type": "payslip",
                "extracted_data": extracted_data,
                "confidence_score": confidence,
                "text_length": len(text)
            })
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        result = {
            "upload_id": upload_id,
            "file_type": "pdf",
            "total_documents": len(documents),
            "documents": documents,
            "summary": {
                "payslips": len(documents),
                "other": 0,
                "average_confidence": round(avg_confidence, 2)
            },
            "processing_completed_at": datetime.now().isoformat(),
            "original_file": f"raw/{upload_id}.pdf",
            "total_text_length": total_text_length
        }
        
        # Save result
        result_path = OUTPUT_DIR / f"{upload_id}.json"
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        processing_state[upload_id] = "completed"
        logger.info(f"Payslip processing completed: {upload_id}")
    
    except Exception as e:
        logger.error(f"Payslip processing error: {str(e)}")
        processing_state[upload_id] = "failed"
