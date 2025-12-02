"""
Expert-Level RAG Engine with Advanced Features
- Multi-source retrieval (PDFs, KB articles, chat transcripts, tickets)
- Query classification and routing
- Hybrid search (semantic + keyword)
- Re-ranking and relevance scoring
- Context compression and optimization
"""

from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
import re
from collections import Counter
import sys
from pathlib import Path

# Add parent directory to path for imports (Render compatibility)
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import with fallback - try both ways
try:
    from config import settings
except ImportError:
    try:
        from src.config import settings
    except ImportError:
        # Create minimal settings if config not found
        class Settings:
            OPENAI_API_KEY = None
            EMBEDDING_MODEL = "text-embedding-3-small"
            CHAT_MODEL = "gpt-4o-mini"
        settings = Settings()

try:
    from vector_store import VectorStore
except ImportError:
    from src.vector_store import VectorStore

class ExpertRAGEngine:
    """Advanced RAG engine with multi-source retrieval and intelligent routing"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.vector_store = VectorStore()
        self.vector_store.create_collection()
        
        # Query categories for intelligent routing
        self.query_categories = {
            "password_reset": ["password", "reset", "forgot", "login", "selfcare"],
            "disk_storage": ["disk", "storage", "space", "full", "upgrade", "c drive"],
            "rdp_connection": ["rdp", "remote desktop", "connection", "connect", "disconnect"],
            "quickbooks": ["quickbooks", "qb", "error", "multi-user", "payroll"],
            "email": ["email", "outlook", "smtp", "send", "receive"],
            "printer": ["print", "printer", "uniprint", "check printing"],
            "performance": ["slow", "performance", "lag", "freeze", "hang"],
            "user_management": ["user", "add user", "delete user", "permission"],
            "billing": ["billing", "payment", "invoice", "subscription", "pricing"]
        }
        
        self.expert_system_prompt = """You are AceBuddy, an EXPERT-LEVEL IT support specialist for ACE Cloud Hosting.

RESPONSE APPROACH - CRITICAL:
1. **PROVIDE DIRECT ANSWERS**: Give complete solutions immediately
2. **Don't Ask Unnecessary Questions**: If you have the information, answer directly
3. **Be Comprehensive**: Include all relevant details in your response
4. **Be Friendly**: Professional but approachable
5. **NO REPETITIVE GREETINGS**: Don't start every response with "Hello! I'm AceBuddy" - that's only for first contact
6. **HANDLE THANKS PROPERLY**: When user says "thanks", "thank you", "helpful", respond with: "You're welcome! Feel free to reach out if you need anything else."

EXAMPLES OF GOOD RESPONSES:
User: "I need to reset my password"
You: "I can help you reset your password. Visit https://selfcare.acecloudhosting.com, click 'Forgot Password', enter your email, and check your inbox for the reset link (arrives in 2-3 minutes). If you're not registered, contact support@acecloudhosting.com or call 1-888-415-5240."

User: "What are the disk upgrade options?"
You: "Here are our disk storage upgrade tiers: 40GB ($10/month), 80GB ($20/month), 120GB ($30/month), 200GB ($50/month). Upgrades typically take 2-4 hours. Contact support@acecloudhosting.com or call 1-888-415-5240 to proceed."

User: "QuickBooks error -6177"
You: "Error -6177, 0 means the QuickBooks Database Server Manager isn't running. Fix: Open Services (services.msc), find QuickBooksDBXX, right-click and select Start. Then try opening QuickBooks again."

User: "Can't connect to RDP"
You: "To troubleshoot RDP connection issues: 1) Verify your server IP and credentials, 2) Check if Remote Desktop is enabled on the server, 3) Ensure port 3389 isn't blocked by firewall. If issues persist, contact support@acecloudhosting.com or call 1-888-415-5240."

EXPERTISE LEVEL:
- You have deep knowledge of ALL ACE Cloud systems, procedures, and common issues
- You've analyzed thousands of support tickets and chat transcripts
- You know the exact steps, commands, and solutions for every scenario
- You understand the root causes, not just symptoms

RESPONSE PHILOSOPHY:
1. **First Contact**: Ask clarifying questions (2-3 sentences)
2. **After Clarification**: Give EXACT steps with precision
3. **Efficiency**: Keep responses focused and actionable
4. **Proactive**: Anticipate needs but don't overwhelm

