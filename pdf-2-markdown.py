"""
PDF to Markdown Converter
Extracts text from PDFs (text-based or scanned) and converts to markdown.

For text-based Tamil PDFs: extracts text and converts from TSCII to Unicode if needed.
For scanned/image PDFs: uses Tesseract OCR to extract text.
Optional --fix flag uses an LLM to clean up OCR errors.
Supports Gemini (GEMINI_API_KEY) and Claude (ANTHROPIC_API_KEY).
Auto-detects provider from .env or environment variables.

Usage:
    python3 pdf-2-markdown.py <input.pdf> <output.md> [--language tam] [--dpi 900] [--images-dir <dir>]
    python3 pdf-2-markdown.py <input.pdf> <output.md> --fix
    python3 pdf-2-markdown.py <input.pdf> <output.md> --fix --fix-model gemini-2.5-flash

Examples:
    python3 pdf-2-markdown.py book.pdf book.md
    python3 pdf-2-markdown.py book.pdf book.md --language eng
    python3 pdf-2-markdown.py book.pdf book.md --images-dir book_images
    python3 pdf-2-markdown.py book.pdf book.md --fix

Requirements:
    pip install pypdf pytesseract pdf2image pillow open-tamil python-dotenv
    pip install anthropic       (only needed with --fix and ANTHROPIC_API_KEY)
    pip install google-genai    (only needed with --fix and GEMINI_API_KEY)
    brew install tesseract tesseract-lang poppler
"""

import argparse
import os
import sys

import pypdf
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Allow high-DPI rendering (e.g. 1000 DPI) without triggering PIL's decompression bomb check.
# Bounded to 300M pixels (~1200 DPI on large pages) rather than None for safety.
Image.MAX_IMAGE_PIXELS = 300_000_000


def is_text_based_pdf(reader: pypdf.PdfReader, sample_pages: int = 5) -> bool:
    """Check if the PDF has extractable text by sampling the first few pages."""
    pages_to_check = min(sample_pages, len(reader.pages))
    for i in range(pages_to_check):
        text = reader.pages[i].extract_text()
        if text and text.strip():
            return True
    return False


def detect_tscii(text: str) -> bool:
    """
    Heuristic to detect if text is TSCII-encoded.
    TSCII uses specific byte patterns in the 0x80-0xFF range that appear
    as latin-extended or other characters when decoded as UTF-8.
    """
    if not text:
        return False
    # TSCII text typically has high concentration of characters in specific ranges
    # and very few standard Tamil Unicode characters (U+0B80-U+0BFF)
    tamil_unicode_count = sum(1 for c in text if "\u0B80" <= c <= "\u0BFF")
    # If we already have Tamil Unicode, it's not TSCII
    if tamil_unicode_count > len(text) * 0.1:
        return False
    # TSCII uses characters in ranges that look unusual for normal text
    high_byte_count = sum(1 for c in text if ord(c) > 127)
    if high_byte_count > len(text) * 0.3:
        return True
    return False


def extract_text_based(reader: pypdf.PdfReader, language: str) -> list[str]:
    """Extract text from a text-based PDF, with TSCII conversion for Tamil."""
    if language == "tam":
        from tamil import tscii

    pages = []
    for i, page in enumerate(reader.pages):
        raw = page.extract_text()
        if not raw or not raw.strip():
            pages.append("")
            continue

        if language == "tam":
            if detect_tscii(raw):
                try:
                    text = tscii.convert_to_unicode(raw)
                except Exception as e:
                    print(f"  Warning: TSCII conversion failed on page {i + 1}: {e}")
                    text = raw
            else:
                # Check if it's already Unicode Tamil
                tamil_chars = sum(1 for c in raw if "\u0B80" <= c <= "\u0BFF")
                if tamil_chars > 0:
                    text = raw
                else:
                    print(
                        f"  Warning: Page {i + 1} text is not TSCII or Unicode Tamil. "
                        f"Encoding unknown — including raw text."
                    )
                    text = raw
        else:
            text = raw

        pages.append(text)
    return pages


def is_image_only_page(page_image: Image.Image) -> tuple[bool, str]:
    """
    Determine if a page is primarily an image (illustration/portrait) vs text.
    Returns (is_image_only, description_hint).
    """
    # Run OCR and check how much text we get
    text = pytesseract.image_to_string(page_image, lang="tam+eng")
    stripped = text.strip()
    # If very little text, it's likely an image-only page
    if len(stripped) < 30:
        return True, stripped
    return False, stripped


