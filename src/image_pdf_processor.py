"""
Enhanced PDF processor with OCR support for image-heavy documents
Extracts text from both text-based and image-based PDFs
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pdfplumber
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image
import io
from datetime import datetime

# OCR support (optional - requires tesseract installation)
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  OCR not available. Install: pip install pytesseract pdf2image")
    print("   Also install Tesseract: https://github.com/tesseract-ocr/tesseract")

class ImagePDFProcessor:
    """Enhanced PDF processor with OCR for image-heavy documents"""
    
    def __init__(self, pdf_dir: str = "data/SOP and KB Docs"):
        self.pdf_dir = Path(pdf_dir)
        self.output_dir = Path("data/processed")
        self.output_dir.mkdir(exist_ok=True)
        self.ocr_enabled = OCR_AVAILABLE
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text using multiple methods"""
        text = ""
        
        # Method 1: Try standard text extraction first
        text = self._extract_standard_text(pdf_path)
        
        # Method 2: If minimal text found, try OCR
        if len(text.strip()) < 100 and self.ocr_enabled:
            print(f"  📸 Low text content, trying OCR...")
            ocr_text = self._extract_with_ocr(pdf_path)
            if len(ocr_text) > len(text):
                text = ocr_text
        
        # Method 3: Extract images and their context
        images_context = self._extract_image_context(pdf_path)
        if images_context:
            text += "\n\n" + images_context
        
        return text
    
    def _extract_standard_text(self, pdf_path: Path) -> str:
        """Standard text extraction"""
        text = ""
        
        try:
            # Try pdfplumber first (best for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"  ⚠️  pdfplumber failed: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"  ⚠️  PyPDF2 also failed: {e2}")
        
        return text
    
    def _extract_with_ocr(self, pdf_path: Path) -> str:
        """Extract text using OCR (for image-based PDFs)"""
        if not self.ocr_enabled:
            return ""
        
        text = ""
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path, dpi=300)
            
            for i, image in enumerate(images):
                print(f"    OCR page {i+1}/{len(images)}...", end=" ")
                
                # Perform OCR
                page_text = pytesseract.image_to_string(image)
                text += f"\n--- Page {i+1} ---\n{page_text}\n"
                
                print("✓")
            
        except Exception as e:
            print(f"  ⚠️  OCR failed: {e}")
        
        return text
    
    def _extract_image_context(self, pdf_path: Path) -> str:
        """Extract context around images (captions, labels, etc.)"""
        context = ""
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                # Get images
                image_list = page.get_images()
                
                if image_list:
                    # Get text blocks near images
                    blocks = page.get_text("blocks")
                    
                    for img_index, img in enumerate(image_list):
                        # Try to find nearby text (captions, labels)
                        nearby_text = self._find_nearby_text(blocks, img_index)
                        if nearby_text:
                            context += f"\n[Image {page_num+1}-{img_index+1}]: {nearby_text}\n"
            
            doc.close()
        except Exception as e:
            print(f"  ⚠️  Image context extraction failed: {e}")
        
        return context
    
    def _find_nearby_text(self, blocks: List, img_index: int) -> str:
        """Find text blocks near an image"""
        # Simple heuristic: get text from nearby blocks
        nearby_text = []
        
        for block in blocks[:10]:  # Check first 10 blocks
            if len(block) >= 5:
                text = block[4].strip()
                if text and len(text) > 10:
                    nearby_text.append(text)
        
        return " ".join(nearby_text[:3])  # Return first 3 relevant blocks
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\[\]\"\'\/\n]', '', text)
        
        # Fix common OCR errors
        replacements = {
            '|': 'I',
            '0uick': 'Quick',
            'Qu1ck': 'Quick',
            'l3ook': 'Book',
            'W1ndows': 'Windows',
            'S3rver': 'Server',
            'Em@il': 'Email',
            'P@ssword': 'Password',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Normalize spacing
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\n\d+\n', '\n', text)
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_metadata(self, filename: str, text: str) -> Dict[str, Any]:
        """Extract metadata from filename and content"""
        metadata = {
            "filename": filename,
            "doc_id": filename.replace('.pdf', '').lower().replace(' ', '_'),
            "processed_at": datetime.now().isoformat(),
            "char_count": len(text),
            "word_count": len(text.split()),
            "has_images": "Image" in text or "Screenshot" in text
        }
        
        # Categorize by content and filename
        filename_lower = filename.lower()
        text_lower = text.lower()
        
        if any(word in filename_lower or word in text_lower for word in ['quickbooks', 'qb', 'accounting']):
            metadata["category"] = "QuickBooks"
        elif any(word in filename_lower or word in text_lower for word in ['rdp', 'remote', 'desktop', 'connection']):
            metadata["category"] = "Remote Desktop"
        elif any(word in filename_lower or word in text_lower for word in ['email', 'outlook', 'office', '365']):
            metadata["category"] = "Email"
        elif any(word in filename_lower or word in text_lower for word in ['server', 'performance', 'storage', 'disk']):
            metadata["category"] = "Server"
        elif any(word in filename_lower or word in text_lower for word in ['user', 'password', 'login', 'account']):
            metadata["category"] = "User Management"
        elif any(word in filename_lower or word in text_lower for word in ['printer', 'print']):
            metadata["category"] = "Printer"
        else:
            metadata["category"] = "General"
        
        # Extract error codes if present
        import re
        error_codes = re.findall(r'error[:\s]*[-]?\d+', text_lower)
        if error_codes:
            metadata["error_codes"] = list(set(error_codes))
        
        return metadata
    
    def process_all_pdfs(self) -> List[Dict[str, Any]]:
        """Process all PDFs with enhanced extraction"""
        documents = []
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        
        print(f"\n{'='*60}")
        print(f"PROCESSING {len(pdf_files)} PDFs WITH IMAGE SUPPORT")
        print(f"{'='*60}")
        if self.ocr_enabled:
            print("✅ OCR enabled for image-heavy PDFs")
        else:
            print("⚠️  OCR not available (install pytesseract for better results)")
        print()
        
        for idx, pdf_path in enumerate(pdf_files, 1):
            print(f"[{idx}/{len(pdf_files)}] {pdf_path.name}")
            
            try:
                # Extract text (with OCR if needed)
                raw_text = self.extract_text_from_pdf(pdf_path)
                
                if not raw_text or len(raw_text.strip()) < 50:
                    print(f"  ⚠️  Skipping - insufficient text ({len(raw_text)} chars)")
                    continue
                
                # Clean text
                cleaned_text = self.clean_text(raw_text)
                
                # Extract metadata
                metadata = self.extract_metadata(pdf_path.name, cleaned_text)
                
                documents.append({
                    "id": metadata["doc_id"],
                    "content": cleaned_text,
                    "metadata": metadata
                })
                
                print(f"  ✅ {len(cleaned_text)} chars, {metadata['word_count']} words")
                if metadata.get("error_codes"):
                    print(f"     Found error codes: {metadata['error_codes']}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return documents
    
    def save_processed_documents(self, documents: List[Dict[str, Any]]):
        """Save processed documents"""
        output_file = self.output_dir / "all_documents_cleaned.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(documents)} documents to {output_file}")
        
        # Generate report
        report = {
            "total_documents": len(documents),
            "total_chars": sum(len(doc["content"]) for doc in documents),
            "total_words": sum(doc["metadata"]["word_count"] for doc in documents),
            "categories": {},
            "documents_with_images": sum(1 for doc in documents if doc["metadata"].get("has_images")),
            "documents_with_errors": sum(1 for doc in documents if doc["metadata"].get("error_codes"))
        }
        
        for doc in documents:
            category = doc["metadata"]["category"]
            report["categories"][category] = report["categories"].get(category, 0) + 1
        
        report_file = self.output_dir / "processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Processing report saved to {report_file}")
        return report

if __name__ == "__main__":
    processor = ImagePDFProcessor()
    documents = processor.process_all_pdfs()
    report = processor.save_processed_documents(documents)
    
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Total Documents: {report['total_documents']}")
    print(f"Total Characters: {report['total_chars']:,}")
    print(f"Total Words: {report['total_words']:,}")
    print(f"Documents with Images: {report['documents_with_images']}")
    print(f"Documents with Error Codes: {report['documents_with_errors']}")
    print("\nCategories:")
    for category, count in report['categories'].items():
        print(f"  - {category}: {count}")
