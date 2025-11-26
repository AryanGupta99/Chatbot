# OCR Setup Guide for Image-Heavy PDFs

Your SOPs contain mostly images with text. To extract this content, you need OCR (Optical Character Recognition) support.

## 🎯 Why OCR?

Without OCR:
- ❌ Image-based PDFs return minimal text
- ❌ Screenshots and diagrams are ignored
- ❌ Step-by-step visual guides are lost

With OCR:
- ✅ Extract text from images
- ✅ Read screenshots and diagrams
- ✅ Capture all visual content
- ✅ 10x more content extracted

## 📦 Installation

### Windows

#### Step 1: Install Tesseract OCR

**Option A: Using Installer (Recommended)**
1. Download Tesseract installer:
   https://github.com/UB-Mannheim/tesseract/wiki
   
2. Run installer (tesseract-ocr-w64-setup-v5.3.3.exe)

3. During installation:
   - Note the installation path (usually `C:\Program Files\Tesseract-OCR`)
   - Check "Add to PATH" option

4. Verify installation:
   ```cmd
   tesseract --version
   ```

**Option B: Using Chocolatey**
```cmd
choco install tesseract
```

#### Step 2: Install Python Packages
```bash
pip install pytesseract pdf2image Pillow
```

#### Step 3: Install Poppler (for pdf2image)

**Option A: Manual Installation**
1. Download Poppler for Windows:
   https://github.com/oschwartz10612/poppler-windows/releases/
   
2. Extract to `C:\Program Files\poppler`

3. Add to PATH:
   - Open System Properties → Environment Variables
   - Edit PATH
   - Add `C:\Program Files\poppler\Library\bin`

**Option B: Using Chocolatey**
```cmd
choco install poppler
```

#### Step 4: Configure Python
If Tesseract is not in PATH, add this to your code:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### macOS

```bash
# Install Tesseract
brew install tesseract

# Install Poppler
brew install poppler

# Install Python packages
pip install pytesseract pdf2image Pillow
```

### Linux (Ubuntu/Debian)

```bash
# Install Tesseract
sudo apt-get update
sudo apt-get install tesseract-ocr

# Install Poppler
sudo apt-get install poppler-utils

# Install Python packages
pip install pytesseract pdf2image Pillow
```

## ✅ Verify Installation

Run this test script:

```python
# test_ocr.py
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

print("Testing OCR setup...")

# Test 1: Tesseract
try:
    version = pytesseract.get_tesseract_version()
    print(f"✅ Tesseract version: {version}")
except Exception as e:
    print(f"❌ Tesseract error: {e}")

# Test 2: pdf2image
try:
    # This will fail if poppler is not installed
    from pdf2image.exceptions import PDFInfoNotInstalledError
    print("✅ pdf2image ready")
except Exception as e:
    print(f"❌ pdf2image error: {e}")

# Test 3: Simple OCR
try:
    # Create a test image with text
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (200, 50), color='white')
    d = ImageDraw.Draw(img)
    d.text((10,10), "Test OCR", fill='black')
    
    text = pytesseract.image_to_string(img)
    if "Test" in text or "OCR" in text:
        print("✅ OCR working correctly")
    else:
        print("⚠️  OCR may not be working properly")
except Exception as e:
    print(f"❌ OCR test failed: {e}")

print("\nIf all checks passed, you're ready to process image-heavy PDFs!")
```

Run it:
```bash
python test_ocr.py
```

## 🚀 Using OCR in Pipeline

Once installed, the pipeline will automatically use OCR:

```bash
# Run enhanced pipeline with OCR
python run_pipeline.py
```

You'll see:
```
✅ OCR enabled for image-heavy PDFs
📸 Low text content, trying OCR...
    OCR page 1/5... ✓
    OCR page 2/5... ✓
```

## 📊 Expected Results

### Without OCR
```
Processing 93 PDFs...
✅ Processed 45 documents (48 failed - insufficient text)
Total words: 15,000
```

### With OCR
```
Processing 93 PDFs...
✅ OCR enabled for image-heavy PDFs
✅ Processed 88 documents (5 failed)
Total words: 125,000
📸 Used OCR on 65 image-heavy PDFs
```

**10x more content extracted!**

## ⚙️ Configuration

### Adjust OCR Quality

In `src/image_pdf_processor.py`, modify:

```python
# Higher DPI = better quality, slower processing
images = convert_from_path(pdf_path, dpi=300)  # Default: 300

# OCR configuration
custom_config = r'--oem 3 --psm 6'  # Page segmentation mode
text = pytesseract.image_to_string(image, config=custom_config)
```

### OCR Language Support

For non-English content:
```bash
# Install language pack
tesseract --list-langs  # See available languages

# Download additional languages
# Windows: During Tesseract installation
# Linux: sudo apt-get install tesseract-ocr-spa  # Spanish example
# macOS: brew install tesseract-lang
```

Use in code:
```python
text = pytesseract.image_to_string(image, lang='eng+spa')  # English + Spanish
```

## 🐛 Troubleshooting

### Error: "tesseract is not installed"
```bash
# Windows: Add to PATH or set explicitly
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Verify installation
tesseract --version
```

### Error: "Unable to get page count"
```bash
# Poppler not installed or not in PATH
# Windows: Download and add to PATH
# macOS: brew install poppler
# Linux: sudo apt-get install poppler-utils
```

### Error: "PDF file is damaged"
```bash
# Some PDFs may be corrupted
# The pipeline will skip them and continue
```

### Slow Processing
```bash
# OCR is CPU-intensive
# Expected: 2-5 seconds per page
# For 93 PDFs with ~5 pages each: 15-40 minutes total

# Speed up:
# 1. Lower DPI (200 instead of 300)
# 2. Process in parallel (advanced)
# 3. Use GPU acceleration (requires additional setup)
```

## 📈 Performance Tips

### 1. Batch Processing
Process PDFs in batches during off-hours

### 2. Cache Results
Processed PDFs are saved - no need to re-process

### 3. Selective OCR
The system automatically detects which PDFs need OCR

### 4. Quality vs Speed
- **Fast**: DPI=200, good for most content
- **Balanced**: DPI=300 (default), recommended
- **High Quality**: DPI=400, for small text

## ✅ Verification Checklist

- [ ] Tesseract installed and in PATH
- [ ] Poppler installed and in PATH
- [ ] Python packages installed (pytesseract, pdf2image, Pillow)
- [ ] Test script runs successfully
- [ ] Pipeline shows "OCR enabled" message
- [ ] PDFs are being processed with OCR

## 🎯 Next Steps

Once OCR is set up:

1. **Run pipeline**:
   ```bash
   python run_pipeline.py
   ```

2. **Check results**:
   - Look for "📸 Used OCR" messages
   - Verify word count is significantly higher
   - Check `data/processed/processing_report.json`

3. **Test chatbot**:
   ```bash
   python test_chatbot.py
   ```
   - Ask questions about visual content
   - Verify responses include image-based information

## 💡 Pro Tips

1. **First Run**: Takes longer (15-40 min) but results are cached
2. **Subsequent Runs**: Much faster, only processes new/changed files
3. **Quality Check**: Review a few processed PDFs to ensure OCR accuracy
4. **Language**: If your PDFs have non-English content, install language packs

## 📞 Need Help?

If OCR setup fails:
1. Check error messages carefully
2. Verify PATH settings
3. Try manual installation paths
4. The system will still work without OCR (but with less content)

**Remember**: OCR is optional but highly recommended for image-heavy PDFs!