def ocr_extract(
    pdf_path: str, language: str, dpi: int, images_dir: str | None
) -> list[str]:
    """Extract text from a scanned PDF using OCR."""
    tesseract_lang = language
    if language == "tam":
        tesseract_lang = "tam+eng"  # Tamil books often have some English

    total_pages = len(pypdf.PdfReader(pdf_path).pages)
    print(f"  OCR processing {total_pages} pages at {dpi} DPI...")

    pages = []
    # Process in batches to manage memory
    batch_size = 10
    for batch_start in range(1, total_pages + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, total_pages)
        print(f"  Processing pages {batch_start}-{batch_end}...")

        images = convert_from_path(
            pdf_path, first_page=batch_start, last_page=batch_end, dpi=dpi
        )

        for i, img in enumerate(images):
            page_num = batch_start + i
            is_img_page, hint_text = is_image_only_page(img)

            if is_img_page:
                # Save the image if images_dir is specified
                placeholder = f"[Image on page {page_num}]"
                if images_dir:
                    os.makedirs(images_dir, exist_ok=True)
                    img_filename = f"page_{page_num:03d}.png"
                    img_path = os.path.join(images_dir, img_filename)
                    img.save(img_path)
                    placeholder = f"![Page {page_num}]({img_filename})"
                if hint_text:
                    placeholder += f"\n\n{hint_text}"
                pages.append(placeholder)
            else:
                text = pytesseract.image_to_string(img, lang=tesseract_lang)
                pages.append(text.strip())

    return pages


FIX_SYSTEM_PROMPT = """\
You are an expert Tamil language editor specializing in correcting OCR errors \
in scanned Tamil texts. You will receive a page of text extracted via Tesseract OCR \
from a scanned Tamil book.

Your task:
1. Fix obvious OCR errors in Tamil text (wrong characters, broken words, missing vowel markers).
2. Remove garbage artifacts — random English words/letters (like "sass", "Popes", "RoBi", "v", "s") \
that are clearly OCR noise, not intentional English in the text.
3. Keep intentional English words (proper nouns, dates, book titles) intact.
4. Preserve the original line structure and paragraph breaks.
5. Do NOT add any commentary, notes, or explanations. Return ONLY the corrected text.
6. If a line is entirely garbage/unrecoverable, remove it.
7. Do NOT translate or paraphrase — only fix character-level OCR errors.
8. Preserve page numbers if present.
"""

LANG_PROMPTS = {
    "tam": "The text is in Tamil. Fix Tamil OCR errors. Tamil Unicode range: U+0B80–U+0BFF.",
    "eng": "The text is in English. Fix English OCR errors (wrong letters, broken words).",
}

# Default models per provider
DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "anthropic": "claude-sonnet-4-20250514",
}


def detect_llm_provider() -> tuple[str, str]:
    """
    Auto-detect which LLM provider to use based on available API keys.
    Returns (provider_name, api_key).
    Checks GEMINI_API_KEY and ANTHROPIC_API_KEY.
    """
    # Load .env file if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    gemini_key = os.environ.get("GEMINI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if gemini_key and anthropic_key:
        # Both available — prefer Gemini (free tier)
        return "gemini", gemini_key
    elif gemini_key:
        return "gemini", gemini_key
    elif anthropic_key:
        return "anthropic", anthropic_key
    else:
        return "", ""


