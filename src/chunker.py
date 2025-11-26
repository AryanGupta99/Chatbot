import json
from pathlib import Path
from typing import List, Dict, Any
import re

class SemanticChunker:
    """Creates semantic chunks optimized for RAG retrieval"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split_by_sections(self, text: str) -> List[str]:
        """Split text by logical sections (headers, steps, etc.)"""
        # Split by common section markers
        patterns = [
            r'\n#{1,3}\s+',  # Markdown headers
            r'\n\d+\.\s+',   # Numbered lists
            r'\n[A-Z][^.!?]*:',  # Section titles ending with colon
            r'\n\n+'  # Double line breaks
        ]
        
        sections = [text]
        for pattern in patterns:
            new_sections = []
            for section in sections:
                parts = re.split(pattern, section)
                new_sections.extend([p.strip() for p in parts if p.strip()])
            sections = new_sections
        
        return sections
    
    def create_chunks(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create overlapping chunks with metadata"""
        chunks = []
        
        # First try semantic splitting
        sections = self.split_by_sections(text)
        
        current_chunk = ""
        chunk_num = 0
        
        for section in sections:
            # If section fits in current chunk
            if len(current_chunk) + len(section) <= self.chunk_size:
                current_chunk += " " + section if current_chunk else section
            else:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(self._create_chunk_dict(
                        current_chunk, metadata, chunk_num
                    ))
                    chunk_num += 1
                
                # If section is too large, split it
                if len(section) > self.chunk_size:
                    sub_chunks = self._split_large_section(section)
                    for sub_chunk in sub_chunks:
                        chunks.append(self._create_chunk_dict(
                            sub_chunk, metadata, chunk_num
                        ))
                        chunk_num += 1
                    current_chunk = ""
                else:
                    current_chunk = section
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk_dict(
                current_chunk, metadata, chunk_num
            ))
        
        return chunks
    
    def _split_large_section(self, text: str) -> List[str]:
        """Split large sections with overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size * 0.5:  # At least 50% of chunk size
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - self.overlap
        
        return chunks
    
    def _create_chunk_dict(self, content: str, metadata: Dict[str, Any], chunk_num: int) -> Dict[str, Any]:
        """Create chunk dictionary with metadata"""
        return {
            "id": f"{metadata['doc_id']}_chunk_{chunk_num}",
            "content": content.strip(),
            "metadata": {
                **metadata,
                "chunk_number": chunk_num,
                "chunk_char_count": len(content)
            }
        }
    
    def process_documents(self, documents: List[Dict[str, Any]], 
                         training_examples: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process all documents into chunks, optionally including training examples"""
        all_chunks = []
        
        print(f"Creating chunks from {len(documents)} documents...")
        
        for doc in documents:
            chunks = self.create_chunks(doc["content"], doc["metadata"])
            all_chunks.extend(chunks)
            print(f"  {doc['id']}: {len(chunks)} chunks")
        
        # Add training examples as special chunks
        if training_examples:
            print(f"\nAdding {len(training_examples)} training examples...")
            for idx, example in enumerate(training_examples):
                chunk = {
                    "id": f"training_example_{idx}",
                    "content": f"Q: {example['query']}\nA: {example['response']}",
                    "metadata": {
                        "doc_id": f"training_{idx}",
                        "category": example.get('category', 'General'),
                        "source": example.get('source', 'chat_transcript'),
                        "type": "training_example",
                        "chunk_number": 0,
                        "chunk_char_count": len(example['query']) + len(example['response'])
                    }
                }
                all_chunks.append(chunk)
            print(f"  ✓ Added {len(training_examples)} training examples")
        
        print(f"\n✓ Created {len(all_chunks)} total chunks")
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict[str, Any]], output_path: str = "data/processed/final_chunks.json"):
        """Save chunks to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved chunks to {output_file}")
        
        # Generate chunk statistics
        stats = {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(len(c["content"]) for c in chunks) / len(chunks),
            "min_chunk_size": min(len(c["content"]) for c in chunks),
            "max_chunk_size": max(len(c["content"]) for c in chunks),
            "chunks_by_category": {}
        }
        
        for chunk in chunks:
            category = chunk["metadata"]["category"]
            stats["chunks_by_category"][category] = stats["chunks_by_category"].get(category, 0) + 1
        
        stats_file = output_file.parent / "chunk_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✓ Chunk statistics saved to {stats_file}")
        return stats

if __name__ == "__main__":
    # Load processed documents
    with open("data/processed/all_documents_cleaned.json", 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    # Load training examples if available
    training_examples = []
    training_file = Path("data/processed/training_examples.json")
    if training_file.exists():
        with open(training_file, 'r', encoding='utf-8') as f:
            training_examples = json.load(f)
        print(f"Loaded {len(training_examples)} training examples")
    
    # Create chunks
    chunker = SemanticChunker(chunk_size=500, overlap=50)
    chunks = chunker.process_documents(documents, training_examples)
    stats = chunker.save_chunks(chunks)
    
    print("\n" + "="*50)
    print("CHUNKING SUMMARY")
    print("="*50)
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"Avg Chunk Size: {stats['avg_chunk_size']:.0f} chars")
    print(f"Min/Max: {stats['min_chunk_size']}/{stats['max_chunk_size']} chars")
