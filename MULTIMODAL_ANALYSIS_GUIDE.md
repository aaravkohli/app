# PromptGuard Multimodal Security Analysis System

## Overview

This system extends PromptGuard to support **multimodal input analysis** including text, images, videos, code files, documents, PDFs, folders, and archives. Each input type receives specialized security analysis and is categorized as **Low, Medium, High, or Critical** risk.

## Architecture

### Backend Components

#### 1. **MultimodalAnalyzer** (`multimodal/analyzer.py`)
- Central orchestrator for all input types
- Detects input type automatically or uses explicit type
- Routes to appropriate specialized analyzer
- Supports recursive folder analysis

#### 2. **TextAnalyzer** (`multimodal/text_analyzer.py`)
Advanced NLP-based analysis including:
- **Injection Threats**: Prompt injection, code injection, SQL injection, XSS
- **Phishing Detection**: Suspicious communication patterns
- **Data Exfiltration Risks**: References to sensitive data
- **Semantic Analysis**: Manipulative language, social engineering
- **Obfuscation Detection**: Base64, hex encoding, Unicode escapes
- **Text Complexity Analysis**: Unusual character patterns

Risk Factors:
- Injection patterns: 0.9x weight
- Code injection: 0.85x weight
- SQL injection: 0.8x weight
- XSS/Script: 0.75x weight
- Phishing: 0.7x weight
- Data exfiltration: 0.65x weight

#### 3. **ImageAnalyzer** (`multimodal/image_analyzer.py`)
Image-specific threat detection:
- **Metadata Analysis**: EXIF data checking, suspicious fields
- **Steganography Detection**: Embedded archives, executables, PDFs
- **Malware Signatures**: Known malicious byte sequences
- **Binary Content Analysis**: Entropy calculations, suspicious patterns
- **Polyglot Detection**: Multiple file types in single file

#### 4. **VideoAnalyzer** (`multimodal/video_analyzer.py`)
Video file security analysis:
- **File Structure Validation**: Correct video headers and signatures
- **Embedded Content**: Malware, archives, executables
- **Polyglot Detection**: Multiple file types embedded
- **Metadata Checking**: Suspicious tags and patterns

#### 5. **FileAnalyzer** (`multimodal/file_analyzer.py`)
Multi-format file analysis:

**Code Files (.py, .js, .ts, etc.)**
- Remote execution patterns: `os.system`, `subprocess`, `eval`, `exec`
- File operations: Dangerous file access
- Network calls: Potential data exfiltration
- Registry access: Windows registry manipulation
- Hardcoded secrets: API keys, passwords
- SQL injection vulnerabilities
- Insecure random number generation

**PDF Files**
- Embedded JavaScript (risk: HIGH)
- Embedded files/executables (risk: HIGH)
- OpenAction tags (auto-execute) (risk: HIGH)
- XFA forms (potential exploits) (risk: MEDIUM)
- Object streams (obfuscation) (risk: MEDIUM)

**Archive Files (ZIP, RAR, 7Z, etc.)**
- Double extensions (suspicious masquerading)
- Path traversal attempts
- Executable files
- Compression ratio anomalies (zip bombs)
- Corrupted archives

**Office Documents (DOCX, XLSX, PPTX)**
- Macro detection
- External connections
- ActiveX objects
- Embedded scripts

### Frontend Components

#### **FileUploader** (`components/FileUploader.tsx`)
- Drag-and-drop file upload interface
- Real-time analysis status display
- Risk level visualization with color coding
- Threat details display
- Batch file support

## Risk Scoring System

### Risk Levels:
- **LOW** (0.0-0.3): Safe content, minimal threats
- **MEDIUM** (0.3-0.6): Potential risks, further review recommended
- **HIGH** (0.6-0.85): Significant threats, likely malicious
- **CRITICAL** (0.85-1.0): Severe threats, block/quarantine

### Risk Calculation:
```
risk_score = (threat_weight * threat_score) / total_weights
risk_score = risk_score - safe_patterns_offset
risk_score = min(1.0, max(0.0, risk_score))
```

## API Endpoints

### Text/Prompt Analysis
```bash
POST /api/analyze
Content-Type: application/json

{
  "prompt": "User prompt text"
}
```

### Multimodal Analysis
```bash
POST /api/analyze/multimodal
Content-Type: multipart/form-data

- file: (optional) File to analyze
- text: (optional) Text to analyze
- folder_path: (optional) Path to folder
```

