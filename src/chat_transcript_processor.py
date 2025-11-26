"""
Chat Transcript Processor
Processes PDF chat transcripts from Zoho SalesIQ to learn:
- Real user queries and language patterns
- Successful resolution patterns
- Escalation triggers
- Common issues and solutions
- Agent response patterns
"""

import json
import pdfplumber
import PyPDF2
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import re

class ChatTranscriptProcessor:
    """Process PDF chat transcripts to extract learning patterns"""
    
    def __init__(self, transcript_dir: str = "data/Chat Transcripts"):
        self.transcript_dir = Path(transcript_dir)
        self.output_dir = Path("data/processed")
        self.output_dir.mkdir(exist_ok=True)
    
    def load_pdf_transcripts(self) -> List[Dict[str, Any]]:
        """Load all PDF chat transcript files from monthly folders"""
        transcripts = []
        
        # Get all monthly folders
        monthly_folders = [d for d in self.transcript_dir.iterdir() if d.is_dir()]
        
        print(f"\n{'='*60}")
        print(f"LOADING CHAT TRANSCRIPTS FROM {len(monthly_folders)} MONTHS")
        print(f"{'='*60}\n")
        
        for folder in sorted(monthly_folders):
            month_name = folder.name.split('_')[1]  # Extract month (e.g., JAN, FEB)
            pdf_files = list(folder.glob("*.pdf"))
            
            print(f"Processing {month_name} ({len(pdf_files)} PDF files)...", end=" ")
            
            month_conversations = 0
            for pdf_file in pdf_files:
                try:
                    conversations = self._extract_conversations_from_pdf(pdf_file, month_name)
                    transcripts.extend(conversations)
                    month_conversations += len(conversations)
                except Exception as e:
                    print(f"\n  ⚠️  Error in {pdf_file.name}: {e}")
            
            print(f"✅ {month_conversations} conversations")
        
        return transcripts
    
    def _extract_conversations_from_pdf(self, pdf_path: Path, month: str) -> List[Dict[str, Any]]:
        """Extract individual conversations from PDF transcript"""
        conversations = []
        
        try:
            # Extract text from PDF
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Parse conversations from text
            # Zoho SalesIQ transcripts typically have patterns like:
            # Visitor: [message]
            # Agent/Bot: [response]
            # Or similar patterns
            
            parsed_conversations = self._parse_chat_text(text, pdf_path.name, month)
            conversations.extend(parsed_conversations)
            
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    
                    parsed_conversations = self._parse_chat_text(text, pdf_path.name, month)
                    conversations.extend(parsed_conversations)
            except:
                pass
        
        return conversations
    
    def _parse_chat_text(self, text: str, source_file: str, month: str) -> List[Dict[str, Any]]:
        """Parse chat conversations from extracted text"""
        conversations = []
        
        # Split by common conversation delimiters
        # Adjust these patterns based on your actual PDF format
        conversation_patterns = [
            r'(?:Conversation|Chat)\s*#?\d+',  # Conversation #123
            r'={3,}',  # === separator
            r'-{3,}',  # --- separator
            r'Visitor\s+ID:',  # Visitor ID: marker
            r'Chat\s+started',  # Chat started marker
        ]
        
        # Try each pattern
        for pattern in conversation_patterns:
            parts = re.split(pattern, text, flags=re.IGNORECASE)
            if len(parts) > 2:  # Found multiple conversations
                for part in parts[1:]:  # Skip first empty part
                    if len(part.strip()) > 100:  # Minimum conversation length
                        conv = self._extract_conversation_data(part, source_file, month)
                        if conv:
                            conversations.append(conv)
                break
        
        # If no pattern matched, treat entire text as one conversation
        if not conversations and len(text.strip()) > 100:
            conv = self._extract_conversation_data(text, source_file, month)
            if conv:
                conversations.append(conv)
        
        return conversations
    
    def load_text_transcripts(self) -> List[Dict[str, Any]]:
        """Load text-based transcript files"""
        transcripts = []
        text_files = list(self.transcript_dir.glob("*.txt"))
        
        for text_file in text_files:
            print(f"Loading {text_file.name}...", end=" ")
            
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse conversations (adjust based on format)
                conversations = self._parse_text_conversations(content)
                transcripts.extend(conversations)
                
                print(f"✅ {len(conversations)} conversations")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return transcripts
    
    def _parse_text_conversations(self, content: str) -> List[Dict[str, Any]]:
        """Parse text-based conversation format"""
        conversations = []
        
        # Split by common delimiters
        # Adjust regex based on your actual format
        patterns = [
            r'---+',  # Dashes
            r'={3,}',  # Equals signs
            r'\n\n\n+',  # Multiple newlines
        ]
        
        for pattern in patterns:
            parts = re.split(pattern, content)
            if len(parts) > 1:
                for part in parts:
                    if len(part.strip()) > 50:
                        conv = self._extract_conversation_data(part)
                        if conv:
                            conversations.append(conv)
                break
        
        return conversations
    
    def _extract_conversation_data(self, text: str, source_file: str, month: str) -> Dict[str, Any]:
        """Extract structured data from conversation text"""
        
        # Extract visitor messages (user queries)
        visitor_patterns = [
            r'(?:Visitor|User|Customer):\s*(.+?)(?=(?:Agent|Bot|Operator):|$)',
            r'(?:Visitor|User|Customer)\s+says?:\s*(.+?)(?=(?:Agent|Bot|Operator):|$)',
            r'\[Visitor\]:\s*(.+?)(?=\[(?:Agent|Bot|Operator)\]:|$)',
        ]
        
        # Extract agent/bot responses
        agent_patterns = [
            r'(?:Agent|Bot|Operator|AceBuddy):\s*(.+?)(?=(?:Visitor|User|Customer):|$)',
            r'(?:Agent|Bot|Operator|AceBuddy)\s+says?:\s*(.+?)(?=(?:Visitor|User|Customer):|$)',
            r'\[(?:Agent|Bot|Operator|AceBuddy)\]:\s*(.+?)(?=\[(?:Visitor|User|Customer)\]:|$)',
        ]
        
        visitor_messages = []
        agent_messages = []
        
        # Extract all visitor messages
        for pattern in visitor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                visitor_messages.extend([m.strip() for m in matches if len(m.strip()) > 5])
                break
        
        # Extract all agent messages
        for pattern in agent_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                agent_messages.extend([m.strip() for m in matches if len(m.strip()) > 5])
                break
        
        # If patterns didn't work, try simple line-by-line parsing
        if not visitor_messages and not agent_messages:
            lines = text.split('\n')
            current_speaker = None
            current_message = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line starts with speaker indicator
                if any(word in line.lower() for word in ['visitor:', 'user:', 'customer:']):
                    if current_speaker == 'agent' and current_message:
                        agent_messages.append(' '.join(current_message))
                    current_speaker = 'visitor'
                    current_message = [line.split(':', 1)[1].strip() if ':' in line else line]
                elif any(word in line.lower() for word in ['agent:', 'bot:', 'operator:', 'acebuddy:']):
                    if current_speaker == 'visitor' and current_message:
                        visitor_messages.append(' '.join(current_message))
                    current_speaker = 'agent'
                    current_message = [line.split(':', 1)[1].strip() if ':' in line else line]
                elif current_speaker:
                    current_message.append(line)
            
            # Add last message
            if current_speaker == 'visitor' and current_message:
                visitor_messages.append(' '.join(current_message))
            elif current_speaker == 'agent' and current_message:
                agent_messages.append(' '.join(current_message))
        
        # Create conversation object
        if visitor_messages:
            # Combine all visitor messages as query
            query = ' | '.join(visitor_messages[:3])  # First 3 messages
            response = ' | '.join(agent_messages[:3]) if agent_messages else ""
            
            # Determine if resolved
            resolved = any(word in text.lower() for word in ['resolved', 'solved', 'fixed', 'thank you', 'thanks'])
            
            return {
                'query': query[:500],  # Limit length
                'response': response[:500],
                'full_conversation': text[:2000],  # Keep full context
                'visitor_message_count': len(visitor_messages),
                'agent_message_count': len(agent_messages),
                'resolved': resolved,
                'month': month,
                'source_file': source_file,
                'processed_at': datetime.now().isoformat()
            }
        
        return None
    
    def analyze_patterns(self, transcripts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns from transcripts"""
        print(f"\n{'='*60}")
        print("ANALYZING CHAT PATTERNS")
        print(f"{'='*60}\n")
        
        analysis = {
            "total_conversations": len(transcripts),
            "common_queries": {},
            "common_keywords": {},
            "categories": {},
            "resolution_patterns": [],
            "escalation_triggers": []
        }
        
        # Extract common queries
        queries = [t.get('query', '') for t in transcripts if t.get('query')]
        
        # Categorize queries
        for transcript in transcripts:
            query = transcript.get('query', '').lower()
            
            # Categorize
            category = self._categorize_query(query)
            analysis['categories'][category] = analysis['categories'].get(category, 0) + 1
            
            # Extract keywords
            keywords = self._extract_keywords(query)
            for keyword in keywords:
                analysis['common_keywords'][keyword] = analysis['common_keywords'].get(keyword, 0) + 1
        
        # Find top patterns
        analysis['top_keywords'] = sorted(
            analysis['common_keywords'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        return analysis
    
    def _categorize_query(self, query: str) -> str:
        """Categorize query based on content"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['password', 'reset', 'login', 'access', 'locked']):
            return "Password/Login"
        elif any(word in query_lower for word in ['quickbooks', 'qb', 'accounting', 'invoice']):
            return "QuickBooks"
        elif any(word in query_lower for word in ['rdp', 'remote', 'desktop', 'connection', 'connect']):
            return "Remote Desktop"
        elif any(word in query_lower for word in ['email', 'outlook', 'office', '365', 'mail']):
            return "Email"
        elif any(word in query_lower for word in ['server', 'slow', 'performance', 'storage', 'disk']):
            return "Server"
        elif any(word in query_lower for word in ['printer', 'print', 'printing']):
            return "Printer"
        elif any(word in query_lower for word in ['user', 'add', 'delete', 'remove']):
            return "User Management"
        elif any(word in query_lower for word in ['error', 'issue', 'problem', 'not working']):
            return "General Error"
        else:
            return "Other"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                     'i', 'you', 'we', 'they', 'my', 'your', 'our', 'can', 'could', 'would',
                     'please', 'help', 'need', 'want', 'how', 'what', 'when', 'where'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        return keywords
    
    def create_training_examples(self, transcripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create training examples from successful resolutions"""
        training_examples = []
        
        for transcript in transcripts:
            query = transcript.get('query', '')
            response = transcript.get('response', '')
            resolved = transcript.get('resolved', False)
            visitor_count = transcript.get('visitor_message_count', 0)
            agent_count = transcript.get('agent_message_count', 0)
            
            # Quality criteria for training examples:
            # 1. Has both query and response
            # 2. Response is substantial (>30 chars)
            # 3. Either marked as resolved OR has good back-and-forth
            # 4. Not too short (indicates incomplete conversation)
            
            if (query and response and 
                len(response) > 30 and 
                (resolved or (visitor_count >= 1 and agent_count >= 1))):
                
                training_examples.append({
                    "query": query,
                    "response": response,
                    "category": self._categorize_query(query),
                    "month": transcript.get('month', 'unknown'),
                    "source": transcript.get('source_file', 'unknown'),
                    "resolved": resolved,
                    "quality_score": self._calculate_quality_score(transcript)
                })
        
        # Sort by quality score and return top examples
        training_examples.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        return training_examples
    
    def _calculate_quality_score(self, transcript: Dict[str, Any]) -> float:
        """Calculate quality score for training example"""
        score = 0.0
        
        # Longer responses are generally better
        response_len = len(transcript.get('response', ''))
        score += min(response_len / 100, 5.0)  # Max 5 points
        
        # Resolved conversations are better
        if transcript.get('resolved', False):
            score += 3.0
        
        # Good back-and-forth indicates engagement
        visitor_count = transcript.get('visitor_message_count', 0)
        agent_count = transcript.get('agent_message_count', 0)
        score += min(visitor_count + agent_count, 5.0)  # Max 5 points
        
        # Penalize very short queries
        query_len = len(transcript.get('query', ''))
        if query_len < 20:
            score -= 2.0
        
        return max(score, 0.0)
    
    def save_processed_transcripts(self, transcripts: List[Dict[str, Any]], 
                                   analysis: Dict[str, Any],
                                   training_examples: List[Dict[str, Any]]):
        """Save processed transcript data"""
        
        # Save all transcripts
        transcripts_file = self.output_dir / "chat_transcripts.json"
        with open(transcripts_file, 'w', encoding='utf-8') as f:
            json.dump(transcripts, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(transcripts)} transcripts to {transcripts_file}")
        
        # Save analysis
        analysis_file = self.output_dir / "chat_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved analysis to {analysis_file}")
        
        # Save training examples
        training_file = self.output_dir / "training_examples.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(training_examples, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(training_examples)} training examples to {training_file}")
    
    def process_all(self):
        """Process all chat transcripts"""
        # Load PDF transcripts from monthly folders
        pdf_transcripts = self.load_pdf_transcripts()
        
        # Also load any text files if they exist
        text_transcripts = self.load_text_transcripts()
        
        all_transcripts = pdf_transcripts + text_transcripts
        
        print(f"\n✅ Loaded {len(all_transcripts)} total conversations from PDFs")
        
        # Analyze patterns
        analysis = self.analyze_patterns(all_transcripts)
        
        # Create training examples
        training_examples = self.create_training_examples(all_transcripts)
        
        # Save everything
        self.save_processed_transcripts(all_transcripts, analysis, training_examples)
        
        # Print summary
        print(f"\n{'='*60}")
        print("CHAT TRANSCRIPT SUMMARY")
        print(f"{'='*60}")
        print(f"Total Conversations: {len(all_transcripts)}")
        print(f"Training Examples: {len(training_examples)}")
        print(f"\nTop Categories:")
        for category, count in sorted(analysis['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {category}: {count}")
        print(f"\nTop Keywords:")
        for keyword, count in analysis['top_keywords'][:10]:
            print(f"  - {keyword}: {count}")
        
        return all_transcripts, analysis, training_examples

if __name__ == "__main__":
    processor = ChatTranscriptProcessor()
    transcripts, analysis, training_examples = processor.process_all()
