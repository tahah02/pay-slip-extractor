import logging
from pathlib import Path
from typing import List
import fitz

logger = logging.getLogger(__name__)

class PDFProcessor:
    @staticmethod
    def pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 300) -> List[str]:
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                image_path = output_path / f"page_{page_num + 1}.png"
                pix.save(str(image_path))
                image_paths.append(str(image_path))
                logger.info(f"Converted page {page_num + 1} to {image_path}")
            
            doc.close()
            return image_paths
        except Exception as e:
            logger.error(f"PDF to image conversion error: {str(e)}")
            raise
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
                text += "\n--- Page Break ---\n"
            
            doc.close()
            return text
        except Exception as e:
            logger.error(f"PDF text extraction error: {str(e)}")
            raise
