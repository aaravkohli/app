# Image Upload Feature - User Guide

## 🖼️ What's New

You can now upload **images directly** to PromptGuard and they will be automatically processed using OCR (Optical Character Recognition) to extract text. The extracted text is then analyzed for security risks just like any PDF or document.

## 📸 Supported Image Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| PNG | `.png` | Screenshots, graphics with text |
| JPEG | `.jpg`, `.jpeg` | Photos of documents |
| BMP | `.bmp` | Scanned images |
| TIFF | `.tiff` | High-quality scanned documents |
| WebP | `.webp` | Modern web images |
| GIF | `.gif` | Animations (processes first frame) |

## 🚀 How to Use

### Option 1: Click and Select
1. Click the **"Select Files"** button
2. Choose one or more image files
3. Images start uploading automatically
4. Watch the status update in real-time

### Option 2: Drag and Drop
1. Click on the upload area or drag files directly
2. Drop one or multiple images
3. Processing starts automatically

### Option 3: Mix File Types
You can upload **images + PDFs + documents together**:
```
Upload together:
  • screenshot.png
  • document.pdf
  • notes.docx
```
All content will be combined and analyzed together!

## 📊 What Happens After Upload

```
1️⃣ Upload Image
   ↓
2️⃣ Extract Text (OCR)
   Status: "Analyzing"
   ↓
3️⃣ Clean & Normalize Text
   ↓
4️⃣ Analyze for Risk
   Status: "Complete"
   ↓
5️⃣ See Results
   Risk Level: Low/Medium/High/Critical
   Risk Score: 0.0 - 1.0
   Vigil Analysis: Available
```

## 📈 Understanding Results

When you upload an image, you'll see:

```json
{
  "status": "approved",           // Approved or blocked
  "file_names": ["screenshot.png"], // Your uploaded file
  "input_type": "image",           // Detected as image
  "extracted_chars": 245,          // Characters extracted from image
  "risk_level": "low",             // Overall risk assessment
  "risk_score": 0.18               // Detailed risk score (0.0-1.0)
}
```

### Risk Levels Explained

| Level | Score | Meaning |
|-------|-------|---------|
| 🟢 Low | 0.0-0.4 | Safe to use |
| 🟡 Medium | 0.4-0.7 | Review recommended |
| 🔴 High | 0.7-0.85 | Likely harmful |
| 🔴🔴 Critical | 0.85-1.0 | Blocked - unsafe |

## ✨ Key Features

### 🎯 Unified Processing
- Images processed **exactly like PDFs and documents**
- Same risk assessment applied to all file types
- Consistent results across different input methods

### 🔄 Status Tracking
See real-time updates:
- ✋ **Pending** - Waiting to upload
- 📤 **Uploading** - Sending to server
- 🔄 **Analyzing** - OCR extracting text and analyzing
- ✅ **Complete** - Results ready
- ❌ **Error** - Issue during processing

### 📝 Extracted Text
See how many characters were extracted:
```
Extracted: 2,456 characters
Analyzed: Full risk assessment on extracted text
```

### 🔗 Multi-File Support
```
Upload multiple files at once:
  ✅ screenshot.png (235 chars extracted)
  ✅ document.pdf (1,820 chars extracted)
  ✅ notes.docx (891 chars extracted)
  
Combined: 2,946 characters analyzed together
```

## 🎓 Best Practices

### For Best OCR Results

1. **Image Quality**
   - Use high-resolution images
   - Ensure good lighting in photos
   - Avoid blurry or faded text

2. **Text Clarity**
   - Black text on white background works best
   - Avoid rotated or tilted documents
   - Keep text straight and horizontal

3. **Format**
   - Use PNG for clear screenshots
   - Use JPEG for camera photos
   - Use TIFF for scanned documents

### Examples of Good Images

✅ **Screenshot of web page** - Clear, sharp text
✅ **Scanned document** - High contrast, straight
✅ **Printed document photo** - Good lighting, no shadows
✅ **Receipt photo** - Readable text, taken straight-on

### Examples to Avoid

❌ **Handwritten notes** - Lower accuracy
❌ **Rotated text** - Extraction quality suffers
❌ **Low contrast** - Text too faint to read
❌ **Blurry photos** - OCR struggles
❌ **Decorative fonts** - May not extract correctly

## ⚙️ Technical Details

### What Gets Extracted
- **Text from images** - Visible text extracted via OCR
- **Languages** - Supports 100+ languages
- **Accuracy** - Typically 95%+ for clear text

### Processing Time
- Small image (< 1 MB): ~0.5-1 second
- Medium image (1-5 MB): ~1-2 seconds  
- Large/complex image: ~2-5 seconds

### File Size Limits
- Maximum: **25 MB per file**
- Total upload: Multiple files supported
- Larger files may take longer to process

## 🐛 Troubleshooting

### "Could not extract text from image"
**Cause:** Image quality or format issue  
**Solution:** 
- Check image is valid/not corrupted
- Try converting format (PNG → JPG)
- Improve image quality

### "No readable text found"
**Cause:** Image has no text or text is too small/faint  
**Solution:**
- Verify image contains readable text
- Use higher quality image
- Ensure good contrast

### "Empty result"
**Cause:** OCR couldn't read the text  
**Solution:**
- Check for OCR-unfriendly fonts
- Improve image contrast
- Try different image format

### Image takes very long to process
**Cause:** Large or complex image  
**Solution:**
- Reduce image size/resolution
- Break large documents into pages
- Use higher contrast for clarity

## 🎯 Use Cases

### 1. Analyze Screenshots
```
Screenshot of message → Upload → Extract text → Risk analysis
```

### 2. Scan Documents
```
Physical document → Scan/Photo → Upload → Extract → Analyze
```

### 3. Review Social Media
```
Screenshot of post → Upload → Extract text → Check safety
```

### 4. Verify Contracts
```
Contract photo → Upload → Extract → Analyze terms
```

### 5. Check Email Images
```
Email screenshot → Upload → Extract text → Verify safety
```

## 🔐 Privacy & Security

- ✅ Images processed on secure server
- ✅ Extracted text encrypted in transit
- ✅ No image data stored (processed then deleted)
- ✅ Same security as PDF/document uploads
- ✅ Protected by HTTPS/SSL

## 🔗 Related Features

- **PDF Upload** - Same workflow as images
- **Document Upload** - DOCX, TXT, CSV support
- **Text Pasting** - Direct text input also supported
- **Risk Assessment** - Unified analysis across all types

## 📞 Support

If you encounter issues:

1. **Check image quality** - Verify text is clearly visible
2. **Try different format** - PNG instead of JPG
3. **Check file size** - Under 25 MB limit?
4. **Review logs** - Error message in results
5. **Report issue** - Contact support with image details

## ✅ Checklist Before Uploading

- [ ] Image contains readable text
- [ ] File size under 25 MB
- [ ] Image quality is good (high resolution)
- [ ] Text is clearly visible
- [ ] Format is supported (PNG, JPG, etc.)

---

**Ready to upload?** Click "Select Files" or drag an image to get started! 🚀
