# Tamil PDF to Markdown Converter

Tools for converting Tamil PDF files into readable UTF-8 Markdown.

Supports two types of Tamil PDFs:

| PDF Type                     | Tool                 | How it works                                |
| ---------------------------- | -------------------- | ------------------------------------------- |
| TSCII-encoded (1990s-2000s)  | `tamil-converter.py` | Extracts text + TSCII to Unicode conversion |
| Scanned / image-based        | `pdf-2-markdown.py`  | OCR with Tesseract + optional LLM cleanup   |

---

## Prerequisites

### System dependencies

Install these via Homebrew (macOS) before proceeding:

```bash
# Required for pdf-2-markdown.py (OCR + PDF rendering)
brew install tesseract tesseract-lang poppler
```

- **tesseract** - OCR engine
- **tesseract-lang** - Language packs including Tamil
- **poppler** - PDF to image conversion (used by `pdf2image`)

### Python setup

Python 3.10+ required. Use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate    # macOS / Linux
pip install -r requirements.txt
```

---

## Tool 1: TSCII PDF Converter (`tamil-converter.py`)

Converts old TSCII-encoded Tamil PDFs into Unicode Markdown. Best for government and university publications from the 1990s-2000s that used pre-Unicode Tamil encoding.

### TSCII Usage

```bash
python3 tamil-converter.py <input.pdf> <output.md>
```

**Default** (converts the bundled computing dictionary):

```bash
python3 tamil-converter.py
# Converts docs/TamilTechnicalDictionary.pdf -> docs/computing-glossary.md
```

### How to tell if your PDF is TSCII-encoded

Copy some text from the PDF and paste it into a text editor. If it looks like random ASCII characters or symbols instead of Tamil script, it is likely TSCII-encoded.

---

## Tool 2: PDF to Markdown (`pdf-2-markdown.py`)

Converts any Tamil PDF (scanned or text-based) into Markdown. Auto-detects whether the PDF has extractable text or needs OCR.

### PDF to Markdown Usage

```bash
python3 pdf-2-markdown.py <input.pdf> <output.md> [options]
```

### Options

| Flag           | Default                    | Description                                                      |
| -------------- | -------------------------- | ---------------------------------------------------------------- |
| `--language`   | `tam`                      | OCR language: `tam` (Tamil), `eng` (English), etc.               |
| `--dpi`        | `900`                      | DPI for OCR rendering. Higher = better quality but slower.       |
| `--images-dir` | None                       | Directory to save extracted images from image-only pages.        |
| `--fix`        | Off                        | Use LLM to fix OCR errors. Auto-detects Gemini or Claude.        |
| `--fix-model`  | Auto-detected              | LLM model: `gemini-2.5-flash`, `claude-sonnet-4-20250514`, etc. |

### Examples

```bash
# Basic conversion (scanned Tamil PDF at 900 DPI)
python3 pdf-2-markdown.py book.pdf book.md

# With image extraction
python3 pdf-2-markdown.py book.pdf book.md --images-dir book_images

# English PDF
python3 pdf-2-markdown.py book.pdf book.md --language eng

# With LLM-based OCR cleanup (auto-detects provider from .env)
python3 pdf-2-markdown.py book.pdf book.md --fix

# With a specific model
python3 pdf-2-markdown.py book.pdf book.md --fix --fix-model gemini-2.5-flash
```

### How it works

1. **Auto-detect**: Checks if the PDF has extractable text or is image-based
2. **Text-based PDFs**: Extracts text directly. For Tamil, detects TSCII encoding and converts to Unicode
3. **Scanned PDFs**: Converts pages to images, runs Tesseract OCR (`tam+eng`)
4. **Image-only pages** (portraits, illustrations): Detected automatically and saved as images or noted as placeholders
5. **Optional LLM fix**: Sends each page through Gemini or Claude API to correct OCR errors

### LLM Setup for `--fix`

Create a `.env` file in the project root with at least one API key:

```bash
GEMINI_API_KEY=your-gemini-key       # Free tier available
ANTHROPIC_API_KEY=your-claude-key    # Optional
```

If both keys are set, Gemini is used by default (free tier). Override with `--fix-model`.

### DPI Recommendations

| DPI   | Accuracy            | Speed     | Use case                                                       |
| ----- | ------------------- | --------- | -------------------------------------------------------------- |
| 300   | ~60-70%             | Fast      | Quick drafts                                                   |
| 600   | ~70-80%             | Moderate  | Good enough for most                                           |
| 900   | ~75-85%             | Slow      | Best quality (default)                                         |
| 1000+ | Diminishing returns | Very slow | Not recommended (see [OCR comparison](docs/ocr-comparison.md)) |

For detailed benchmarks across DPI levels and OCR engines, see [docs/ocr-comparison.md](docs/ocr-comparison.md).

---

## Project Structure

```text
tamil-converter/
  tamil-converter.py          # TSCII PDF to Unicode Markdown
  pdf-2-markdown.py           # Scanned/text PDF to Markdown (OCR)
  requirements.txt            # Python dependencies
  FAQ.md                      # FAQ in Tamil
  docs/
    ocr-comparison.md         # OCR engine benchmark results
    TamilTechnicalDictionary.pdf
    computing-glossary.md
    bharathithasan/           # Sample Tamil book PDFs and outputs
  tests/
    test_easyocr.py           # EasyOCR benchmark script
    test_paddleocr.py         # PaddleOCR benchmark script
    test_ocrtamil.py          # ocr-tamil benchmark script
```

---

## Libraries

- [pypdf](https://pypdf.readthedocs.io/) - PDF text extraction
- [open-tamil](https://github.com/Ezhil-Language-Foundation/open-tamil) - TSCII to Unicode conversion
- [pytesseract](https://github.com/madmaze/pytesseract) - Tesseract OCR Python wrapper
- [pdf2image](https://github.com/Belval/pdf2image) - PDF to image conversion
- [Pillow](https://pillow.readthedocs.io/) - Image processing
- [google-genai](https://github.com/googleapis/python-genai) - Gemini API (optional, for `--fix`)
- [anthropic](https://github.com/anthropics/anthropic-sdk-python) - Claude API (optional, for `--fix`)
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Load API keys from `.env` file

---

## License

See [LICENSE](LICENSE).
