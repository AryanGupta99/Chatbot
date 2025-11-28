"""
Build Knowledge Base for Deployment (Non-Interactive)
"""

import sys
from build_focused_kb import build_focused_knowledge_base, rebuild_vector_store_with_focused_data

if __name__ == "__main__":
    print("\n🚀 Building Knowledge Base for Deployment\n")
    
    try:
        # Build chunks
        chunks = build_focused_knowledge_base()
        
        # Rebuild vector store
        success = rebuild_vector_store_with_focused_data(chunks)
        
        if success:
            print("\n✅ Knowledge base built successfully!")
            sys.exit(0)
        else:
            print("\n❌ Failed to build knowledge base")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
