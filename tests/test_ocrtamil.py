"""
Test ocr-tamil on 2 pages of the Bharathidasan PDF.
Run: python3 test_ocrtamil.py

First run downloads models (~270MB total).
"""

import time
from pdf2image import convert_from_path
from PIL import Image
from ocr_tamil.ocr import OCR

Image.MAX_IMAGE_PIXELS = None

PDF_PATH = "../docs/bharathithasan/bharathi_songs_Vol_2-10-11.pdf"
DPI = 600

print("Loading ocr-tamil...")
start = time.time()
ocr = OCR()
print(f"Loaded in {time.time() - start:.1f}s\n")

print(f"Converting PDF pages at {DPI} DPI...")
images = convert_from_path(PDF_PATH, first_page=1, last_page=2, dpi=DPI)

for page_num, img in enumerate(images, 1):
    print(f"\n{'='*60}")
    print(f"PAGE {page_num}")
    print(f"{'='*60}")

    # ocr-tamil works with file paths
    tmp_path = f"/tmp/ocr_tamil_test_page_{page_num}.png"
    img.save(tmp_path)
    print(f"Image saved to {tmp_path}")

    start = time.time()
    result = ocr.predict(tmp_path)
    elapsed = time.time() - start
    print(f"OCR completed in {elapsed:.1f}s\n")

    if isinstance(result, list):
        for line in result:
            print(line)
    else:
        print(result)

print("\n\nDone!")
