# AceBuddy RAG Chatbot

High-level RAG-based chatbot for ACE Cloud support, designed to replace the current Zobot and significantly improve automation rates.

## 🎯 Goals

- **Current**: 800-900 monthly chats, ~100 resolved by Zobot (11% automation)
- **Target**: 40-60% automation rate with intelligent RAG system
- **Integration**: Zoho SalesIQ webhook for seamless deployment

## 🏗️ Architecture

```
User Query → Zoho SalesIQ → Webhook → FastAPI Backend
                                          ↓
                                    RAG Engine
                                    ↙        ↘
                            Vector Store    OpenAI GPT-4
                            (ChromaDB)      (Generation)
                                    ↘        ↙
                                    Response
                                          ↓
                                    Zoho SalesIQ → User
```

## 📋 Features

- **Semantic Search**: ChromaDB vector store with OpenAI embeddings
- **Context-Aware**: Maintains conversation history
- **Smart Escalation**: Automatically escalates complex queries to human agents
- **Multi-Source**: 93 PDF SOPs + 10 KB articles = comprehensive knowledge base
- **Category-Based**: QuickBooks, RDP, Email, Server, User Management
- **Webhook Ready**: Direct integration with Zoho SalesIQ

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env with your API keys
notepad .env
```

### 2. Data Processing (Phase 1)

```bash
# Step 1: Extract and clean PDFs
python src/data_processor.py

# Step 2: Create semantic chunks
python src/chunker.py

# Step 3: Build vector database
python src/vector_store.py
```

### 3. Test RAG Engine

```bash
# Test retrieval and generation
python src/rag_engine.py
```

### 4. Start API Server

```bash
# Development
python src/api.py

# Production
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## 📊 Data Processing Pipeline

### Phase 1: PDF Extraction & Cleaning

```bash
python src/data_processor.py
```

**Output**: `data/processed/all_documents_cleaned.json`

- Extracts text from 93 PDF files
- Cleans OCR errors and formatting issues
- Categorizes by topic (QuickBooks, RDP, Email, etc.)
- Generates processing report

### Phase 2: Semantic Chunking

```bash
python src/chunker.py
```

**Output**: `data/processed/final_chunks.json`

- Creates 500-char chunks with 50-char overlap
- Preserves semantic boundaries (sections, steps)
- Maintains metadata for each chunk
- Optimized for RAG retrieval

### Phase 3: Vector Database

```bash
python src/vector_store.py
```

**Output**: `data/chroma/` (persistent vector DB)

- Generates OpenAI embeddings
- Stores in ChromaDB with cosine similarity
- Enables fast semantic search

## 🔌 API Endpoints

### Chat Endpoint

```bash
POST /chat
Content-Type: application/json

{
  "query": "I forgot my password",
  "session_id": "optional_session_id",
  "user_id": "optional_user_id"
}
```

**Response**:
```json
{
  "response": "To reset your password, follow these steps...",
  "session_id": "session_123",
  "escalate": false,
  "confidence": "high",
  "sources": [
    {
      "id": "01_password_reset_chunk_0",
      "category": "User Management",
      "relevance": 0.92
    }
  ],
  "timestamp": "2025-11-26T10:30:00"
}
```

### Zoho Webhook

```bash
POST /webhook/zoho
X-Zoho-Signature: <signature>

{
  "visitor_id": "12345",
  "chat_id": "chat_67890",
  "message": "How do I connect to RDP?",
  "visitor_name": "John Doe",
  "visitor_email": "john@example.com"
}
```

### Health Check

```bash
GET /health
```

## 🔧 Configuration

Edit `.env` file:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# RAG Settings
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
TEMPERATURE=0.3

# Zoho Integration
ZOHO_WEBHOOK_SECRET=your_secret
```

## 📈 Performance Metrics

### Expected Improvements

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Automation Rate | 11% | 40-60% |
| Avg Response Time | 5-10 min | <30 sec |
| Agent Workload | 700-800 chats | 300-500 chats |
| Resolution Accuracy | Variable | 85%+ |

### Monitoring

```bash
# Get current stats
curl http://localhost:8000/stats

# Check health
curl http://localhost:8000/health
```

## 🧪 Testing

```bash
# Test data processing
python src/data_processor.py

# Test chunking
python src/chunker.py

# Test RAG engine
python src/rag_engine.py

# Test API
python -m pytest tests/
```

## 🔐 Security

- Webhook signature verification
- API key authentication
- Rate limiting (configure in production)
- Input sanitization
- Session management

## 📝 Zoho SalesIQ Integration

### Setup Steps

1. **Create Webhook in Zoho SalesIQ**:
   - Go to Settings → Developers → Webhooks
   - Add new webhook: `https://your-domain.com/webhook/zoho`
   - Select trigger: "On visitor message"
   - Copy webhook secret to `.env`

2. **Configure Bot Response**:
   - Create bot flow in Zoho
   - Add webhook action
   - Map response to chat

3. **Test Integration**:
   - Send test message in SalesIQ
   - Verify webhook receives request
   - Check bot responds correctly

## 🛠️ Troubleshooting

### PDF Extraction Issues
```bash
# If PDFs fail to extract
pip install --upgrade pypdf2 pdfplumber pymupdf
```

### Vector Store Issues
```bash
# Clear and rebuild
rm -rf data/chroma
python src/vector_store.py
```

### API Connection Issues
```bash
# Check if port is available
netstat -ano | findstr :8000

# Use different port
uvicorn src.api:app --port 8001
```

## 📚 Knowledge Base Categories

- **QuickBooks**: Errors, setup, integrations, payroll
- **Remote Desktop**: Connection issues, configuration, performance
- **Email**: Outlook setup, Office 365, authentication
- **Server**: Performance, storage, maintenance
- **User Management**: Onboarding, offboarding, permissions
- **General**: Passwords, monitors, printers

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
# Coming soon
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=...

# Run with gunicorn
gunicorn src.api:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📊 Next Steps

1. ✅ **Phase 1**: Data processing (current)
2. **Phase 2**: RAG system testing
3. **Phase 3**: Zoho integration
4. **Phase 4**: Production deployment
5. **Phase 5**: Monitoring & optimization

## 🤝 Support

For issues or questions:
- Check logs: `logs/acebuddy.log`
- Review API docs: `http://localhost:8000/docs`
- Contact: support@acebuddy.com

## 📄 License

Proprietary - ACE Cloud Services