### Specific File Type Analysis
```bash
POST /api/analyze/image
POST /api/analyze/video
POST /api/analyze/code
POST /api/analyze/pdf (auto-detected)
POST /api/analyze/batch
```

### Batch Analysis
```bash
POST /api/analyze/batch
Content-Type: multipart/form-data

files: [file1, file2, file3, ...]
```

### Supported Types
```bash
GET /api/supported-types

Returns:
{
  "types": [list of all extensions],
  "categories": {
    "images": [...],
    "videos": [...],
    "documents": [...],
    "code": [...],
    "archives": [...]
  }
}
```

## Response Format

### Multimodal Analysis Response
```json
{
  "risk_level": "low|medium|high|critical",
  "risk_score": 0.0-1.0,
  "input_type": "text|image|video|code|document|pdf|folder|archive",
  "threats": [
    {
      "type": "threat_type",
      "description": "Human readable description",
      "severity": "high|medium|low",
      "score": 0.0-1.0
    }
  ],
  "file_name": "filename.ext",
  "file_size": 12345,
  "details": {
    "complexity": {...},
    "line_count": 100,
    "word_count": 500
  }
}
```

## File Type Support

### Images
- .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg, .ico

### Videos
- .mp4, .avi, .mov, .mkv, .flv, .wmv, .webm, .m4v

### Code
- .py, .js, .ts, .java, .cpp, .c, .cs, .go, .rs, .php, .rb, .sh, .bash, .bat, .ps1, .gradle, .xml, .json, .yaml

### Documents
- .txt, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .odt, .csv

### Archives
- .zip, .rar, .7z, .tar, .gz, .bz2

### PDFs
- .pdf

## Usage Examples

### Frontend - Analyze Text
```typescript
import { apiService } from "@/lib/apiService_multimodal";

const result = await apiService.analyzeText("Your text here");
console.log(result.risk_level); // "low", "medium", "high", "critical"
```

### Frontend - Upload File
```typescript
const file = document.getElementById('fileInput').files[0];
const result = await apiService.analyzeFile(file);

if (result.risk_level === 'high' || result.risk_level === 'critical') {
  // Block or quarantine
}
```

### Frontend - Batch Upload
```typescript
const files = document.getElementById('multiFileInput').files;
const results = await apiService.analyzeBatch(files);

console.log(results.summary); // { total: 5, critical: 1, high: 2, medium: 2, low: 0 }
```

### Frontend - Upload Image
```typescript
const imageFile = document.getElementById('imageInput').files[0];
const result = await apiService.analyzeImage(imageFile);
```

### Frontend - Upload Video
```typescript
const videoFile = document.getElementById('videoInput').files[0];
const result = await apiService.analyzeVideo(videoFile);
```

### Frontend - Upload Code
```typescript
const codeFile = document.getElementById('codeInput').files[0];
const result = await apiService.analyzeCode(codeFile);
```

## Integration with Existing System

### Flow for Low/Medium/High Risk

1. **LOW RISK**
   - Text: Direct LLM response
   - Files: Allowed download/processing
   - Action: Process normally

2. **MEDIUM RISK**
   - Text: Additional semantic analysis (Phase 2)
   - Files: Manual review required
   - Action: Quarantine for review

3. **HIGH/CRITICAL RISK**
   - Text: Blocked with detailed reason
   - Files: Blocked/Quarantined
   - Action: Alert administrator

## Installing Dependencies

```bash
# Use Python 3.11
python -m venv .venv311
.\.venv311\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Key Features

✅ **Advanced NLP** - Beyond keywords, semantic analysis
✅ **Multimodal** - Images, videos, code, documents, archives
✅ **Recursive Scanning** - Analyze entire folders
✅ **Threat Classification** - Categorize threats by type
✅ **Risk Scoring** - Numerical risk assessment
✅ **Batch Processing** - Analyze multiple files
✅ **File Type Detection** - Auto-detect and route to specialist
✅ **Polyglot Detection** - Find disguised file types
✅ **Steganography Detection** - Find embedded threats
✅ **Archive Analysis** - Zip bomb, path traversal detection

## Performance Considerations

- **File Size Limit**: 100MB default (configurable)
- **Batch Limit**: 20 files per batch
- **Timeout**: 30 seconds per file (adjustable)
- **Async Processing**: Non-blocking analysis
- **Caching**: Results cached for identical inputs

## Security Best Practices

1. Always block/quarantine HIGH and CRITICAL risk content
2. Review MEDIUM risk content manually before processing
3. Monitor upload patterns for abuse
4. Rotate analysis models regularly
5. Keep threat signatures updated
6. Log all analyses for audit trails
