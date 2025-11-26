from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import settings
from src.vector_store import VectorStore

class RAGEngine:
    """Core RAG engine for query processing and response generation"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.vector_store = VectorStore()
        self.vector_store.create_collection()
        
        self.system_prompt = """You are AceBuddy, an intelligent IT support assistant for ACE Cloud services.

Your role:
- Provide accurate, helpful technical support based on the knowledge base
- Be concise but thorough in your responses
- Use step-by-step instructions when appropriate
- If you're not confident about an answer, say so and offer to escalate to a human agent
- Always maintain a professional, friendly tone

Guidelines:
- Focus on QuickBooks, Remote Desktop, Email, Server, and User Management issues
- Provide specific error codes and solutions when available
- Include relevant troubleshooting steps
- Mention expected resolution times when known
- If the query is outside your knowledge base, politely escalate to human support

Remember: Your goal is to resolve issues quickly and accurately, improving on the current 11% automation rate."""
    
    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieve relevant context from vector store"""
        results = self.vector_store.search(query, top_k=top_k or settings.top_k_results)
        
        # Filter by similarity threshold - but keep at least 3 results
        filtered_results = [
            r for r in results 
            if r['distance'] is None or (1 - r['distance']) >= settings.similarity_threshold
        ]
        
        # If we filtered out too many, keep the top 3 anyway
        if len(filtered_results) < 3 and len(results) >= 3:
            filtered_results = results[:3]
        elif len(filtered_results) == 0 and len(results) > 0:
            filtered_results = results[:1]
        
        return filtered_results
    
    def build_context_string(self, results: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents"""
        if not results:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        total_length = 0
        
        for i, result in enumerate(results, 1):
            content = result['content']
            category = result['metadata'].get('category', 'General')
            
            part = f"[Source {i} - {category}]\n{content}\n"
            
            if total_length + len(part) > settings.max_context_length:
                break
            
            context_parts.append(part)
            total_length += len(part)
        
        return "\n".join(context_parts)
    
    def generate_response(
        self, 
        query: str, 
        context: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate response using OpenAI with retrieved context"""
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages for context
        
        # Add current query with context
        user_message = f"""Based on the following knowledge base information, please answer the user's question.

Knowledge Base Context:
{context}

User Question: {query}

Please provide a helpful, accurate response. If the information isn't in the knowledge base, let the user know and offer to escalate to a human agent."""
        
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        response = self.openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": settings.openai_model,
            "tokens_used": response.usage.total_tokens
        }
    
    def should_escalate(self, query: str, retrieved_results: List[Dict[str, Any]]) -> bool:
        """Determine if query should be escalated to human agent"""
        # No relevant results found at all
        if not retrieved_results or len(retrieved_results) == 0:
            return True
        
        # Very low confidence (very high distance) - only escalate if really bad
        if retrieved_results[0].get('distance'):
            confidence = 1 - retrieved_results[0]['distance']
            # Only escalate if confidence is extremely low
            if confidence < 0.15:
                return True
        
        # Check for escalation keywords - only truly urgent ones
        escalation_keywords = [
            "billing", "payment", "cancel subscription", "refund", 
            "complaint", "speak to manager", "legal"
        ]
        
        if any(keyword in query.lower() for keyword in escalation_keywords):
            return True
        
        return False
    
    def process_query(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Main method to process a user query"""
        
        # Retrieve relevant context
        retrieved_results = self.retrieve_context(query)
        
        # Check if should escalate
        if self.should_escalate(query, retrieved_results):
            return {
                "response": "I'd like to connect you with one of our support specialists who can better assist you with this request. Please hold while I transfer you.",
                "escalate": True,
                "confidence": "low",
                "sources": []
            }
        
        # Build context
        context = self.build_context_string(retrieved_results)
        
        # Generate response
        result = self.generate_response(query, context, conversation_history)
        
        return {
            "response": result["response"],
            "escalate": False,
            "confidence": "high" if retrieved_results else "medium",
            "sources": [
                {
                    "id": r["id"],
                    "category": r["metadata"].get("category"),
                    "relevance": 1 - r["distance"] if r.get("distance") else None
                }
                for r in retrieved_results[:3]
            ],
            "tokens_used": result["tokens_used"]
        }

if __name__ == "__main__":
    # Test the RAG engine
    rag = RAGEngine()
    
    test_queries = [
        "I forgot my password, how do I reset it?",
        "My QuickBooks is showing error -6177",
        "I can't connect to Remote Desktop",
        "How much does 200GB storage cost?",
        "I need urgent help with billing"
    ]
    
    print("="*50)
    print("TESTING RAG ENGINE")
    print("="*50)
    
    for query in test_queries:
        print(f"\n\nQuery: {query}")
        print("-" * 50)
        
        result = rag.process_query(query)
        
        print(f"Escalate: {result['escalate']}")
        print(f"Confidence: {result['confidence']}")
        print(f"\nResponse:\n{result['response']}")
        
        if result.get('sources'):
            print(f"\nSources: {len(result['sources'])}")
            for source in result['sources']:
                print(f"  - {source['id']} ({source['category']})")
