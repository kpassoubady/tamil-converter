# Tamil PDF to Unicode Converter

A tool for converting old Tamil PDF files (TSCII-encoded) into readable UTF-8 Markdown.

---

## Background

Tamil documents published before ~2010 — particularly government and university publications from the 1990s and early 2000s — were often encoded in **TSCII** (Tamil Script Code for Information Interchange), a pre-Unicode encoding. These PDFs cannot be read directly as text; the extracted characters appear as gibberish without conversion.

This tool extracts text from such PDFs and converts it to proper Unicode Tamil.

---

## Requirements

Python 3.10+ and two libraries:

```bash
pip install pypdf open-tamil
```

Or using the requirements file:

```bash
pip install -r requirements.txt
```

---

## Usage

**With your own files:**

```bash
python3 tamil-converter.py path/to/input.pdf path/to/output.md
```

**Default (converts the bundled computing dictionary):**

```bash
python3 tamil-converter.py
```

This converts `docs/TamilTechnicalDictionary.pdf` → `docs/computing-glossary.md`.

---

## When to Use This Tool

This tool works specifically for **TSCII-encoded PDFs** — it will not help with other PDF types:

| PDF Type | Supported? |
| -------- | --------- |
| TSCII-encoded (1990s–2000s government/university) | ✅ Yes |
| Unicode Tamil PDF (modern, ~2010+) | ❌ No — text is already readable |
| Scanned / image-based PDF | ❌ No — requires OCR instead |

### How to tell if your PDF is TSCII-encoded

Copy some text from the PDF and paste it into a text editor. If it looks like random ASCII characters or symbols instead of Tamil script, it is likely TSCII-encoded and this tool can help.

---

## Output Format

The converter parses lines in the format `English term - Tamil term` and writes them as a two-column Markdown table. This is well-suited for bilingual glossary-style documents. For other document formats, the raw Unicode text from `pdf_to_unicode()` can be used directly.

---

## Example

**Input PDF text (TSCII, garbled):**

```text
Abacus - v©uz
```

**Output Markdown:**

```markdown
| Abacus | கணக்குச்சட்டம் |
```

---

## Libraries

- [pypdf](https://pypdf.readthedocs.io/) — PDF text extraction
- [open-tamil](https://github.com/Ezhil-Language-Foundation/open-tamil) — TSCII → Unicode conversion

---

## License

See [LICENSE](LICENSE).