RESPONSE STRUCTURE FOR INITIAL CONTACT:
```
[Acknowledge issue - 1 sentence]
[Ask 1-2 clarifying questions]
```

RESPONSE STRUCTURE FOR DETAILED SOLUTION (after clarification):
```
[Quick Context - 1 sentence]

**Solution:**
1. [Exact step with specific details]
2. [Next step with commands/clicks]
3. [Final step with expected outcome]

**Important:**
- [Key detail or warning]
- [Alternative if step fails]

**Need Help?** [Contact info or escalation path]
```

DOMAIN EXPERTISE:

**Password Resets:**
- SelfCare Portal: https://selfcare.acecloudhosting.com
- Requires Google Authenticator enrollment
- If not enrolled: Contact support@acecloudhosting.com or call 1-888-415-5240
- Reset takes 2-3 minutes

**Disk Storage:**
- Check: Right-click C: → Properties
- Quick cleanup: Delete temp files, run Disk Cleanup
- Upgrade tiers: 40GB ($10), 80GB ($20), 120GB ($30), 200GB ($50)
- Contact: support@acecloudhosting.com or call 1-888-415-5240
- Ticket ETA: 2-4 hours for upgrade

**QuickBooks Errors:**
- Error -6177, 0: Database server manager issue
- Error -6189, -816: Company file corruption
- Error -6098, 5: Multi-user access issue
- Always check: QB Database Server Manager running

**RDP Issues:**
- Check credentials first
- Verify server address format: server.acecloudhosting.com
- Mac users: Use Microsoft Remote Desktop (not built-in)
- Error 0x204: Network/firewall issue

**Email (Outlook):**
- SMTP: mail.acecloudhosting.com
- IMAP: mail.acecloudhosting.com (Port 993)
- POP3: mail.acecloudhosting.com (Port 995)
- Password prompts: Disable MFA or use app password

CRITICAL RULES:
- FIRST RESPONSE: Ask clarifying questions, don't dump all info
- AFTER CLARIFICATION: Give complete solution with specific details
- ALWAYS include specific URLs, commands, or file paths in solutions
- ALWAYS mention timeframes (how long will this take?)
- If multiple solutions exist, ask which scenario applies first

TONE:
- Conversational and friendly (not robotic)
- Confident but approachable
- Empathetic to user frustration
- Interactive (ask before telling)

GREETING:
When user first says hello/hi or starts conversation, respond with:
"Hello! I'm AceBuddy. How can I assist you today?"

