# Chat Transcript Processing Guide

## 📁 Data Structure

Your chat data is organized as follows:

```
data/
├── Chat Transcripts/              ← REAL CHAT CONVERSATIONS (PDFs)
│   ├── 60000687661_JAN_1/        ← January chats
│   │   ├── 60000687661_JAN_0_50.pdf
│   │   ├── 60000687661_JAN_50_100.pdf
│   │   └── ... (28 PDF files)
│   ├── 60000687661_FEB_1/        ← February chats
│   ├── 60000687661_MAR_1/        ← March chats
│   ├── 60000687661_APR_1/        ← April chats
│   ├── 60000687661_MAY_1/        ← May chats
│   ├── 60000687661_JUN_1/        ← June chats
│   ├── 60000687661_JUL_1/        ← July chats
│   ├── 60000687661_AUG_1/        ← August chats
│   ├── 60000687661_SEP_1/        ← September chats
│   ├── 60000687661_OCT_1/        ← October chats
│   └── 60000687661_NOV_1/        ← November chats
│
└── Ticket Data/                   ← METADATA (Excel files)
    ├── 1jan-24jan.xlsx           ← Ticket metadata
    ├── 1feb-26feb.xlsx           ← (timing, visitor ID, etc.)
    └── ... (16 Excel files)
```

## 🎯 What Gets Processed

### ✅ Chat Transcripts (PDFs)
**Location**: `data/Chat Transcripts/`
**Format**: PDF files with actual conversations
**Content**: 
- Visitor messages (user queries)
- Agent/Bot responses
- Full conversation flow
- Resolution status

**What We Extract**:
- User queries and language patterns
- Successful agent responses
- Resolution patterns
- Common issues
- User terminology

### ⚠️ Ticket Data (Excel)
**Location**: `data/Ticket Data/`
**Format**: Excel files (.xlsx)
**Content**: 
- Metadata (timing, visitor ID, session data)
- NOT actual conversations

**Usage**: 
- Currently NOT processed for training
- Can be used for analytics (optional)
- Contains timing and visitor statistics

## 🔄 Processing Flow

### Step 1: Load PDF Transcripts
```python
# Scans all monthly folders
# Loads all PDF files
# Extracts text from each PDF
```

### Step 2: Parse Conversations
```python
# Identifies conversation boundaries
# Extracts visitor messages
# Extracts agent responses
# Determines resolution status
```

### Step 3: Create Training Examples
```python
# Filters for quality conversations
# Pairs queries with responses
# Categorizes by topic
# Calculates quality scores
```

### Step 4: Generate Insights
```python
# Analyzes common patterns
# Identifies top keywords
# Categorizes issues
# Creates training dataset
```

## 📊 Expected Output

### From 11 Months of PDFs

**Estimated Volume**:
- ~11 monthly folders
- ~28 PDFs per month (batches of 50 chats)
- ~50 conversations per PDF
- **Total: ~15,000+ conversations**

**Quality Filtering**:
- Extract all conversations: ~15,000
- Filter for quality: ~5,000-8,000
- High-quality training examples: ~1,000-2,000

### Training Examples Format

```json
{
  "query": "I forgot my password and can't login to the server",
  "response": "I can help you reset your password. I'll need your username, Customer ID, and registered email address...",
  "category": "Password/Login",
  "month": "JAN",
  "source": "60000687661_JAN_0_50.pdf",
  "resolved": true,
  "quality_score": 8.5
}
```

## 🎓 What the Chatbot Learns

### 1. User Language Patterns
- How users actually phrase questions
- Common abbreviations and slang
- Emotional context (frustrated, urgent)
- Follow-up question patterns

**Example**:
- User says: "cant get in forgot pw"
- Learns: This means "password reset request"

### 2. Successful Response Patterns
- What responses led to resolution
- Effective troubleshooting steps
- Appropriate escalation timing
- Helpful clarifying questions

**Example**:
- Successful pattern: Ask for CID → Verify email → Send reset link
- Learns: This sequence works for password resets

### 3. Category Recognition
- QuickBooks issues
- RDP connection problems
- Email/Outlook issues
- Server performance
- User management
- Password resets

### 4. Escalation Triggers
- When conversations weren't resolved
- What issues require human agents
- Complexity indicators
- Urgency markers

## 🔧 Configuration

### Adjust Conversation Parsing

In `src/chat_transcript_processor.py`:

```python
# Modify conversation patterns based on your PDF format
conversation_patterns = [
    r'(?:Conversation|Chat)\s*#?\d+',
    r'={3,}',
    r'-{3,}',
    r'Visitor\s+ID:',
    r'Chat\s+started',
]
```

### Adjust Quality Criteria

```python
# Minimum response length
if len(response) > 30:  # Adjust threshold

# Quality score weights
score += min(response_len / 100, 5.0)  # Response length
score += 3.0 if resolved else 0.0      # Resolution bonus
```

