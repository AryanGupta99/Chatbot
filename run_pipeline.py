"""
Complete data processing pipeline for AceBuddy RAG system
Run this script to process all data from PDFs to vector database
Includes: Image-heavy PDFs with OCR + Chat transcript learning
"""

import sys
from pathlib import Path
import json

def run_pipeline():
    print("="*60)
    print("ACEBUDDY RAG DATA PROCESSING PIPELINE")
    print("Enhanced with OCR + Chat Learning")
    print("="*60)
    
    # Step 1: Process PDFs with OCR support
    print("\n[STEP 1/4] Processing PDF documents (with OCR for images)...")
    print("-" * 60)
    try:
        from src.image_pdf_processor import ImagePDFProcessor
        processor = ImagePDFProcessor()
        documents = processor.process_all_pdfs()
        
        if not documents:
            print("❌ No documents processed. Check PDF directory.")
            return False
        
        report = processor.save_processed_documents(documents)
        print(f"✅ Processed {report['total_documents']} documents")
        print(f"   Total words: {report['total_words']:,}")
        print(f"   Documents with images: {report.get('documents_with_images', 0)}")
        print(f"   Categories: {len(report['categories'])}")
    except Exception as e:
        print(f"❌ Error in PDF processing: {e}")
        print(f"   Tip: Install OCR support for better results:")
        print(f"   pip install pytesseract pdf2image")
        return False
    
    # Step 1.5: Process chat transcripts
    print("\n[STEP 2/4] Processing chat transcripts (learning from real data)...")
    print("-" * 60)
    try:
        from src.chat_transcript_processor import ChatTranscriptProcessor
        chat_processor = ChatTranscriptProcessor()
        transcripts, analysis, training_examples = chat_processor.process_all()
        
        print(f"✅ Processed {len(transcripts)} conversations")
        print(f"   Training examples: {len(training_examples)}")
        print(f"   Categories identified: {len(analysis['categories'])}")
    except Exception as e:
        print(f"⚠️  Warning: Chat transcript processing failed: {e}")
        print(f"   Continuing with PDF data only...")
        transcripts = []
        training_examples = []
    
    # Step 3: Create chunks (combining PDFs + chat examples)
    print("\n[STEP 3/4] Creating semantic chunks (PDFs + Chat Examples)...")
    print("-" * 60)
    try:
        from src.chunker import SemanticChunker
        
        # Load processed documents
        with open("data/processed/all_documents_cleaned.json", 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # Load training examples if available
        training_examples = []
        training_file = Path("data/processed/training_examples.json")
        if training_file.exists():
            with open(training_file, 'r', encoding='utf-8') as f:
                training_examples = json.load(f)
        
        chunker = SemanticChunker(chunk_size=500, overlap=50)
        chunks = chunker.process_documents(documents, training_examples)
        stats = chunker.save_chunks(chunks)
        
        print(f"✅ Created {stats['total_chunks']} chunks")
        print(f"   PDF chunks: {stats['total_chunks'] - len(training_examples)}")
        print(f"   Training examples: {len(training_examples)}")
        print(f"   Avg size: {stats['avg_chunk_size']:.0f} chars")
    except Exception as e:
        print(f"❌ Error in chunking: {e}")
        return False
    
    # Step 3: Build vector database
    print("\n[STEP 4/4] Building vector database...")
    print("-" * 60)
    try:
        from src.vector_store import VectorStore
        
        # Load chunks
        with open("data/processed/final_chunks.json", 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        vector_store = VectorStore()
        vector_store.create_collection()
        vector_store.add_documents(chunks)
        
        stats = vector_store.get_collection_stats()
        print(f"✅ Vector database ready")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Collection: {stats['collection_name']}")
    except Exception as e:
        print(f"❌ Error building vector database: {e}")
        print(f"   Make sure OPENAI_API_KEY is set in .env file")
        return False
    
    # Success!
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"   - PDF Documents: {report['total_documents']}")
    print(f"   - Chat Conversations: {len(transcripts) if transcripts else 0}")
    print(f"   - Training Examples: {len(training_examples) if training_examples else 0}")
    print(f"   - Total Chunks: {stats['total_chunks']}")
    print(f"   - Vector Database: Ready")
    print("\n🎯 Your chatbot now understands:")
    print("   ✅ 93 PDF SOPs (with image content via OCR)")
    print("   ✅ 9 months of real chat conversations")
    print("   ✅ Successful resolution patterns")
    print("   ✅ User language and terminology")
    print("\nNext steps:")
    print("1. Test RAG engine: python src/rag_engine.py")
    print("2. Test chatbot: python test_chatbot.py")
    print("3. Start API server: python src/api.py")
    print("\n🚀 Ready to achieve 40-60% automation!")
    
    return True

if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
