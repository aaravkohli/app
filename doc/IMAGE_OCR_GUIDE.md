# Image OCR Text Extraction Guide

## Overview

The system now supports automatic text extraction from images using **Optical Character Recognition (OCR)**. Images are processed identically to PDFs and text documents, with extracted text automatically routed through the same risk assessment pipeline.

## Supported Image Formats

- **PNG** (.png) - Lossless format with transparency support
- **JPEG/JPG** (.jpg, .jpeg) - Compressed format, widely compatible
- **BMP** (.bmp) - Uncompressed bitmap format
- **TIFF** (.tiff) - High-quality format for scanned documents
- **WebP** (.webp) - Modern compressed format
- **GIF** (.gif) - Animated format (processes first frame)

## How It Works

### 1. **Upload Process**
Users can upload images alongside PDFs, documents, and text, or submit images independently.

```
Image Upload → OCR Processing → Text Extraction → Text Cleaning → Risk Assessment
                                                                        ↓
                                                        Unified Analysis Pipeline
```

### 2. **Text Extraction (OCR)**
When an image is uploaded:
1. Image is loaded and format-normalized (RGBA → RGB if needed)
2. Pytesseract performs optical character recognition
3. Extracted text is cleaned and normalized
4. Results are logged with character count

### 3. **Text Cleaning**
Extracted image text goes through the same cleaning process as PDF text:
- Fix hyphenated line breaks (e.g., "con-\ntinue" → "continue")
- Normalize whitespace and line endings
- Collapse excessive blank lines while preserving paragraph structure
- Trim spaces from each line

### 4. **Risk Assessment**
Cleaned image text is processed identically to:
- PDF-extracted text
- Document text
- User-entered chat prompts

**Same Analysis Applied:**
- ML-based risk scoring
- Lexical risk detection
- Benign offset calculation
- Vigil-LLM scanning (if available)

## Backend Implementation

### Extract Function
```python
def extract_text_from_image_bytes(data: bytes) -> str:
    """
    Extract text from image using OCR.
    Supports: PNG, JPG, JPEG, BMP, TIFF, WebP, GIF
    
    Process:
    1. Load image from bytes
    2. Convert RGBA to RGB for compatibility
    3. Extract text using pytesseract
    4. Clean and normalize text
    5. Return extracted text
    """
```

### API Endpoint
**POST** `/api/analyze/file`

Accepts:
- Single or multiple image files
- Images + PDFs + documents combined
- Optional user text to append to extracted content

Response:
```json
{
  "status": "approved" | "blocked",
  "file_names": ["screenshot.png", "document.pdf"],
  "input_type": "image+pdf",
  "extracted_chars": 2456,
  "combined_text_chars": 3100,
  "risk_level": "low" | "medium" | "high" | "critical",
  "risk_score": 0.32,
  "analysis": {
    "risk": 0.32,
    "ml_score": 0.15,
    "lexical_risk": 0.28,
    "benign_offset": 0.08,
    "adaptive_phrases": 2
  },
  "analysisTime": 523,
  "vigil_analysis": { ... }
}
```

## Frontend Features

### File Type Detection
Images are automatically detected and routed to OCR processing:
```typescript
const getFileType = (file: File): FileType => {
  const ext = file.name.split(".").pop()?.toLowerCase() || "";
  if (["jpg", "jpeg", "png", "gif", "bmp", "webp"].includes(ext)) {
    return "image";
  }
  // ... other types
};
```

### Processing Pipeline
```typescript
// Images use the same analyze endpoint as PDFs
case "image":
  result = await apiService.analyzeFile(uploadedFile.file);
  break;
```

### Status Feedback
Users see processing status updates:
- 📤 **Uploading** - File being sent to server
- 🔄 **Analyzing** - OCR extraction and risk assessment in progress
- ✅ **Complete** - Results ready for review
- ❌ **Error** - Processing failed (see error message)

## Use Cases

### 1. **Scan Documents**
Users can scan physical documents and upload the images directly for analysis.

```
Physical Document → Scanner → Image → OCR → Risk Assessment
```

### 2. **Screenshots**
Analyze screenshots of web content, messages, or documents.

```
Screenshot → Upload → OCR → Risk Assessment
```

### 3. **Handwritten Notes**
Extract and analyze handwritten text captured in images.

```
Handwritten Note → Photo → OCR → Risk Assessment
```

### 4. **Mixed Content Analysis**
Combine multiple document types in a single analysis request.

```
┌─ document.pdf ─────────┐
├─ screenshot.png ───────┼─→ Combined Text → Risk Assessment
├─ report.docx ──────────┤
└─ handwritten_note.jpg ─┘
```

## Quality Considerations

### OCR Accuracy Factors

**Optimal for:**
- Clear, printed text
- High contrast (dark text on light background)
- Straight, horizontal text
- Standard fonts (Arial, Times New Roman, etc.)

