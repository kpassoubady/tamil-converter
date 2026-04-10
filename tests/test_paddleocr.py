"""
Test PaddleOCR on 2 pages of the Bharathidasan PDF.
Run: PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True python3 test_paddleocr.py

First run downloads models from HuggingFace (~100MB).
"""

import os
import time
import warnings
import logging

# Skip the slow connectivity check
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)

from pdf2image import convert_from_path
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR

Image.MAX_IMAGE_PIXELS = None

PDF_PATH = "../docs/bharathithasan/bharathi_songs_Vol_2-10-11.pdf"
DPI = 600

print("Loading PaddleOCR (lang=ta)...")
start = time.time()
ocr = PaddleOCR(lang="ta")
print(f"Loaded in {time.time() - start:.1f}s\n")

print(f"Converting PDF pages at {DPI} DPI...")
images = convert_from_path(PDF_PATH, first_page=1, last_page=2, dpi=DPI)

for page_num, img in enumerate(images, 1):
    print(f"\n{'='*60}")
    print(f"PAGE {page_num}")
    print(f"{'='*60}")

    img_array = np.array(img)
    print(f"Image size: {img_array.shape}")

    start = time.time()
    result = ocr.predict(img_array)
    elapsed = time.time() - start
    print(f"OCR completed in {elapsed:.1f}s\n")

    for item in result:
        # Debug: show what attributes are available
        if page_num == 1:
            attrs = [a for a in dir(item) if not a.startswith("_")]
            print(f"[DEBUG] OCRResult attributes: {attrs}\n")

        # Try different possible attribute names
        if hasattr(item, "rec_texts"):
            texts = item.rec_texts
            scores = item.rec_scores
        elif hasattr(item, "text"):
            texts = item.text if isinstance(item.text, list) else [item.text]
            scores = item.score if isinstance(item.score, list) else [item.score]
        elif hasattr(item, "rec_text"):
            texts = item.rec_text if isinstance(item.rec_text, list) else [item.rec_text]
            scores = item.rec_score if isinstance(item.rec_score, list) else [item.rec_score]
        else:
            print(f"[DEBUG] Full item: {item}")
            print(f"[DEBUG] item dict: {item.__dict__}" if hasattr(item, "__dict__") else "")
            continue

        print(f"{len(texts)} text regions detected:\n")
        for text, score in zip(texts, scores):
            print(f"[{score:.2f}] {text}")

print("\n\nDone!")
