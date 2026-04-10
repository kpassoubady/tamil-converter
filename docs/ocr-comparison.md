# Tamil OCR Engine Comparison

> Benchmark results from testing different OCR engines on a scanned Tamil book
> (Bharathidasan Kavithaigal Vol 2, published 1952).
>
> Test machine: Apple M4 Pro, 24 GB RAM, macOS, CPU-only (no GPU)
>
> Test date: April 2026

## Test Setup

- **Source PDF**: Scanned Tamil poetry book, 153 pages, image-based (no text layer)
- **Test pages**: Pages 10-11 of the book (poetry with mixed Tamil and some English)
- **PDF to image conversion**: `pdf2image` (poppler)
- **Python**: 3.12

## Summary

| Engine | Tamil Accuracy | Speed (per page) | Resource Usage | Verdict |
|--------|---------------|-------------------|----------------|---------|
| **Tesseract 5.5** (300 DPI) | ~60-70% | ~5s | Low | Usable baseline, many character errors |
| **Tesseract 5.5** (600 DPI) | ~70-80% | ~8s | Low | Noticeable improvement over 300 |
| **Tesseract 5.5** (900 DPI) | ~75-85% | ~12s | Moderate | Best Tesseract sweet spot |
| **Tesseract 5.5** (1000 DPI) | ~70-80% | ~15s | Moderate | Worse than 900 — overfitting on thick strokes |
| **Tesseract 5.5** (1200 DPI) | ~72-82% | ~18s | Moderate | Some wins, more garbage than 900 |
| **PaddleOCR 3.4** (600 DPI) | ~75-85% | ~976s (16 min!) | Very High (system slowdown) | Impractical on CPU |
| **EasyOCR 1.7.2** | N/A | N/A | N/A | Broken — Tamil model incompatible |
| **ocr-tamil 0.4.1** | ~5% | ~2s | Low | Unusable — detected almost no text |

## Detailed Comparison: Tesseract DPI Sweep

All results on the same poem (திராவிடநாட்டுப் பண்).

### 300 DPI

```
கீறராவிடநாட்டப்‌ பண்‌,
இசை--மோகனம்‌ : Stow b— gD
வாழ்க வாழ்கவே
வளமார்‌ எமதுதி ராவிடநாடு
வாழ்க வாழ்கவே /
கூழும்‌ தென்கடல்‌ ஆடும்‌ குமரி
தொடரும்‌ வடபால்‌ அடல்சேர்‌ வங்கம்‌
ஆமும்‌ கடல்கள்‌ கிழக்கு மேற்காம்‌
அறிவும்‌ திறலும்‌ செறிந்தநாடு (ar)
```

- Raga line is English garbage (`Stow b— gD`)
- Refrain `(வா)` reads as `(ar)`
- Multiple character errors: `கீறராவிடநாட்டப்` (wrong), `ஆமும்` (should be `ஆழும்`)

### 600 DPI

```
தீராவிடறநாட்டுப்‌ பண்‌,
இசை--மோகனம்‌ ' ST or b— 9 D
வாழ்க வாழ்கவே
வளமார்‌ எமதுதி ராவிடநாடு
வாழ்க வாழ்கவே /
குழும்‌ தென்கடல்‌ ஆடும்‌ குமரி
தொடரும்‌ வடபால்‌ அ௮டல்சேர்‌ வங்கம்‌
ஆழும்‌ கடல்கள்‌ கிழக்கு மேற்காம்‌
அறிவும்‌ திறலும்‌ செறிந்தநாடு (வா)
```

- Title slightly better but still wrong (`தீராவிடறநாட்டுப்`)
- Raga line still English garbage
- Refrains now correct `(வா)`
- `ஆழும்` now correct (was `ஆமும்` at 300)

### 900 DPI (Recommended)

```
கீராவிடநாட்டுப்‌ பண்‌,
இசை--மோகனம்‌ ' தாளம்‌--ஆஇ
வாழ்க வாழ்கவே
வளமார்‌ எமதுதி ராவிடநாடு
வாழ்க வாழ்கவே /
குழும்‌ தென்கடல்‌ ஆடும்‌ குமரி
தொடரும்‌ வடபால்‌ ௮டல்சேர்‌ வங்கம்‌
ஆழூம்‌ கடல்கள்‌ கிழக்கு மேற்காம்‌
அறிவும்‌ திறலும்‌ செறிந்தநாடு (aur)
பண்டைத்தமிழும்‌ தமிழில்‌ மலர்ந்த
```

- Raga line now reads as Tamil (`தாளம்‌--ஆஇ`) instead of English garbage
- `பண்டைத்தமிழும்` is correct (was wrong at all lower DPIs)
- Best overall consistency across the full page

### 1000 DPI

```
இறராவிடநாட்டுப்‌ பண்‌,
இசை--மோகனம்‌ தாளம்‌ அஆஇ
வாழ்க வாழ்கவே
வளமார்‌ எமதுதி ராவிடநாடு
வாழ்க வாழ்கவே /
குழும்‌ தென்கடல்‌ அடும்‌ குமரி
தொடரும்‌ வடபால்‌ அடல்சேர்‌ வங்கம்‌
BU) கடல்கள்‌ கிழக்கு மேற்காம்‌
```