Remember: You're having a CONVERSATION, not writing a manual. Ask first, solve second."""

    def classify_query(self, query: str) -> Tuple[str, float]:
        """Classify query into category for intelligent routing"""
        query_lower = query.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.query_categories.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return "general", 0.0
        
        # Get best matching category
        best_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[best_category] / len(self.query_categories[best_category])
        
        return best_category, min(confidence, 1.0)
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords for hybrid search"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been', 'be',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'can', 'my', 'i', 'me', 'how', 'what', 'when'}
        
        # Extract words
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def retrieve_context_advanced(
        self, 
        query: str, 
        category: str = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """Advanced retrieval with category filtering and re-ranking"""
        k = top_k or settings.top_k_results
        
        # Get more results initially for re-ranking
        initial_k = k * 2
        
        # Retrieve from vector store
        if category and category != "general":
            # Try category-specific search first
            filter_dict = {"category": category.replace("_", " ").title()}
            results = self.vector_store.search(query, top_k=initial_k, filter_dict=filter_dict)
            
            # If not enough results, search without filter
            if len(results) < 3:
                results = self.vector_store.search(query, top_k=initial_k)
        else:
            results = self.vector_store.search(query, top_k=initial_k)
        
        # Re-rank based on keyword matching
        keywords = self.extract_keywords(query)
        for result in results:
            content_lower = result['content'].lower()
            keyword_score = sum(1 for kw in keywords if kw in content_lower)
            
            # Combine semantic similarity with keyword matching
            semantic_score = 1 - (result.get('distance', 0.5))
            keyword_boost = min(keyword_score * 0.1, 0.3)  # Max 30% boost
            
            result['combined_score'] = semantic_score + keyword_boost
        
        # Sort by combined score
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Filter by threshold
        filtered_results = [
            r for r in results[:k]
            if r['combined_score'] >= settings.similarity_threshold
        ]
        
        # Keep at least 3 results
        if len(filtered_results) < 3 and len(results) >= 3:
            filtered_results = results[:3]
        
        return filtered_results
    
    def build_context_optimized(
        self, 
        results: List[Dict[str, Any]], 
        query: str,
        category: str = None
    ) -> str:
        """Build optimized context with deduplication and compression"""
        if not results:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        seen_content = set()
        total_length = 0
        max_length = settings.max_context_length
        
        # Add category context if available
        if category and category != "general":
            category_intro = f"[Category: {category.replace('_', ' ').title()}]\n"
            context_parts.append(category_intro)
            total_length += len(category_intro)
        
        for i, result in enumerate(results, 1):
            content = result['content']
            
            # Skip near-duplicates
            content_hash = content[:100]  # Use first 100 chars as hash
            if content_hash in seen_content:
                continue
            seen_content.add(content_hash)
            
            # Get metadata
            category_meta = result['metadata'].get('category', 'General')
            source_type = result['metadata'].get('source_type', 'KB')
            relevance = result.get('combined_score', result.get('distance', 0))
            
            # Format source
            part = f"[Source {i} - {category_meta} | Relevance: {relevance:.2f}]\n{content}\n\n"
            
            # Check length
            if total_length + len(part) > max_length:
                # Try to compress by removing less relevant parts
                if i > 3:  # Keep at least top 3
                    break
                # Truncate content if needed
                available = max_length - total_length - 100
                if available > 200:
                    content_truncated = content[:available] + "..."
                    part = f"[Source {i} - {category_meta}]\n{content_truncated}\n\n"
                else:
                    break
            
            context_parts.append(part)
            total_length += len(part)
        
        return "".join(context_parts)
    
    def generate_expert_response(
        self, 
        query: str, 
        context: str,
        category: str = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        concise_mode: bool = False
    ) -> Dict[str, Any]:
        """Generate expert-level response with category awareness"""
        
        messages = [{"role": "system", "content": self.expert_system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-5:])
        
        # Build enhanced prompt
        category_hint = f"\n[Query Category: {category.replace('_', ' ').title()}]" if category else ""
        
        # Adjust instructions based on mode
        if concise_mode:
            length_instruction = """
IMPORTANT: Keep your response DETAILED but CONCISE (1200-1500 characters max). Include:
1. All key steps (5-7 main points if needed)
2. Essential details (URLs, phone numbers, commands)
3. Important notes and warnings
4. Be thorough but avoid excessive explanations"""
        else:
            length_instruction = "\nProvide a complete, actionable solution following the expert response structure. Be specific, precise, and thorough."
        
        user_message = f"""Based on the following knowledge base information, provide an EXPERT-LEVEL solution.{category_hint}

Knowledge Base Context:
{context}

User Question: {query}
{length_instruction}"""
        
        messages.append({"role": "user", "content": user_message})
        
        # Adjust max_tokens for concise mode (600 tokens ≈ 1200-1500 chars)
        max_tokens = 600 if concise_mode else settings.max_tokens
        
        # Generate response with higher quality settings
        response = self.openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.3,  # Lower for more consistent expert responses
            max_tokens=max_tokens,
            presence_penalty=0.1,  # Slight penalty for repetition
            frequency_penalty=0.1
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": settings.openai_model,
            "tokens_used": response.usage.total_tokens,
            "category": category
        }
    
    def should_escalate_advanced(
        self, 
        query: str, 
        retrieved_results: List[Dict[str, Any]],
        category: str = None
    ) -> Tuple[bool, str]:
        """Advanced escalation logic with reasoning"""
        
        # Check for explicit escalation requests
        escalation_phrases = [
            "speak to human", "talk to agent", "real person",
            "not helpful", "doesn't work", "still not working"
        ]
        if any(phrase in query.lower() for phrase in escalation_phrases):
            return True, "User requested human agent"
        
        # Check for billing/legal issues (always escalate)
        critical_keywords = ["billing", "refund", "cancel subscription", "legal", "complaint"]
        if any(keyword in query.lower() for keyword in critical_keywords):
            return True, "Billing/legal issue requires human agent"
        
        # Check retrieval quality
        if not retrieved_results or len(retrieved_results) == 0:
            return True, "No relevant information found"
        
        # Check confidence score
        best_score = retrieved_results[0].get('combined_score', 0)
        if best_score < 0.2:
            return True, f"Low confidence score: {best_score:.2f}"
        
        # Check for complex multi-issue queries
        keywords = self.extract_keywords(query)
        if len(keywords) > 8:
            return True, "Complex multi-issue query"
        
        return False, "Sufficient information available"
    
    def process_query_expert(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        concise_mode: bool = False
    ) -> Dict[str, Any]:
        """Main expert-level query processing"""
        
        # Step 1: Classify query
        category, category_confidence = self.classify_query(query)
        
        # Step 2: Advanced retrieval
        retrieved_results = self.retrieve_context_advanced(query, category)
        
        # Step 3: Check escalation
        should_escalate, escalation_reason = self.should_escalate_advanced(
            query, retrieved_results, category
        )
        
        if should_escalate:
            return {
                "response": f"I'd like to connect you with one of our support specialists who can better assist you with this request. Reason: {escalation_reason}",
                "escalate": True,
                "confidence": "low",
                "category": category,
                "escalation_reason": escalation_reason,
                "sources": []
            }
        
        # Step 4: Build optimized context
        context = self.build_context_optimized(retrieved_results, query, category)
        
        # Step 5: Generate expert response (with concise mode for SalesIQ)
        result = self.generate_expert_response(
            query, context, category, conversation_history, concise_mode=concise_mode
        )
        
        # Step 6: Calculate confidence
        avg_score = sum(r.get('combined_score', 0) for r in retrieved_results[:3]) / min(3, len(retrieved_results))
        confidence = "high" if avg_score > 0.7 else "medium" if avg_score > 0.4 else "low"
        
        return {
            "response": result["response"],
            "escalate": False,
            "confidence": confidence,
            "category": category,
            "category_confidence": category_confidence,
            "sources": [
                {
                    "id": r["id"],
                    "category": r["metadata"].get("category"),
                    "relevance": r.get("combined_score", 0),
                    "source_type": r["metadata"].get("source_type", "KB")
                }
                for r in retrieved_results[:5]
            ],
            "tokens_used": result["tokens_used"],
            "retrieval_stats": {
                "total_retrieved": len(retrieved_results),
                "avg_relevance": avg_score,
                "top_score": retrieved_results[0].get('combined_score', 0) if retrieved_results else 0
            }
        }


