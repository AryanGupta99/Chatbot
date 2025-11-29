"""
Build Expert-Level Knowledge Base from ALL Data Sources
- PDFs (SOPs and KB Docs)
- Manual KB articles
- Chat transcripts
- Ticket data
- Zobot extracted data
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from src.data_processor import DataProcessor
from src.chunker import SemanticChunker
from src.vector_store import VectorStore
import re

class ExpertKBBuilder:
    """Build comprehensive knowledge base from all available sources"""
    
    def __init__(self):
        self.output_dir = Path("data/expert_kb")
        self.output_dir.mkdir(exist_ok=True)
        self.all_chunks = []
    
    def load_pdf_data(self) -> List[Dict[str, Any]]:
        """Load and process PDF documents"""
        print("\n" + "="*70)
        print("LOADING PDF DOCUMENTS")
        print("="*70)
        
        processor = DataProcessor()
        documents = processor.process_all_pdfs()
        
        # Chunk the documents
        chunker = SemanticChunker(chunk_size=500, overlap=50)
        chunks = []
        
        for doc in documents:
            doc_chunks = chunker.create_chunks(
                doc['content'],
                doc['metadata']
            )
            chunks.extend(doc_chunks)
        
        # Add source type
        for chunk in chunks:
            chunk['metadata']['source_type'] = 'PDF_SOP'
            chunk['metadata']['priority'] = 'high'  # SOPs are authoritative
        
        print(f"✓ Loaded {len(chunks)} chunks from {len(documents)} PDF documents")
        return chunks
    
    def load_manual_kb(self) -> List[Dict[str, Any]]:
        """Load manual KB articles"""
        print("\n" + "="*70)
        print("LOADING MANUAL KB ARTICLES")
        print("="*70)
        
        kb_dir = Path("data/kb")
        chunks = []
        chunk_id = 0
        
        for kb_file in kb_dir.glob("*.md"):
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title from filename
                title = kb_file.stem.replace('_', ' ').title()
                
                # Determine category from filename
                category = "General"
                if "password" in kb_file.name.lower():
                    category = "Password Reset"
                elif "disk" in kb_file.name.lower() or "storage" in kb_file.name.lower():
                    category = "Disk Storage"
                elif "rdp" in kb_file.name.lower() or "connection" in kb_file.name.lower():
                    category = "RDP Connection"
                elif "quickbooks" in kb_file.name.lower():
                    category = "QuickBooks"
                elif "email" in kb_file.name.lower():
                    category = "Email"
                elif "user" in kb_file.name.lower():
                    category = "User Management"
                elif "printer" in kb_file.name.lower():
                    category = "Printer"
                elif "server" in kb_file.name.lower() or "performance" in kb_file.name.lower():
                    category = "Server Performance"
                
                # Split into sections if content is long
                if len(content) > 800:
                    # Split by headers or paragraphs
                    sections = re.split(r'\n#{1,3}\s+', content)
                    for section in sections:
                        if len(section.strip()) > 100:
                            chunks.append({
                                "id": f"manual_kb_{chunk_id}",
                                "content": section.strip(),
                                "metadata": {
                                    "source": kb_file.name,
                                    "title": title,
                                    "category": category,
                                    "source_type": "Manual_KB",
                                    "priority": "high"
                                }
                            })
                            chunk_id += 1
                else:
                    chunks.append({
                        "id": f"manual_kb_{chunk_id}",
                        "content": content.strip(),
                        "metadata": {
                            "source": kb_file.name,
                            "title": title,
                            "category": category,
                            "source_type": "Manual_KB",
                            "priority": "high"
                        }
                    })
                    chunk_id += 1
                
            except Exception as e:
                print(f"  ⚠️  Error loading {kb_file.name}: {e}")
        
        print(f"✓ Loaded {len(chunks)} chunks from manual KB articles")
        return chunks
    
    def load_chat_transcripts(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Load processed chat transcripts"""
        print("\n" + "="*70)
        print("LOADING CHAT TRANSCRIPTS")
        print("="*70)
        
        transcript_file = Path("data/processed/chat_transcripts.json")
        if not transcript_file.exists():
            print("  ⚠️  No chat transcripts found")
            return []
        
        try:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                transcripts = json.load(f)
            
            chunks = []
            chunk_id = 0
            
            # Process transcripts (limit to avoid too much data)
            for transcript in transcripts[:limit]:
                # Extract useful information
                issue = transcript.get('issue_summary', '')
                resolution = transcript.get('resolution', '')
                category = transcript.get('category', 'General')
                
                if issue and resolution:
                    content = f"Issue: {issue}\n\nResolution: {resolution}"
                    
                    chunks.append({
                        "id": f"chat_transcript_{chunk_id}",
                        "content": content,
                        "metadata": {
                            "source": "chat_transcript",
                            "category": category,
                            "source_type": "Chat_Transcript",
                            "priority": "medium"
                        }
                    })
                    chunk_id += 1
            
            print(f"✓ Loaded {len(chunks)} chunks from chat transcripts")
            return chunks
            
        except Exception as e:
            print(f"  ⚠️  Error loading chat transcripts: {e}")
            return []
    
    def load_zobot_data(self) -> List[Dict[str, Any]]:
        """Load Zobot extracted Q&A pairs"""
        print("\n" + "="*70)
        print("LOADING ZOBOT Q&A DATA")
        print("="*70)
        
        zobot_file = Path("data/zobot_extracted/zobot_qa_pairs.json")
        if not zobot_file.exists():
            print("  ⚠️  No Zobot data found")
            return []
        
        try:
            with open(zobot_file, 'r', encoding='utf-8') as f:
                qa_pairs = json.load(f)
            
            chunks = []
            
            for i, qa in enumerate(qa_pairs):
                question = qa.get('question', '')
                answer = qa.get('answer', '')
                category = qa.get('category', 'General')
                
                if question and answer:
                    content = f"Q: {question}\n\nA: {answer}"
                    
                    chunks.append({
                        "id": f"zobot_qa_{i}",
                        "content": content,
                        "metadata": {
                            "source": "zobot",
                            "category": category,
                            "source_type": "Zobot_QA",
                            "priority": "medium"
                        }
                    })
            
            print(f"✓ Loaded {len(chunks)} chunks from Zobot Q&A pairs")
            return chunks
            
        except Exception as e:
            print(f"  ⚠️  Error loading Zobot data: {e}")
            return []
    
    def load_existing_chunks(self) -> List[Dict[str, Any]]:
        """Load any existing processed chunks"""
        print("\n" + "="*70)
        print("LOADING EXISTING PROCESSED CHUNKS")
        print("="*70)
        
        chunk_files = [
            "data/processed/final_chunks.json",
            "data/processed/focused_chunks.json",
            "data/kb_article_chunks.json"
        ]
        
        all_chunks = []
        seen_ids = set()
        
        for chunk_file in chunk_files:
            path = Path(chunk_file)
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        chunks = json.load(f)
                    
                    # Deduplicate
                    for chunk in chunks:
                        chunk_id = chunk.get('id', '')
                        if chunk_id and chunk_id not in seen_ids:
                            seen_ids.add(chunk_id)
                            all_chunks.append(chunk)
                    
                    print(f"  ✓ Loaded {len(chunks)} chunks from {path.name}")
                except Exception as e:
                    print(f"  ⚠️  Error loading {path.name}: {e}")
        
        print(f"✓ Total: {len(all_chunks)} unique chunks from existing files")
        return all_chunks
    
    def deduplicate_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate chunks based on content similarity"""
        print("\n" + "="*70)
        print("DEDUPLICATING CHUNKS")
        print("="*70)
        
        unique_chunks = []
        seen_content = set()
        
        for chunk in chunks:
            # Use first 100 chars as fingerprint
            content = chunk.get('content', '')
            fingerprint = content[:100].lower().strip()
            
            if fingerprint and fingerprint not in seen_content:
                seen_content.add(fingerprint)
                unique_chunks.append(chunk)
        
        removed = len(chunks) - len(unique_chunks)
        print(f"✓ Removed {removed} duplicate chunks")
        print(f"✓ Kept {len(unique_chunks)} unique chunks")
        
        return unique_chunks
    
    def build_expert_kb(self):
        """Build complete expert knowledge base"""
        print("\n" + "="*70)
        print("BUILDING EXPERT KNOWLEDGE BASE")
        print("="*70)
        
        all_chunks = []
        
        # Load from all sources
        all_chunks.extend(self.load_pdf_data())
        all_chunks.extend(self.load_manual_kb())
        all_chunks.extend(self.load_chat_transcripts(limit=300))
        all_chunks.extend(self.load_zobot_data())
        all_chunks.extend(self.load_existing_chunks())
        
        # Deduplicate
        unique_chunks = self.deduplicate_chunks(all_chunks)
        
        # Save combined chunks
        output_file = self.output_dir / "expert_kb_chunks.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_chunks, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(unique_chunks)} chunks to {output_file}")
        
        # Generate statistics
        stats = self.generate_statistics(unique_chunks)
        stats_file = self.output_dir / "expert_kb_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✓ Saved statistics to {stats_file}")
        
        return unique_chunks, stats
    
    def generate_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about the knowledge base"""
        stats = {
            "total_chunks": len(chunks),
            "total_chars": sum(len(c.get('content', '')) for c in chunks),
            "total_words": sum(len(c.get('content', '').split()) for c in chunks),
            "by_source_type": {},
            "by_category": {},
            "by_priority": {}
        }
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            
            # Count by source type
            source_type = metadata.get('source_type', 'Unknown')
            stats['by_source_type'][source_type] = stats['by_source_type'].get(source_type, 0) + 1
            
            # Count by category
            category = metadata.get('category', 'Unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # Count by priority
            priority = metadata.get('priority', 'medium')
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        return stats
    
    def build_vector_store(self, chunks: List[Dict[str, Any]]):
        """Build vector store from chunks"""
        print("\n" + "="*70)
        print("BUILDING VECTOR STORE")
        print("="*70)
        
        vector_store = VectorStore()
        vector_store.create_collection()
        vector_store.add_documents(chunks)
        
        print("✓ Vector store built successfully")


if __name__ == "__main__":
    builder = ExpertKBBuilder()
    
    # Build knowledge base
    chunks, stats = builder.build_expert_kb()
    
    # Print summary
    print("\n" + "="*70)
    print("EXPERT KNOWLEDGE BASE SUMMARY")
    print("="*70)
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"Total Characters: {stats['total_chars']:,}")
    print(f"Total Words: {stats['total_words']:,}")
    
    print("\nBy Source Type:")
    for source_type, count in sorted(stats['by_source_type'].items()):
        print(f"  {source_type}: {count}")
    
    print("\nBy Category:")
    for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {category}: {count}")
    
    print("\nBy Priority:")
    for priority, count in sorted(stats['by_priority'].items()):
        print(f"  {priority}: {count}")
    
    # Ask if user wants to build vector store
    print("\n" + "="*70)
    response = input("Build vector store now? (y/n): ")
    if response.lower() == 'y':
        builder.build_vector_store(chunks)
        print("\n✓ COMPLETE! Expert knowledge base is ready.")
    else:
        print("\nTo build vector store later, run:")
        print("  python build_expert_kb.py")