**Challenges:**
- Handwriting (especially cursive)
- Rotated or skewed text
- Low contrast or faded text
- Decorative or stylized fonts
- Multiple languages mixed together

### Best Practices

1. **Image Quality**
   - Use high-resolution images (minimum 150 DPI)
   - Ensure good lighting conditions
   - Avoid shadows or glare

2. **Text Alignment**
   - Keep text straight and horizontal
   - Avoid tilted or rotated documents
   - Frame images to capture all text

3. **Contrast**
   - Use dark ink on light paper
   - Avoid blurred or faded text
   - Clean/dust scanner lens before scanning

4. **Format**
   - JPG for photographs and natural images
   - PNG for documents with transparency
   - TIFF for archival scanned documents

## Error Handling

### Common Issues and Solutions

**Issue:** "Could not extract text from image"
- **Cause:** Invalid image format or corrupted file
- **Solution:** Verify image file is valid, try converting format

**Issue:** "Empty text extracted"
- **Cause:** Image contains no readable text
- **Solution:** Check image quality, verify text is visible

**Issue:** "Garbled or incorrect text"
- **Cause:** Poor image quality or OCR limitations
- **Solution:** Improve image quality, use cleaner document

## System Requirements

### Backend Dependencies
```
Pillow==10.1.0        # Image processing
pytesseract==0.3.10   # OCR wrapper
```

### System Requirements
- **Tesseract-OCR** engine installed on server
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

## Configuration

### Environment Variables
```env
# Optional: Custom Tesseract path (if not in system PATH)
# TESSERACT_PATH=/usr/bin/tesseract

# File size limit (default 25MB)
MAX_UPLOAD_SIZE=26214400
```

### Pytesseract Configuration
If Tesseract is not in system PATH, set path in api_server.py:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"/custom/path/to/tesseract"
```

## Performance

### Processing Time
- **Typical Image:** 0.5-2 seconds
- **Complex/Large Images:** 2-5 seconds
- **Included in Response:** `analysisTime` (milliseconds)

### Text Extraction Quality
- **Confidence:** Usually 95%+ for clear printed text
- **Languages:** Supports 100+ languages (Tesseract default)
- **Mixed Language:** Works but may have lower accuracy

## Troubleshooting

### OCR Returns No Text
1. Check image quality and contrast
2. Verify Tesseract is installed: `tesseract --version`
3. Check system logs for OCR errors

### Deployment Issues (Render/Vercel)

**Render (Backend):**
- Ensure Tesseract is included in build:
  ```yaml
  # render.yaml
  buildCommand: apt-get update && apt-get install -y tesseract-ocr && pip install -r requirements.txt
  ```

**Vercel (Frontend):**
- Image processing happens on backend only
- Frontend just uploads the file

## Future Enhancements

- [ ] Language selection for OCR
- [ ] Preprocessing filters (deskew, denoise)
- [ ] Table structure detection
- [ ] Layout analysis for multi-column documents
- [ ] Batch processing optimization
- [ ] Confidence scoring per extracted text block
- [ ] Handwriting specialization mode

## API Examples

### Upload Single Image
```bash
curl -X POST http://localhost:5000/api/analyze/file \
  -F "file=@screenshot.png"
```

### Upload Multiple Files (Mixed Types)
```bash
curl -X POST http://localhost:5000/api/analyze/file \
  -F "file=@document.pdf" \
  -F "file=@screenshot.png" \
  -F "file=@notes.docx" \
  -F "text=Additional context text"
```

### Response Example
```json
{
  "status": "approved",
  "file_names": ["screenshot.png"],
  "input_type": "image",
  "extracted_chars": 456,
  "combined_text_chars": 456,
  "risk_level": "low",
  "risk_score": 0.18,
  "analysis": {
    "risk": 0.18,
    "ml_score": 0.08,
    "lexical_risk": 0.22,
    "benign_offset": 0.12,
    "adaptive_phrases": 0
  },
  "analysisTime": 1023
}
```

## Testing

### Local Testing
```python
from PIL import Image
import pytesseract

# Test OCR locally
image = Image.open("test_image.png")
text = pytesseract.image_to_string(image)
print(f"Extracted: {text}")
```

### Upload Test
```bash
# Test with real image
curl -X POST http://localhost:5000/api/analyze/file \
  -F "file=@/path/to/test/image.png" \
  | jq '.analysis'
```

## Related Features

- [PDF Text Extraction](./DEPLOYMENT.md#pdf-text-extraction)
- [File Upload Guide](../frontend/doc/ARCHITECTURE.md#file-upload)
- [Risk Assessment Pipeline](../doc/VIGIL_INTEGRATION.md)

---

**Last Updated:** February 2026
**Status:** Production Ready ✅
