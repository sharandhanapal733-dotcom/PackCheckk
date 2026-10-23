import os
import logging
from typing import List, Dict, Any, Optional
from rapidocr_onnxruntime import RapidOCR

logger = logging.getLogger(__name__)

# Initialize RapidOCR singleton
_rapid_ocr_instance: Optional[RapidOCR] = None

def get_ocr_engine() -> RapidOCR:
    global _rapid_ocr_instance
    if _rapid_ocr_instance is None:
        try:
            _rapid_ocr_instance = RapidOCR()
            logger.info("RapidOCR (PaddleOCR models) initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RapidOCR: {e}")
            raise
    return _rapid_ocr_instance

def run_ocr(image_path: str) -> List[Dict[str, Any]]:
    """
    Executes OCR on the given image path.
    Returns structured results:
    [
        {
            "text": "MRP ₹50.00",
            "confidence": 0.94,
            "box": [100, 200, 350, 250], # [xmin, ymin, xmax, ymax]
            "polygon": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
            "line_number": 1,
            "engine": "RapidOCR (PaddleOCR-v4)"
        },
        ...
    ]
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    ocr_results: List[Dict[str, Any]] = []

    try:
        engine = get_ocr_engine()
        result, elapse = engine(image_path)

        if result:
            for idx, item in enumerate(result):
                # item format: [box_points, text, score]
                # box_points: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                box_points = item[0]
                text = str(item[1]).strip()
                confidence = round(float(item[2]), 4)

                # Compute axis-aligned bounding box [xmin, ymin, xmax, ymax]
                xs = [pt[0] for pt in box_points]
                ys = [pt[1] for pt in box_points]
                xmin, xmax = int(min(xs)), int(max(xs))
                ymin, ymax = int(min(ys)), int(max(ys))

                ocr_results.append({
                    "text": text,
                    "confidence": confidence,
                    "box": [xmin, ymin, xmax, ymax],
                    "polygon": [[int(pt[0]), int(pt[1])] for pt in box_points],
                    "line_number": idx + 1,
                    "engine": "PaddleOCR (RapidOCR-v4)"
                })

        logger.info(f"RapidOCR completed: detected {len(ocr_results)} text lines in {elapse}s")
        return ocr_results

    except Exception as e:
        logger.warning(f"PaddleOCR primary engine encountered error: {e}. Attempting Tesseract fallback.")
        # Attempt fallback to PyTesseract if available
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(image_path)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            n_boxes = len(data['text'])
            line_idx = 1
            for i in range(n_boxes):
                txt = data['text'][i].strip()
                conf = float(data['conf'][i])
                if txt and conf > 0:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    ocr_results.append({
                        "text": txt,
                        "confidence": round(conf / 100.0, 4),
                        "box": [x, y, x + w, y + h],
                        "polygon": [[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
                        "line_number": line_idx,
                        "engine": "Tesseract OCR (Fallback)"
                    })
                    line_idx += 1
            return ocr_results
        except Exception as fallback_err:
            logger.error(f"Fallback OCR also failed: {fallback_err}")
            if ocr_results:
                return ocr_results
            raise RuntimeError(f"OCR processing failed on image {image_path}: {e}")