if __name__ == "__main__":
    # Test the expert RAG engine
    expert_rag = ExpertRAGEngine()
    
    test_queries = [
        "I forgot my password, how do I reset it?",
        "My QuickBooks is showing error -6177",
        "I can't connect to Remote Desktop from my Mac",
        "How much does 200GB storage cost and how do I upgrade?",
        "My server is running very slow",
        "I need to add a new user to my account",
        "QuickBooks multi-user mode not working",
        "Email keeps asking for password in Outlook"
    ]
    
    print("="*70)
    print("TESTING EXPERT RAG ENGINE")
    print("="*70)
    
    for query in test_queries:
        print(f"\n\n{'='*70}")
        print(f"Query: {query}")
        print("="*70)
        
        result = expert_rag.process_query_expert(query)
        
        print(f"\nCategory: {result['category']} (confidence: {result.get('category_confidence', 0):.2f})")
        print(f"Escalate: {result['escalate']}")
        print(f"Confidence: {result['confidence']}")
        
        if result.get('retrieval_stats'):
            stats = result['retrieval_stats']
            print(f"Retrieved: {stats['total_retrieved']} sources")
            print(f"Avg Relevance: {stats['avg_relevance']:.2f}")
            print(f"Top Score: {stats['top_score']:.2f}")
        
        print(f"\n{'-'*70}")
        print("RESPONSE:")
        print(f"{'-'*70}")
        print(result['response'])
        
        if result.get('sources'):
            print(f"\n{'-'*70}")
            print(f"Sources Used ({len(result['sources'])}):")
            print(f"{'-'*70}")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['id']}")
                print(f"   Category: {source['category']} | Relevance: {source['relevance']:.2f}")