- `ஆழும்` became `BU)` (garbage)
- `ஆடும்` lost the ஆ, became `அடும்`
- More English noise creeping in

### 1200 DPI

```
கீராவிடநாட்டூப்‌ பண்‌,
இசை--மோகனம்‌ : தாளம்‌--அஇ
ஆமூம்‌ கடல்கள்‌ கிழக்கு மேற்காம்‌
SLIPS கலைகள்‌ சிறந்தநாடு (our)
முகிலும்‌ செந்நெலும்‌ முழங்கு நன்செய்‌
```

- Some unique wins: `முகிலும்` correct (all others failed), `செந்நெலும்` correct
- But more garbage: `SLIPS`, `Aan`, `(our)`
- Inconsistent overall

## DPI Recommendation

```
Accuracy
  ^
  |         *  (900)
  |      *        *  (1200 — occasional wins)
  |   *               *  (1000 — regression)
  |*
  +--+--+--+--+--+--+--> DPI
   300 400 600 800 900 1000 1200

900 DPI is the sweet spot for Tesseract + scanned Tamil books.
```

**Why 900?** At lower DPIs, Tesseract lacks detail to distinguish similar Tamil characters.
Above 900, character strokes become too thick and Tesseract confuses them with
Latin characters, producing English garbage.

## PaddleOCR vs Tesseract: Line-by-Line

| Text (Correct) | Tesseract 900 DPI | PaddleOCR 600 DPI |
|----------------|-------------------|-------------------|
| திராவிடநாட்டுப் | `கீராவிடநாட்டுப்` | `திராவிடநாட்ுப்` (closer) |
| தாளம்--ஆதி | `தாளம்‌--ஆஇ` | `தாளம்-ஆD` |
| வாழ்கவே | `வாழ்கவே` | `வோழ்கவே` (wrong) |
| ஆடும் குமரி | `ஆடும்‌ குமரி` | `ஆடும் குடமரி` (wrong) |
| (வா) refrain | mixed `(aur)/(வா)` | all `(வா)` (correct) |
| ஆழும் | `ஆழூம்‌` | `ஆழும்` (correct) |
| ஆர்ந்திடு | `ஆர்ந்இடு` | `ஆர்ந்திடு` (correct) |
| தொடரும் | `தொடரும்` (correct) | `தாடரும்` (wrong) |
| கிழக்கு | `கிழக்கு` (correct) | `கழேக்கு` (wrong) |
| ஊழித்தீயும் | `ஊழித்தீயும்` (correct) | `ஊழித்கயும்` (wrong) |

**PaddleOCR accuracy is comparable to Tesseract, not dramatically better.**
Both get ~75-85% right on old Tamil print, just on *different* words.

## EasyOCR

**Status**: Broken as of April 2026.

EasyOCR 1.7.2 has a model incompatibility with Tamil:

```
RuntimeError: Error(s) in loading state_dict for Model:
  size mismatch for Prediction.weight: copying a param with shape
  torch.Size([143, 512]) from checkpoint, the shape in current model
  is torch.Size([127, 512]).
```

The Tamil recognition model expects 143 character classes but the code defines 127.
This affects both `["ta", "en"]` and `["ta"]` configurations.

## ocr-tamil

**Status**: Unusable for scanned books.

Despite claiming >95% accuracy, `ocr-tamil 0.4.1` detected almost no text from
the scanned pages. It appears to be designed for cleaner, modern Tamil text
(signboards, screenshots) rather than old printed books.

```
PAGE 1: "இரகல்லின்னே" (one garbled word for the entire page)
PAGE 2: "IIII" (complete failure)
```

## Practical Findings

1. **Tesseract at 900 DPI remains the best option** for scanned Tamil books on
   CPU-only machines. It's fast (~12s/page), lightweight, and produces the most
   consistent results.

2. **PaddleOCR is impractical on CPU** — 16 minutes per page and causes system
   slowdown on M4 Pro 24GB. May perform well with a GPU, but most Mac users
   won't have CUDA.

3. **The OCR accuracy ceiling for old Tamil print is ~80-85%** regardless of engine.
   The remaining errors are best addressed by LLM post-processing rather than
   switching engines.

4. **DPI matters more than engine choice** (up to a point). Going from 300 to 900 DPI
   with the same Tesseract engine improved accuracy more than switching from
   Tesseract to PaddleOCR at the same DPI.

## Recommended Pipeline

```
Scanned Tamil PDF
    |
    v
[pdf2image at 900 DPI]
    |
    v
[Tesseract OCR (tam+eng)]  -- free, fast, ~80% accuracy
    |
    v
[Markdown formatting]
    |
    v  (optional)
[Claude API --fix]  -- cleans up OCR errors, costs API tokens
    |
    v
Clean Tamil Markdown
```
