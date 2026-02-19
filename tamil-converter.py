"""
Tamil PDF to Unicode Converter
Uses pypdf to extract TSCII-encoded text from old Tamil PDFs (pre-Unicode),
then uses open-tamil's tscii module to convert to Unicode (UTF-8).

Usage:
    python3 converter/tamil-converter.py <input.pdf> <output.md>

If no arguments given, defaults to the computing dictionary:
    docs/TamilTechnicalDictionary.pdf → docs/computing-glossary.md

Requirements:
    pip install pypdf
    pip install open-tamil
"""

import sys
import pypdf
from tamil import tscii


def pdf_to_unicode(pdf_path: str) -> str:
    """Extract all text from a TSCII-encoded PDF and convert to Unicode."""
    reader = pypdf.PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        raw = page.extract_text()
        if raw:
            unicode_text = tscii.convert_to_unicode(raw)
            pages.append(unicode_text)
    return "\n".join(pages)


def extract_glossary(text: str) -> list[tuple[str, str]]:
    """
    Parse lines of the form 'English term - Tamil term' from converted text.
    Returns a list of (english, tamil) pairs.
    Lines that don't match the pattern are skipped (headers, page numbers, etc.).
    """
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Dictionary lines contain ' - ' separating English from Tamil
        if " - " in line:
            parts = line.split(" - ", 1)
            english = parts[0].strip()
            tamil = parts[1].strip()
            # Skip header/footer lines: no lowercase Tamil vowels → likely a page header
            if english and tamil and not english.isdigit():
                entries.append((english, tamil))
    return entries


def write_markdown(entries: list[tuple[str, str]], output_path: str) -> None:
    """Write glossary entries as a two-column markdown table."""
    lines = [
        "# கணிப்பொறிக் கலைச்சொல் அகராதி",
        "",
        "> ஆதாரம்: வளர்தமிழ் மன்றம், அண்ணா பல்கலைக்கழகம், சென்னை-600 025 (1998)",
        "> இந்த அகராதி TamilTechnicalDictionary.pdf இலிருந்து தானாகவே பிரித்தெடுக்கப்பட்டது.",
        "",
        "| ஆங்கிலம் | தமிழ் |",
        "|----------|-------|",
    ]
    for english, tamil in entries:
        # Escape pipe characters in content
        english = english.replace("|", "\\|")
        tamil = tamil.replace("|", "\\|")
        lines.append(f"| {english} | {tamil} |")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(entries)} entries to {output_path}")


def convert_pdf_to_markdown(pdf_path: str, output_path: str) -> None:
    print(f"Reading {pdf_path} ...")
    text = pdf_to_unicode(pdf_path)

    print("Parsing glossary entries ...")
    entries = extract_glossary(text)
    print(f"Found {len(entries)} entries.")

    write_markdown(entries, output_path)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_pdf = sys.argv[1]
        output_md = sys.argv[2]
    else:
        input_pdf = "docs/TamilTechnicalDictionary.pdf"
        output_md = "docs/computing-glossary.md"

    convert_pdf_to_markdown(input_pdf, output_md)