### Adjust Category Mapping

```python
def _categorize_query(self, query: str) -> str:
    # Add your custom categories
    if 'your_keyword' in query_lower:
        return "Your Category"
```

## 🚀 Running the Processor

### Command
```bash
python run_pipeline.py
```

### What Happens
```
[STEP 2/4] Processing chat transcripts...
LOADING CHAT TRANSCRIPTS FROM 11 MONTHS

Processing JAN (28 PDF files)... ✅ 1,247 conversations
Processing FEB (25 PDF files)... ✅ 1,156 conversations
Processing MAR (27 PDF files)... ✅ 1,298 conversations
...

✅ Processed 14,523 conversations
   Training examples: 1,847
   Categories: 9
   Top keywords: password(1,234), quickbooks(987), rdp(856)
```

## 📈 Quality Metrics

### Conversation Quality Score

**Components**:
1. **Response Length** (0-5 points)
   - Longer, detailed responses score higher
   - Max 5 points for 500+ char responses

2. **Resolution Status** (0-3 points)
   - +3 points if marked as resolved
   - Indicates successful outcome

3. **Engagement** (0-5 points)
   - Back-and-forth conversation
   - Multiple visitor/agent exchanges
   - Shows active problem-solving

4. **Query Quality** (-2 to 0 points)
   - Penalty for very short queries
   - Ensures meaningful questions

**Total Score**: 0-13 points

### Training Example Selection

- **High Quality** (Score 8+): Used for primary training
- **Medium Quality** (Score 5-7): Used for supplementary training
- **Low Quality** (Score <5): Excluded from training

## 🐛 Troubleshooting

### Issue: Few Conversations Extracted

**Symptom**: "✅ Processed 45 conversations" (expected 15,000+)

**Causes**:
1. PDF format doesn't match parsing patterns
2. Conversations not properly delimited
3. Text extraction failing

**Solutions**:
1. Check one PDF manually to see format
2. Adjust `conversation_patterns` in code
3. Modify `_extract_conversation_data()` parsing logic

### Issue: Low Quality Training Examples

**Symptom**: "Training examples: 23" (expected 1,000+)

**Causes**:
1. Quality criteria too strict
2. Conversations too short
3. Resolution markers not detected

**Solutions**:
1. Lower quality thresholds
2. Adjust minimum response length
3. Add more resolution keywords

### Issue: Wrong Categories

**Symptom**: Most conversations categorized as "Other"

**Solutions**:
1. Review `_categorize_query()` method
2. Add more category keywords
3. Check for typos in keywords

## 📊 Validation

### Check Extracted Data

```python
# After processing, check output files
import json

# Load training examples
with open('data/processed/training_examples.json', 'r') as f:
    examples = json.load(f)

# Review first few examples
for ex in examples[:5]:
    print(f"Query: {ex['query']}")
    print(f"Response: {ex['response'][:100]}...")
    print(f"Category: {ex['category']}")
    print(f"Quality: {ex['quality_score']}")
    print("-" * 50)
```

### Check Analysis

```python
# Load analysis
with open('data/processed/chat_analysis.json', 'r') as f:
    analysis = json.load(f)

# Review statistics
print(f"Total conversations: {analysis['total_conversations']}")
print(f"Categories: {analysis['categories']}")
print(f"Top keywords: {analysis['top_keywords'][:10]}")
```

## ✅ Success Criteria

Your chat transcript processing is successful when:

- ✅ Processes 10,000+ conversations from PDFs
- ✅ Extracts 1,000+ high-quality training examples
- ✅ Identifies 8-10 main categories
- ✅ Captures user language patterns
- ✅ Includes successful resolution examples
- ✅ Quality scores are distributed (not all low/high)

## 🎯 Next Steps

1. **Run the pipeline**:
   ```bash
   python run_pipeline.py
   ```

2. **Review output**:
   - Check `data/processed/chat_transcripts.json`
   - Review `data/processed/training_examples.json`
   - Analyze `data/processed/chat_analysis.json`

3. **Validate quality**:
   - Read sample training examples
   - Verify categories make sense
   - Check quality scores distribution

4. **Adjust if needed**:
   - Modify parsing patterns
   - Adjust quality criteria
   - Update category keywords

5. **Test chatbot**:
   ```bash
   python test_chatbot.py
   ```
   - Try queries in user language
   - Verify responses match training data
   - Check if it learned patterns

## 💡 Pro Tips

1. **First Run**: Takes 10-20 minutes to process all PDFs
2. **Cached**: Subsequent runs are faster (results cached)
3. **Incremental**: Add new months as they come
4. **Quality Over Quantity**: 1,000 good examples > 10,000 poor ones
5. **Review Samples**: Always check a few examples manually

---

**Your chatbot will now learn from real conversations!** 🚀
