# Quick Setup Guide - Multimodal Analysis

## Step 1: Install Dependencies

```powershell
cd e:\app
.\.venv311\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Start the API Server

```powershell
python api_server.py
```

You should see:
```
📬 Received request with prompt: ...
🔍 Starting analysis...
✅ Analysis complete - Risk Level: low
```

## Step 3: Test the System

### Test Text Analysis (Command Line)
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing"}'
```

### Test File Upload (Command Line)
```bash
curl -X POST http://localhost:5000/api/analyze/multimodal \
  -F "file=@path/to/file.py"
```

## Step 4: Frontend Integration

The frontend now has:
- **FileUploader** component with drag-and-drop
- **apiService** with multimodal methods
- Real-time analysis display

## File Type Support

### Supported Formats:
- **Images**: jpg, jpeg, png, gif, bmp, webp, svg, ico
- **Videos**: mp4, avi, mov, mkv, flv, wmv, webm, m4v
- **Code**: py, js, ts, java, cpp, c, cs, go, rs, php, rb, sh, bash, bat, ps1
- **Documents**: txt, doc, docx, xls, xlsx, ppt, pptx, odt, csv, pdf
- **Archives**: zip, rar, 7z, tar, gz, bz2
- **Folders**: Recursive analysis of all files

## Risk Categories

### Low Risk (0.0-0.3)
✅ Safe content
✅ Educational queries
✅ General questions
✅ Creative requests

### Medium Risk (0.3-0.6)
⚠️ Potential concerns
⚠️ Requires review
⚠️ Suspicious patterns detected
⚠️ Multiple minor threats

### High Risk (0.6-0.85)
🚫 Significant threats
🚫 Likely malicious
🚫 Should be blocked
🚫 Clear attack indicators

### Critical Risk (0.85-1.0)
🛑 Severe threats
🛑 Definitely malicious
🛑 Must block/quarantine
🛑 Multiple high-severity threats

## What Gets Analyzed

### Text Analysis
- ✅ Injection attacks (prompt, SQL, code, XSS)
- ✅ Phishing indicators
- ✅ Data exfiltration attempts
- ✅ Social engineering tactics
- ✅ Obfuscation techniques
- ✅ Semantic threats

### Image Analysis
- ✅ Metadata threats
- ✅ Steganography (hidden data)
- ✅ Malware signatures
- ✅ Polyglot files
- ✅ Binary anomalies

### Video Analysis
- ✅ File structure validation
- ✅ Embedded threats
- ✅ Polyglot detection
- ✅ Suspicious metadata
- ✅ Corrupted files

### Code Analysis
- ✅ Dangerous function calls
- ✅ Command execution
- ✅ File operations
- ✅ Network access
- ✅ Hardcoded secrets
- ✅ SQL injection vulnerabilities
- ✅ Registry access

### Document Analysis
- ✅ Embedded scripts/macros
- ✅ External connections
- ✅ ActiveX objects
- ✅ Suspicious forms
- ✅ OLE objects

### Archive Analysis
- ✅ Double extensions
- ✅ Path traversal
- ✅ Executables
- ✅ Zip bombs
- ✅ Compression anomalies

### Folder Analysis
- ✅ Recursive scanning
- ✅ Aggregate risk scores
- ✅ Summary statistics
- ✅ Threat listing

## API Endpoints

### Text
```
POST /api/analyze
{"prompt": "text"}
```

### Multimodal
```
POST /api/analyze/multimodal
file: (upload file)
OR
text: (text content)
OR
folder_path: (path to folder)
```

### Specific Types
```
POST /api/analyze/image (images only)
POST /api/analyze/video (videos only)
POST /api/analyze/code (code only)
POST /api/analyze/batch (multiple files)
```

### Info
```
GET /api/supported-types (list all)
```

## Example Responses

### Low Risk
```json
{
  "risk_level": "low",
  "risk_score": 0.15,
  "input_type": "text",
  "threats": [],
  "complexity": {
    "has_special_chars": false,
    "has_urls": false,
    "has_code": false
  }
}
```

### High Risk
```json
{
  "risk_level": "high",
  "risk_score": 0.75,
  "input_type": "code",
  "threats": [
    {
      "type": "remote_execution",
      "description": "Found: os.system",
      "severity": "high"
    },
    {
      "type": "hardcoded_secrets",
      "description": "Potential hardcoded credentials",
      "severity": "high"
    }
  ],
  "file_name": "script.py",
  "line_count": 250
}
```

## Troubleshooting

### ImportError for PIL/opencv/etc
```bash
pip install Pillow opencv-python PyPDF2 python-magic-bin
```

### File too large
- Default max: 100MB
- Edit `MAX_FILE_SIZE` in `multimodal_routes.py`

### Slow analysis
- Large files take time
- Async processing prevents blocking
- Consider breaking into smaller files

### Port already in use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F
```

## Next Steps

1. ✅ Test with sample files
2. ✅ Integrate FileUploader into UI
3. ✅ Set up quarantine directory
4. ✅ Configure alert thresholds
5. ✅ Enable logging/monitoring
6. ✅ Deploy to production

## Support

For issues or questions, check:
- [MULTIMODAL_ANALYSIS_GUIDE.md](./MULTIMODAL_ANALYSIS_GUIDE.md) - Full documentation
- Console logs - Detailed analysis steps
- API responses - Specific threat details
