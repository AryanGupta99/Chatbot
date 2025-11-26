import json
import re
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
import PyPDF2
from datetime import datetime

class DataProcessor:
    """Handles PDF extraction, text cleaning, and normalization"""
    
    def __init__(self, pdf_dir: str = "data/SOP and KB Docs"):
        self.pdf_dir = Path(pdf_dir)
        self.output_dir = Path("data/processed")
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using multiple methods for robustness"""
        text = ""
        
        try:
            # Method 1: pdfplumber (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed for {pdf_path.name}: {e}")
            
            # Fallback: PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"PyPDF2 also failed for {pdf_path.name}: {e2}")
        
        return text
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\[\]\"\'\/]', '', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')
        text = text.replace('0uickBooks', 'QuickBooks')
        text = text.replace('Qu1ckBooks', 'QuickBooks')
        
        # Normalize spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        
        # Remove URLs (optional - keep if needed)
        # text = re.sub(r'http[s]?://\S+', '', text)
        
        return text.strip()
    
    def extract_metadata(self, filename: str, text: str) -> Dict[str, Any]:
        """Extract metadata from filename and content"""
        metadata = {
            "filename": filename,
            "doc_id": filename.replace('.pdf', '').lower().replace(' ', '_'),
            "processed_at": datetime.now().isoformat(),
            "char_count": len(text),
            "word_count": len(text.split())
        }
        
        # Extract topic from filename
        if "quickbooks" in filename.lower():
            metadata["category"] = "QuickBooks"
        elif "rdp" in filename.lower() or "remote" in filename.lower():
            metadata["category"] = "Remote Desktop"
        elif "email" in filename.lower() or "outlook" in filename.lower():
            metadata["category"] = "Email"
        elif "server" in filename.lower():
            metadata["category"] = "Server"
        elif "user" in filename.lower():
            metadata["category"] = "User Management"
        else:
            metadata["category"] = "General"
        
        return metadata
    
    def process_all_pdfs(self) -> List[Dict[str, Any]]:
        """Process all PDFs in the directory"""
        documents = []
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        for idx, pdf_path in enumerate(pdf_files, 1):
            print(f"Processing {idx}/{len(pdf_files)}: {pdf_path.name}")
            
            try:
                # Extract text
                raw_text = self.extract_pdf_text(pdf_path)
                
                if not raw_text or len(raw_text.strip()) < 50:
                    print(f"  ⚠️  Skipping {pdf_path.name} - insufficient text")
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
                
                print(f"  ✓ Processed: {len(cleaned_text)} chars, {metadata['word_count']} words")
                
            except Exception as e:
                print(f"  ✗ Error processing {pdf_path.name}: {e}")
        
        return documents
    
    def save_processed_documents(self, documents: List[Dict[str, Any]]):
        """Save processed documents to JSON"""
        output_file = self.output_dir / "all_documents_cleaned.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(documents)} documents to {output_file}")
        
        # Generate summary report
        report = {
            "total_documents": len(documents),
            "total_chars": sum(len(doc["content"]) for doc in documents),
            "total_words": sum(doc["metadata"]["word_count"] for doc in documents),
            "categories": {}
        }
        
        for doc in documents:
            category = doc["metadata"]["category"]
            report["categories"][category] = report["categories"].get(category, 0) + 1
        
        report_file = self.output_dir / "processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Processing report saved to {report_file}")
        return report

if __name__ == "__main__":
    processor = DataProcessor()
    documents = processor.process_all_pdfs()
    report = processor.save_processed_documents(documents)
    
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Total Documents: {report['total_documents']}")
    print(f"Total Characters: {report['total_chars']:,}")
    print(f"Total Words: {report['total_words']:,}")
    print("\nCategories:")
    for category, count in report['categories'].items():
        print(f"  - {category}: {count}")
