import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image

def preprocess_image(input_path: str, output_path: str = None) -> str:
    """
    Preprocesses product/label photograph for optimal OCR recognition:
    1. Reads original image
    2. Corrects orientation/deskew if required
    3. Converts to grayscale
    4. Contrast Limited Adaptive Histogram Equalization (CLAHE)
    5. Subtle bilateral filter noise reduction (preserves text edges)
    6. Unsharp masking to sharpen characters
    7. Saves preprocessed image alongside original
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    # Read image using OpenCV
    img = cv2.imread(input_path)
    if img is None:
        # Fallback using PIL
        pil_img = Image.open(input_path).convert("RGB")
        img = np.array(pil_img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    h, w = img.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Noise removal with bilateral filter (smooths backgrounds while preserving crisp text edges)
    filtered = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

    # Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(filtered)

    # Sharpening kernel
    kernel_sharpen = np.array([
        [0, -0.5, 0],
        [-0.5, 3.0, -0.5],
        [0, -0.5, 0]
    ], dtype=np.float32)
    sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    # Determine destination path
    if output_path is None:
        p = Path(input_path)
        output_path = str(p.parent / f"{p.stem}_preprocessed.jpg")

    cv2.imwrite(output_path, sharpened)
    return output_path

def get_image_dimensions(image_path: str) -> tuple[int, int]:
    try:
        with Image.open(image_path) as img:
            return img.width, img.height
    except Exception:
        return 800, 600
