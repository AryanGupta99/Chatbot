"""Quick script to check pipeline progress"""
import json
from pathlib import Path

print("="*60)
print("PIPELINE PROGRESS CHECK")
print("="*60)

# Check Step 1: PDF Processing
pdf_report = Path("data/processed/processing_report.json")
if pdf_report.exists():
    with open(pdf_report) as f:
        data = json.load(f)
    print("\n✅ STEP 1: PDF Processing - COMPLETE")
    print(f"   Documents: {data['total_documents']}")
    print(f"   Words: {data['total_words']:,}")
    print(f"   Categories: {len(data['categories'])}")
else:
    print("\n⏳ STEP 1: PDF Processing - IN PROGRESS")

# Check Step 2: Chat Transcripts
chat_file = Path("data/processed/chat_transcripts.json")
if chat_file.exists():
    with open(chat_file) as f:
        data = json.load(f)
    print("\n✅ STEP 2: Chat Transcripts - COMPLETE")
    print(f"   Conversations: {len(data)}")
else:
    print("\n⏳ STEP 2: Chat Transcripts - IN PROGRESS")

# Check Step 2.5: Training Examples
training_file = Path("data/processed/training_examples.json")
if training_file.exists():
    with open(training_file) as f:
        data = json.load(f)
    print(f"   Training Examples: {len(data)}")

# Check Step 3: Chunks
chunks_file = Path("data/processed/final_chunks.json")
if chunks_file.exists():
    with open(chunks_file) as f:
        data = json.load(f)
    print("\n✅ STEP 3: Chunking - COMPLETE")
    print(f"   Total Chunks: {len(data)}")
else:
    print("\n⏳ STEP 3: Chunking - PENDING")

# Check Step 4: Vector DB
chroma_dir = Path("data/chroma")
if chroma_dir.exists() and any(chroma_dir.iterdir()):
    print("\n✅ STEP 4: Vector Database - COMPLETE")
else:
    print("\n⏳ STEP 4: Vector Database - PENDING")

print("\n" + "="*60)
