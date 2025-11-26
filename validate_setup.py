"""
Validation script to check if everything is set up correctly
Run this before starting the main pipeline
"""

import sys
from pathlib import Path
import json

def check_python_version():
    """Check Python version"""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (need 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required = [
        "fastapi",
        "uvicorn",
        "openai",
        "chromadb",
        "pdfplumber",
        "PyPDF2",
        "pandas"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\nChecking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("  ❌ .env file not found")
        print("  Run: copy .env.example .env")
        return False
    
    print("  ✅ .env file exists")
    
    # Check for API key
    with open(env_file, 'r') as f:
        content = f.read()
    
    if "OPENAI_API_KEY=sk-" in content or "OPENAI_API_KEY=your_" in content:
        if "your_openai_api_key" in content:
            print("  ⚠️  OPENAI_API_KEY not configured (using placeholder)")
            print("  Edit .env and add your actual OpenAI API key")
            return False
        else:
            print("  ✅ OPENAI_API_KEY configured")
            return True
    else:
        print("  ❌ OPENAI_API_KEY not found in .env")
        return False

def check_data_directories():
    """Check if data directories exist"""
    print("\nChecking data directories...")
    
    checks = []
    
    # Check PDF directory
    pdf_dir = Path("data/SOP and KB Docs")
    if pdf_dir.exists():
        pdf_count = len(list(pdf_dir.glob("*.pdf")))
        print(f"  ✅ PDF directory exists ({pdf_count} PDFs)")
        checks.append(pdf_count > 0)
    else:
        print("  ❌ PDF directory not found")
        checks.append(False)
    
    # Check KB directory
    kb_dir = Path("data/kb")
    if kb_dir.exists():
        kb_count = len(list(kb_dir.glob("*.md"))) + len(list(kb_dir.glob("*.txt")))
        print(f"  ✅ KB directory exists ({kb_count} articles)")
        checks.append(True)
    else:
        print("  ⚠️  KB directory not found (optional)")
        checks.append(True)
    
    # Create processed directory if needed
    processed_dir = Path("data/processed")
    if not processed_dir.exists():
        processed_dir.mkdir(parents=True, exist_ok=True)
        print("  ✅ Created processed directory")
    else:
        print("  ✅ Processed directory exists")
    
    return all(checks)

def check_existing_data():
    """Check if data has already been processed"""
    print("\nChecking for existing processed data...")
    
    files = {
        "Cleaned documents": Path("data/processed/all_documents_cleaned.json"),
        "Chunks": Path("data/processed/final_chunks.json"),
        "Vector DB": Path("data/chroma")
    }
    
    found = []
    for name, path in files.items():
        if path.exists():
            if path.is_file():
                size = path.stat().st_size / 1024  # KB
                print(f"  ✅ {name} found ({size:.1f} KB)")
            else:
                print(f"  ✅ {name} found")
            found.append(name)
        else:
            print(f"  ⚠️  {name} not found (will be created)")
    
    if found:
        print(f"\n  ℹ️  Found {len(found)} existing data files")
        print("  You can skip data processing or re-run to refresh")
    
    return True

def check_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI API connection...")
    
    try:
        from openai import OpenAI
        from config import settings
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Test with a simple embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="test"
        )
        
        print("  ✅ OpenAI API connection successful")
        return True
        
    except Exception as e:
        print(f"  ❌ OpenAI API connection failed: {e}")
        print("  Check your API key in .env file")
        return False

def main():
    """Run all validation checks"""
    print("="*60)
    print("ACEBUDDY RAG CHATBOT - SETUP VALIDATION")
    print("="*60)
    
    checks = {
        "Python version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Environment config": check_env_file(),
        "Data directories": check_data_directories(),
        "Existing data": check_existing_data(),
    }
    
    # Only test OpenAI if env is configured
    if checks["Environment config"]:
        checks["OpenAI connection"] = check_openai_connection()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Ready to run pipeline.")
        print("\nNext steps:")
        print("1. Run data pipeline: python run_pipeline.py")
        print("2. Test chatbot: python test_chatbot.py")
        print("3. Start API: python src/api.py")
        return True
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Configure .env: copy .env.example .env")
        print("- Add OpenAI API key to .env file")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