def create_llm_client(provider: str, api_key: str):
    """Create an LLM client for the given provider."""
    if provider == "gemini":
        from google import genai
        return genai.Client(api_key=api_key)
    elif provider == "anthropic":
        import anthropic
        return anthropic.Anthropic(api_key=api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def fix_page_with_llm(
    client, provider: str, page_text: str, page_num: int, language: str, model: str
) -> str:
    """Send a page of OCR text to an LLM for cleanup."""
    # Skip image placeholders and empty pages
    if not page_text.strip() or page_text.startswith("![") or page_text.startswith("[Image"):
        return page_text

    lang_hint = LANG_PROMPTS.get(language, f"The text is in language: {language}.")
    user_message = (
        f"{lang_hint}\n\n"
        f"--- OCR text from page {page_num} ---\n\n"
        f"{page_text}"
    )

    if provider == "gemini":
        response = client.models.generate_content(
            model=model,
            contents=user_message,
            config={"system_instruction": FIX_SYSTEM_PROMPT, "max_output_tokens": 4096},
        )
        return response.text
    elif provider == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=FIX_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    else:
        raise ValueError(f"Unknown provider: {provider}")


RETRY_DELAYS = [1, 5, 15, 30]  # Progressive delays in seconds


def fix_page_with_retries(
    client, provider: str, page_text: str, page_num: int,
    language: str, model: str,
) -> str:
    """Fix a single page with progressive retry on transient errors (503, 429, etc.)."""
    import time

    for attempt, delay in enumerate(RETRY_DELAYS, 1):
        try:
            return fix_page_with_llm(client, provider, page_text, page_num, language, model)
        except Exception as e:
            error_msg = str(e).lower()
            is_retryable = any(
                keyword in error_msg
                for keyword in ["503", "429", "rate", "quota", "unavailable", "overloaded"]
            )
            if is_retryable and attempt < len(RETRY_DELAYS):
                print(f" retry in {delay}s...", end="", flush=True)
                time.sleep(delay)
            else:
                raise

    # Final attempt without catching
    return fix_page_with_llm(client, provider, page_text, page_num, language, model)


def fix_pages_with_llm(
    pages: list[str], language: str, model: str | None
) -> list[str]:
    """Fix all pages using an LLM, with progress tracking and retries."""
    provider, api_key = detect_llm_provider()
    if not provider:
        print("Error: No LLM API key found.")
        print("Set one of these in your .env file or environment:")
        print("  GEMINI_API_KEY=your-key       (free tier available)")
        print("  ANTHROPIC_API_KEY=your-key")
        sys.exit(1)

    # Use provided model or default for the detected provider
    if not model:
        model = DEFAULT_MODELS[provider]

    client = create_llm_client(provider, api_key)
    print(f"  LLM provider: {provider} (model: {model})")

    # Count pages that need fixing (non-empty, non-image)
    fixable = [
        i for i, p in enumerate(pages)
        if p.strip() and not p.startswith("![") and not p.startswith("[Image")
    ]
    print(f"  LLM fix: {len(fixable)} pages to process")

    fixed_pages = list(pages)
    fixed_count = 0

    for count, idx in enumerate(fixable, 1):
        page_num = idx + 1
        print(f"  Fixing page {page_num} ({count}/{len(fixable)})...", end="", flush=True)
        try:
            fixed_pages[idx] = fix_page_with_retries(
                client, provider, pages[idx], page_num, language, model
            )
            fixed_count += 1
            print(" done")
        except Exception as e:
            print(f" failed: {e} — keeping original")

    print(f"  LLM fix complete: {fixed_count}/{len(fixable)} pages fixed")
    return fixed_pages


def format_as_markdown(pages: list[str], pdf_name: str) -> str:
    """Format extracted pages into a markdown document."""
    lines = []
    lines.append(f"# {os.path.splitext(pdf_name)[0].replace('_', ' ')}")
    lines.append("")
    lines.append(f"> Extracted from: `{pdf_name}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, page_text in enumerate(pages, 1):
        if not page_text:
            continue

        # Add page separator
        if i > 1 and lines[-1] != "":
            lines.append("")

        # Add page marker as a comment
        lines.append(f"<!-- Page {i} -->")
        lines.append("")
        lines.append(page_text)
        lines.append("")

    return "\n".join(lines) + "\n"


def convert(
    input_pdf: str,
    output_md: str,
    language: str = "tam",
    dpi: int = 900,
    images_dir: str | None = None,
    fix: bool = False,
    fix_model: str | None = None,
) -> None:
    """Main conversion pipeline."""
    if not os.path.exists(input_pdf):
        print(f"Error: Input file not found: {input_pdf}")
        sys.exit(1)

    print(f"Reading: {input_pdf}")
    reader = pypdf.PdfReader(input_pdf)
    print(f"  Total pages: {len(reader.pages)}")

    # Auto-detect PDF type
    if is_text_based_pdf(reader):
        print("  Detected: text-based PDF")
        if language == "tam":
            # Sample text to check encoding
            sample = reader.pages[0].extract_text() or ""
            if detect_tscii(sample):
                print("  Encoding: TSCII (will convert to Unicode)")
            else:
                print("  Encoding: Unicode or unknown")
        pages = extract_text_based(reader, language)
    else:
        print("  Detected: scanned/image-based PDF (no extractable text)")
        print(f"  OCR language: {language}")

        # Verify tesseract language is available
        try:
            available_langs = pytesseract.get_languages()
            lang_parts = language.split("+")
            for lp in lang_parts:
                if lp not in available_langs:
                    print(
                        f"Error: Tesseract language '{lp}' not installed. "
                        f"Available: {', '.join(available_langs)}"
                    )
                    print(f"Install with: brew install tesseract-lang")
                    sys.exit(1)
        except Exception:
            pass

        if images_dir:
            os.makedirs(images_dir, exist_ok=True)
            print(f"  Images will be saved to: {images_dir}")

        pages = ocr_extract(input_pdf, language, dpi, images_dir)

    # LLM-based OCR cleanup (optional)
    if fix:
        print("  Starting LLM-based OCR cleanup...")
        pages = fix_pages_with_llm(pages, language, fix_model)

    # Format and write
    pdf_name = os.path.basename(input_pdf)
    markdown = format_as_markdown(pages, pdf_name)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_md)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_md, "w", encoding="utf-8") as f:
        f.write(markdown)

    non_empty = sum(1 for p in pages if p)
    print(f"\nDone! Wrote {non_empty} pages to: {output_md}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF and convert to Markdown."
    )
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("output_md", help="Path to output Markdown file")
    parser.add_argument(
        "--language",
        default="tam",
        help="OCR/text language: tam (Tamil, default), eng (English), etc.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=900,
        help="DPI for OCR rendering (default: 900). Higher = better quality but slower.",
    )
    parser.add_argument(
        "--images-dir",
        help="Directory to save extracted images. If not set, images are noted as placeholders only.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Use LLM to fix OCR errors. Auto-detects Gemini or Claude from .env/environment.",
    )
    parser.add_argument(
        "--fix-model",
        default=None,
        help="LLM model for --fix. Auto-detected if not set. "
        "Examples: gemini-2.5-flash, claude-sonnet-4-20250514.",
    )

    args = parser.parse_args()
    convert(
        args.input_pdf,
        args.output_md,
        args.language,
        args.dpi,
        args.images_dir,
        args.fix,
        args.fix_model,
    )


if __name__ == "__main__":
    main()
