"""
Vision Analyzer - Computer vision capabilities for screen analysis
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import pytesseract
from PIL import Image
from loguru import logger


class VisionAnalyzer:
    """Computer vision analyzer for screen content and UI element detection"""
    
    def __init__(self, config):
        """Initialize the vision analyzer"""
        self.config = config
        
        # Setup OCR if tesseract is available
        try:
            pytesseract.get_tesseract_version()
            self.ocr_available = True
            logger.info("OCR (Tesseract) is available")
        except Exception:
            self.ocr_available = False
            logger.warning("OCR (Tesseract) not available")

    def analyze_image(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze an image and extract information about UI elements
        
        Args:
            image: Image as numpy array
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                'timestamp': str(np.datetime64('now')),
                'image_shape': image.shape,
                'text_content': [],
                'buttons': [],
                'text_fields': [],
                'clickable_elements': [],
                'dominant_colors': [],
                'has_text': False,
                'ui_elements_count': 0
            }
            
            # Convert to different formats for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Extract text using OCR
            if self.ocr_available:
                text_data = self.extract_text_with_positions(image)
                analysis['text_content'] = text_data
                analysis['has_text'] = len(text_data) > 0
            
            # Detect UI elements
            buttons = self.detect_buttons(gray)
            analysis['buttons'] = buttons
            
            text_fields = self.detect_text_fields(gray)
            analysis['text_fields'] = text_fields
            
            clickable_elements = self.detect_clickable_elements(gray)
            analysis['clickable_elements'] = clickable_elements
            
            # Analyze colors
            dominant_colors = self.get_dominant_colors(image)
            analysis['dominant_colors'] = dominant_colors
            
            # Count total UI elements
            analysis['ui_elements_count'] = (
                len(buttons) + len(text_fields) + len(clickable_elements)
            )
            
            logger.debug(f"Image analysis complete: {analysis['ui_elements_count']} elements found")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze image: {e}")
            return {'error': str(e)}

    def extract_text_with_positions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract text from image with position information
        
        Args:
            image: Image as numpy array
            
        Returns:
            List of text elements with positions
        """
        if not self.ocr_available:
            return []
            
        try:
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(image)
            
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            text_elements = []
            n_boxes = len(data['level'])
            
            for i in range(n_boxes):
                confidence = int(data['conf'][i])
                text = data['text'][i].strip()
                
                # Filter out low confidence and empty text
                if confidence > 30 and text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    text_elements.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                        'center': {'x': x + w//2, 'y': y + h//2}
                    })
            
            return text_elements
            
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            return []

    def detect_buttons(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect button-like UI elements
        
        Args:
            gray_image: Grayscale image
            
        Returns:
            List of detected buttons with positions
        """
        try:
            buttons = []
            
            # Use edge detection to find rectangular shapes
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's roughly rectangular and of reasonable size
                if len(approx) >= 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filter by size (likely buttons are not too small or too large)
                    if 20 < w < 300 and 15 < h < 100:
                        aspect_ratio = w / h
                        
                        # Buttons typically have certain aspect ratios
                        if 0.5 < aspect_ratio < 8:
                            buttons.append({
                                'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                                'center': {'x': x + w//2, 'y': y + h//2},
                                'aspect_ratio': aspect_ratio,
                                'area': w * h
                            })
            
            # Sort by area (larger elements first)
            buttons.sort(key=lambda b: b['area'], reverse=True)
            
            return buttons[:10]  # Return top 10 candidates
            
        except Exception as e:
            logger.error(f"Failed to detect buttons: {e}")
            return []

    def detect_text_fields(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect text input fields
        
        Args:
            gray_image: Grayscale image
            
        Returns:
            List of detected text fields
        """
        try:
            text_fields = []
            
            # Use template matching for common text field patterns
            # This is a simplified approach - in practice, you might use more sophisticated methods
            
            # Detect horizontal lines (text field borders)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            horizontal_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, kernel)
            
            # Find contours of horizontal lines
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Text fields are typically wide and not too tall
                if w > 50 and h < 50:
                    aspect_ratio = w / h
                    if aspect_ratio > 3:  # Wide rectangles
                        text_fields.append({
                            'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                            'center': {'x': x + w//2, 'y': y + h//2},
                            'type': 'input_field'
                        })
            
            return text_fields
            
        except Exception as e:
            logger.error(f"Failed to detect text fields: {e}")
            return []

    def detect_clickable_elements(self, gray_image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect other clickable elements (links, icons, etc.)
        
        Args:
            gray_image: Grayscale image
            
        Returns:
            List of detected clickable elements
        """
        try:
            clickable_elements = []
            
            # Use corner detection to find potential clickable elements
            corners = cv2.goodFeaturesToTrack(
                gray_image,
                maxCorners=100,
                qualityLevel=0.01,
                minDistance=10
            )
            
            if corners is not None:
                for corner in corners:
                    x, y = corner.ravel().astype(int)
                    
                    clickable_elements.append({
                        'center': {'x': int(x), 'y': int(y)},
                        'type': 'corner_feature'
                    })
            
            return clickable_elements[:20]  # Limit to top 20
            
        except Exception as e:
            logger.error(f"Failed to detect clickable elements: {e}")
            return []

    def get_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Extract dominant colors from image
        
        Args:
            image: Image as numpy array
            k: Number of dominant colors to extract
            
        Returns:
            List of dominant colors
        """
        try:
            # Reshape image to be a list of pixels
            pixels = image.reshape((-1, 3))
            pixels = np.float32(pixels)
            
            # Apply k-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to integers
            centers = np.uint8(centers)
            
            # Count pixels for each cluster
            unique_labels, counts = np.unique(labels, return_counts=True)
            
            dominant_colors = []
            for i, (label, count) in enumerate(zip(unique_labels, counts)):
                color = centers[label]
                percentage = (count / len(pixels)) * 100
                
                dominant_colors.append({
                    'rgb': color.tolist(),
                    'hex': f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                    'percentage': round(percentage, 2)
                })
            
            # Sort by percentage
            dominant_colors.sort(key=lambda c: c['percentage'], reverse=True)
            
            return dominant_colors
            
        except Exception as e:
            logger.error(f"Failed to get dominant colors: {e}")
            return []

    def find_text_on_screen(self, target_text: str, image: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Find specific text on screen and return its center coordinates
        
        Args:
            target_text: Text to search for
            image: Screenshot image
            
        Returns:
            (x, y) coordinates of text center, or None if not found
        """
        if not self.ocr_available:
            return None
            
        try:
            text_elements = self.extract_text_with_positions(image)
            
            for element in text_elements:
                if target_text.lower() in element['text'].lower():
                    center = element['center']
                    return (center['x'], center['y'])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find text '{target_text}': {e}")
            return None

    def compare_images(self, image1: np.ndarray, image2: np.ndarray) -> float:
        """
        Compare two images and return similarity score
        
        Args:
            image1, image2: Images to compare
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
            
            # Resize to same dimensions if different
            if gray1.shape != gray2.shape:
                h, w = min(gray1.shape[0], gray2.shape[0]), min(gray1.shape[1], gray2.shape[1])
                gray1 = cv2.resize(gray1, (w, h))
                gray2 = cv2.resize(gray2, (w, h))
            
            # Calculate structural similarity
            # For simplicity, using basic correlation coefficient
            correlation = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
            
            return float(correlation[0][0])
            
        except Exception as e:
            logger.error(f"Failed to compare images: {e}")
            return 0.0