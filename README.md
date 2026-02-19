# converter/

கருவிகள் — பழைய தமிழ் PDF கோப்புகளை Unicode Markdown-ஆக மாற்றுவதற்கு.

---

## tamil-converter.py

TSCII-குறியாக்கம் (pre-Unicode) கொண்ட Tamil PDF கோப்புகளை படிக்கக்கூடிய UTF-8 Markdown-ஆக மாற்றுகிறது.

**பயன்படுத்திய சூழல்:** 1998-ல் வெளியான அண்ணா பல்கலைக்கழக கணிப்பொறிக் கலைச்சொல் அகராதி — `docs/TamilTechnicalDictionary.pdf` — இதனை `docs/computing-glossary.md` ஆக மாற்ற இந்தக் கருவி பயன்படுகிறது.

### தேவையான நூலகங்கள்

```bash
pip install pypdf open-tamil
```

### பயன்பாடு

**இயல்புநிலை** (computing dictionary):

```bash
python3 converter/tamil-converter.py
```

`docs/TamilTechnicalDictionary.pdf` → `docs/computing-glossary.md`

**தனிப்பயன் கோப்புகளுக்கு:**

```bash
python3 converter/tamil-converter.py path/to/input.pdf path/to/output.md
```

### எப்போது பயன்படுத்தலாம்?

இந்த கருவி **TSCII-குறியாக்கம்** கொண்ட PDF கோப்புகளுக்கு மட்டுமே பொருந்தும் — பொதுவாக 1990கள் மற்றும் 2000களின் தொடக்கத்தில் வெளியான அரசு / பல்கலைக்கழக வெளியீடுகள்.

| PDF வகை | பொருந்துமா? |
|---------|-----------|
| TSCII-குறியாக்கம் (1990s–2000s) | ✅ |
| Unicode Tamil PDF (2010+) | ❌ — நேரடியாகப் படிக்கலாம் |
| ஸ்கேன் செய்யப்பட்ட படம் (image-based PDF) | ❌ — OCR தேவை |

### நூலகங்கள்

- [pypdf](https://pypdf.readthedocs.io/) — PDF உரை பிரித்தெடுத்தல்
- [open-tamil](https://github.com/Ezhil-Language-Foundation/open-tamil) — TSCII → Unicode மாற்றம்
