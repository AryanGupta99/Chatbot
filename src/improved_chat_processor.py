"""
Improved Chat Transcript Processor
Extracts clean, meaningful Q&A pairs from chat transcripts
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class ImprovedChatProcessor:
    """Extract clean Q&A pairs from chat transcripts"""
    
    def __init__(self):
        self.output_dir = Path("data/processed")
        self.output_dir.mkdir(exist_ok=True)
    
    def clean_message(self, text: str) -> str:
        """Remove timestamps, names, and metadata from message"""
        # Remove timestamps (various formats)
        text = re.sub(r'\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)?', '', text)
        text = re.sub(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[,\s]+\d{1,2}:\d{2}:\d{2}', '', text)
        
        # Remove agent names (common patterns)
        agent_names = ['Rohan Prajapati', 'Yash Kalra', 'Shubham Maurya', 'Tushar Pharswan', 
                      'Shubham Kataria', 'Abhay Kumar', 'Anjainay Singh']
        for name in agent_names:
            text = text.replace(name, '')
        
        # Remove metadata lines
        metadata_patterns = [
            r'Website:\s*https?://\S+',
            r'Operating System:.*',
            r'Browser:.*',
            r'Device:.*',
            r'City:.*',
            r'State:.*',
            r'Country:.*',
            r'Chat Duration:.*',
            r'Average Response Time:.*',
            r'Email:.*',
            r'Department:.*',
            r'Visitor Details.*',
            r'Chat Transcript.*',
            r'#\d+\s+\w+\s+\w+',  # Visitor IDs
        ]
        
        for pattern in metadata_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_qa_pairs(self, conversation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract clean Q&A pairs from a conversation"""
        qa_pairs = []
        
        query = conversation.get('query', '')
        response = conversation.get('response', '')
        
        if not query or not response:
            return []
        
        # Clean both
        clean_query = self.clean_message(query)
        clean_response = self.clean_message(response)
        
        # Quality checks
        if len(clean_query) < 10 or len(clean_response) < 20:
            return []
        
        # Remove if too much noise
        if clean_query.count('|') > 5 or clean_response.count('|') > 5:
            return []
        
        # Extract actual question/issue
        question = self._extract_question(clean_query)
        answer = self._extract_answer(clean_response)
        
        if question and answer:
            qa_pairs.append({
                'query': question,
                'response': answer,
                'category': conversation.get('category', 'General'),
                'resolved': conversation.get('resolved', False),
                'month': conversation.get('month', 'unknown')
            })
        
        return qa_pairs
    
    def _extract_question(self, text: str) -> Optional[str]:
        """Extract the actual question/issue from user message"""
        # Remove common chat prefixes
        text = re.sub(r'^(?:Visitor|User|Customer):\s*', '', text, flags=re.IGNORECASE)
        
        # Look for question patterns
        question_patterns = [
            r'(?:how|what|when|where|why|can|could|would|is|are|do|does).*\?',
            r'(?:i need|i want|i have|i\'m having|i\'m getting|i can\'t|i cannot).*',
            r'(?:error|issue|problem|not working|doesn\'t work).*',
            r'(?:help|assist|support).*',
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                question = match.group(0).strip()
                # Limit length
                if len(question) > 200:
                    question = question[:200] + '...'
                return question
        
        # If no pattern matched, take first sentence
        sentences = re.split(r'[.!?]', text)
        if sentences and len(sentences[0]) > 10:
            return sentences[0].strip()[:200]
        
        return None
    
    def _extract_answer(self, text: str) -> Optional[str]:
        """Extract the actual answer from agent response"""
        # Remove common agent prefixes
        text = re.sub(r'^(?:Agent|Bot|Operator|AceBuddy|Acebuddy):\s*', '', text, flags=re.IGNORECASE)
        
        # Remove greetings
        greetings = [
            r'Hello.*?assist you[.!]?',
            r'Thank you for contacting.*?[.!]',
            r'My name is.*?[.!]',
            r'How are you.*?[.!]',
            r'Welcome to.*?[.!]',
        ]
        
        for greeting in greetings:
            text = re.sub(greeting, '', text, flags=re.IGNORECASE)
        
        # Look for actual solution/answer
        solution_patterns = [
            r'(?:please|kindly|you can|you need to|try to|follow these steps).*',
            r'(?:the issue is|the problem is|this is because).*',
            r'(?:to fix|to resolve|to solve).*',
            r'(?:i have|i\'ve|i will|i\'ll).*(?:check|fix|resolve|update).*',
        ]
        
        for pattern in solution_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                answer = match.group(0).strip()
                # Limit length
                if len(answer) > 300:
                    answer = answer[:300] + '...'
                return answer
        
        # If no pattern, take first few sentences
        sentences = re.split(r'[.!?]', text)
        meaningful = [s.strip() for s in sentences if len(s.strip()) > 20]
        if meaningful:
            answer = '. '.join(meaningful[:3])
            if len(answer) > 300:
                answer = answer[:300] + '...'
            return answer
        
        return None
    
    def process_existing_transcripts(self) -> List[Dict[str, Any]]:
        """Process existing chat transcripts and create clean training examples"""
        # Load existing transcripts
        transcripts_file = self.output_dir / "chat_transcripts.json"
        
        if not transcripts_file.exists():
            print("❌ No chat transcripts found. Run chat_transcript_processor.py first.")
            return []
        
        with open(transcripts_file, 'r', encoding='utf-8') as f:
            transcripts = json.load(f)
        
        print(f"Processing {len(transcripts)} conversations...")
        
        # Extract clean Q&A pairs
        all_qa_pairs = []
        for transcript in transcripts:
            qa_pairs = self.extract_qa_pairs(transcript)
            all_qa_pairs.extend(qa_pairs)
        
        # Filter and rank by quality
        quality_pairs = []
        for qa in all_qa_pairs:
            score = self._calculate_quality(qa)
            if score > 3.0:  # Minimum quality threshold
                qa['quality_score'] = score
                quality_pairs.append(qa)
        
        # Sort by quality
        quality_pairs.sort(key=lambda x: x['quality_score'], reverse=True)
        
        print(f"✅ Extracted {len(quality_pairs)} high-quality Q&A pairs")
        
        return quality_pairs
    
    def _calculate_quality(self, qa: Dict[str, Any]) -> float:
        """Calculate quality score for Q&A pair"""
        score = 0.0
        
        query = qa.get('query', '')
        response = qa.get('response', '')
        
        # Length checks
        if 20 <= len(query) <= 200:
            score += 2.0
        if 30 <= len(response) <= 300:
            score += 2.0
        
        # Resolved conversations are better
        if qa.get('resolved', False):
            score += 2.0
        
        # Check for solution keywords in response
        solution_keywords = ['fix', 'resolve', 'solution', 'try', 'follow', 'steps', 'check']
        if any(kw in response.lower() for kw in solution_keywords):
            score += 1.0
        
        # Check for question markers in query
        if '?' in query or any(word in query.lower() for word in ['how', 'what', 'why', 'can', 'error']):
            score += 1.0
        
        # Penalize if too much noise
        if query.count('|') > 2 or response.count('|') > 2:
            score -= 2.0
        
        return max(score, 0.0)
    
    def save_improved_training_examples(self, qa_pairs: List[Dict[str, Any]]):
        """Save improved training examples"""
        output_file = self.output_dir / "improved_training_examples.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved to {output_file}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("IMPROVED TRAINING EXAMPLES SUMMARY")
        print(f"{'='*60}")
        print(f"Total Q&A pairs: {len(qa_pairs)}")
        print(f"Avg quality score: {sum(qa['quality_score'] for qa in qa_pairs) / len(qa_pairs):.2f}")
        
        # Category breakdown
        categories = {}
        for qa in qa_pairs:
            cat = qa.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nBy Category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        
        # Show top 5 examples
        print(f"\n{'='*60}")
        print("TOP 5 EXAMPLES")
        print(f"{'='*60}")
        for i, qa in enumerate(qa_pairs[:5], 1):
            print(f"\n[{i}] Category: {qa['category']} | Quality: {qa['quality_score']:.1f}")
            print(f"Q: {qa['query']}")
            print(f"A: {qa['response']}")
            print("-" * 60)

if __name__ == "__main__":
    processor = ImprovedChatProcessor()
    qa_pairs = processor.process_existing_transcripts()
    
    if qa_pairs:
        processor.save_improved_training_examples(qa_pairs)
    else:
        print("\n❌ No quality Q&A pairs extracted.")
        print("This might mean:")
        print("1. Chat transcripts need better parsing")
        print("2. Conversations are too noisy/incomplete")
        print("3. Need to manually curate training examples")
