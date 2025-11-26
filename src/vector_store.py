import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from config import settings

class VectorStore:
    """Manages vector database operations with ChromaDB"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.collection = None
    
    def create_collection(self, collection_name: str = None):
        """Create or get collection"""
        name = collection_name or settings.collection_name
        
        try:
            self.collection = self.client.get_collection(name=name)
            print(f"✓ Loaded existing collection: {name}")
        except:
            self.collection = self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✓ Created new collection: {name}")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        embeddings = []
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.openai_client.embeddings.create(
                model=settings.openai_embedding_model,
                input=batch
            )
            embeddings.extend([item.embedding for item in response.data])
        
        return embeddings
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Add document chunks to vector store"""
        if not self.collection:
            self.create_collection()
        
        print(f"Adding {len(chunks)} chunks to vector store...")
        
        # Prepare data
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.get_embeddings(documents)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))
            
            self.collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
            print(f"  Added batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
        
        print(f"✓ Successfully added {len(chunks)} chunks to vector store")
    
    def search(self, query: str, top_k: int = None, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if not self.collection:
            self.create_collection()
        
        k = top_k or settings.top_k_results
        
        # Generate query embedding
        query_embedding = self.get_embeddings([query])[0]
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_dict
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        if not self.collection:
            return {"error": "No collection loaded"}
        
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name
        }

if __name__ == "__main__":
    # Load chunks
    chunks_file = Path("data/processed/final_chunks.json")
    
    if not chunks_file.exists():
        print("Error: Run data_processor.py and chunker.py first!")
        exit(1)
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Initialize vector store
    vector_store = VectorStore()
    vector_store.create_collection()
    
    # Add documents
    vector_store.add_documents(chunks)
    
    # Test search
    print("\n" + "="*50)
    print("TESTING SEARCH")
    print("="*50)
    
    test_queries = [
        "How do I reset my password?",
        "QuickBooks error codes",
        "RDP connection issues"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = vector_store.search(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['id']} (distance: {result['distance']:.3f})")
            print(f"     {result['content'][:100]}...")
