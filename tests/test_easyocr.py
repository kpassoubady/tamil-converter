"""
Test EasyOCR on 2 pages of the Bharathidasan PDF.
Run: python3 test_easyocr.py

This may take a few minutes on first run (downloads ~180MB of models).
M4 Pro with 24GB RAM should handle this fine.
"""

import time
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import easyocr

Image.MAX_IMAGE_PIXELS = None

PDF_PATH = "../docs/bharathithasan/bharathi_songs_Vol_2-10-11.pdf"
DPI = 600

print("Loading EasyOCR reader (ta + en)...")
start = time.time()
try:
    reader = easyocr.Reader(["ta", "en"], gpu=False)
except RuntimeError as e:
    if "size mismatch" in str(e):
        print(f"\nERROR: EasyOCR Tamil model is incompatible with installed version.")
        print(f"This is a known bug in easyocr 1.7.2 with Tamil language support.")
        print(f"\nWorkaround — try downgrading:")
        print(f"  pip3 install easyocr==1.7.1")
        print(f"\nOr try Tamil-only (without English):")
        reader = None
        try:
            reader = easyocr.Reader(["ta"], gpu=False)
            print("Loaded with Tamil-only mode.\n")
        except RuntimeError:
            print("Tamil-only also failed. EasyOCR is not usable for Tamil currently.")
            print("Skipping EasyOCR test.")
            exit(1)
    else:
        raise
print(f"Reader loaded in {time.time() - start:.1f}s\n")

print(f"Converting PDF pages at {DPI} DPI...")
images = convert_from_path(PDF_PATH, first_page=1, last_page=2, dpi=DPI)

for page_num, img in enumerate(images, 1):
    print(f"\n{'='*60}")
    print(f"PAGE {page_num}")
    print(f"{'='*60}")

    img_array = np.array(img)
    print(f"Image size: {img_array.shape}")

    start = time.time()
    results = reader.readtext(img_array)
    elapsed = time.time() - start
    print(f"OCR completed in {elapsed:.1f}s — {len(results)} text regions\n")

    for _, text, conf in results:
        print(f"[{conf:.2f}] {text}")

print("\n\nDone!")
