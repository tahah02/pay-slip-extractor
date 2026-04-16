import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.dpi = self.config.get('dpi', 300)
        self.contrast_enhancement = self.config.get('contrast_enhancement', True)
        self.noise_reduction = self.config.get('noise_reduction', True)
        self.binarization = self.config.get('binarization', True)
    
    def preprocess(self, image_path: str, output_path: str = None) -> str:
        try:
            image = cv2.imread(image_path)
            
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return image_path
            
            processed = self._apply_preprocessing(image)
            
            if output_path is None:
                output_path = image_path.replace('.png', '_processed.png')
            
            cv2.imwrite(output_path, processed)
            logger.info(f"Preprocessed image saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Preprocessing error: {str(e)}")
            return image_path
    
    def _apply_preprocessing(self, image: np.ndarray) -> np.ndarray:
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if self.noise_reduction:
            gray = cv2.fastNlMeansDenoising(gray, h=10)
        
        if self.contrast_enhancement:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
        
        if self.binarization:
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        
        return sharpened
    
    def batch_preprocess(self, image_paths: list) -> list:
        processed_paths = []
        for image_path in image_paths:
            processed_path = self.preprocess(image_path)
            processed_paths.append(processed_path)
        return processed_paths
