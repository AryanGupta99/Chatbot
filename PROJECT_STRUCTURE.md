# AceBuddy RAG Chatbot - Project Structure

```
acebuddy-rag-chatbot/
│
├── 📄 README.md                          # Main documentation
├── 📄 IMPLEMENTATION_PLAN.md             # Detailed implementation guide
├── 📄 PROJECT_STRUCTURE.md               # This file
├── 📄 requirements.txt                   # Python dependencies
├── 📄 .env.example                       # Environment template
├── 📄 .env                               # Your config (create this)
├── 📄 .gitignore                         # Git ignore rules
├── 📄 config.py                          # Configuration management
│
├── 🚀 run_pipeline.py                    # Main data processing pipeline
├── 🧪 test_chatbot.py                    # Interactive testing
│
├── 📁 src/                               # Source code
│   ├── __init__.py
│   ├── data_processor.py                 # PDF extraction & cleaning
│   ├── chunker.py                        # Semantic chunking
│   ├── vector_store.py                   # ChromaDB vector database
│   ├── rag_engine.py                     # Core RAG logic
│   └── api.py                            # FastAPI server
│
└── 📁 data/                              # Data directory
    ├── 📁 SOP and KB Docs/               # 93 PDF files (input)
    ├── 📁 kb/                            # 10 markdown KB articles
    ├── 📁 processed/                     # Processed data (output)
    │   ├── all_documents_cleaned.json    # Cleaned documents
    │   ├── final_chunks.json             # Semantic chunks
    │   ├── processing_report.json        # Processing stats
    │   └── chunk_statistics.json         # Chunk stats
    └── 📁 chroma/                        # Vector database (output)
        └── [ChromaDB files]
```

## 🔄 Data Flow

```
PDFs (93 files)
    ↓
[data_processor.py] → Extract & Clean
    ↓
all_documents_cleaned.json
    ↓
[chunker.py] → Semantic Chunking
    ↓
final_chunks.json
    ↓
[vector_store.py] → Generate Embeddings
    ↓
ChromaDB Vector Database
    ↓
[rag_engine.py] → Query Processing
    ↓
[api.py] → REST API
    ↓
Zoho SalesIQ Webhook
```

## 📦 Key Components

### 1. Data Processing (`src/data_processor.py`)
- Extracts text from PDFs using multiple methods
- Cleans OCR errors and formatting
- Categorizes by topic
- Outputs: `all_documents_cleaned.json`

### 2. Semantic Chunking (`src/chunker.py`)
- Creates 500-char chunks with 50-char overlap
- Preserves semantic boundaries
- Maintains metadata
- Outputs: `final_chunks.json`

### 3. Vector Store (`src/vector_store.py`)
- Generates OpenAI embeddings
- Stores in ChromaDB
- Enables semantic search
- Outputs: `data/chroma/` directory

### 4. RAG Engine (`src/rag_engine.py`)
- Retrieves relevant context
- Generates responses with OpenAI
- Handles escalation logic
- Maintains conversation history

### 5. API Server (`src/api.py`)
- FastAPI REST endpoints
- Zoho webhook integration
- Session management
- Health checks and monitoring

## 🎯 Entry Points

### For Development
```bash
# Process all data
python run_pipeline.py

# Test chatbot interactively
python test_chatbot.py

# Test with predefined cases
python test_chatbot.py auto

# Start API server
python src/api.py
```

### For Production
```bash
# Start API with gunicorn
gunicorn src.api:app -w 4 -k uvicorn.workers.UvicornWorker

# Or with uvicorn directly
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## 📊 Data Files

### Input Files
- `data/SOP and KB Docs/*.pdf` - 93 PDF documents
- `data/kb/*.md` - 10 markdown KB articles

### Output Files
- `data/processed/all_documents_cleaned.json` - ~93 documents
- `data/processed/final_chunks.json` - ~1000-1500 chunks
- `data/chroma/` - Vector database with embeddings

### Configuration Files
- `.env` - Environment variables (API keys, settings)
- `config.py` - Configuration management

## 🔌 API Endpoints

```
GET  /                    - Health check
GET  /health              - Detailed health status
POST /chat                - Main chat endpoint
POST /webhook/zoho        - Zoho SalesIQ webhook
POST /session/clear       - Clear conversation session
GET  /stats               - API statistics
```

## 🧪 Testing

```bash
# Interactive testing
python test_chatbot.py

# Automated test suite
python test_chatbot.py auto

# API testing
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "I forgot my password"}'
```

## 📈 Monitoring

### Logs
- Console output during development
- Production: Configure logging in `src/api.py`

### Metrics
- `/stats` endpoint - Active sessions, vector store stats
- `/health` endpoint - System health check
- OpenAI dashboard - Token usage and costs

## 🔐 Security

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key (required)
- `API_SECRET_KEY` - API authentication (recommended)
- `ZOHO_WEBHOOK_SECRET` - Webhook signature verification

### Best Practices
- Never commit `.env` file
- Use webhook signature verification
- Implement rate limiting in production
- Monitor API usage and costs

## 🚀 Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure `.env` with API keys
- [ ] Run data pipeline: `python run_pipeline.py`
- [ ] Test chatbot: `python test_chatbot.py auto`
- [ ] Start API: `python src/api.py`
- [ ] Test API endpoints
- [ ] Deploy to production server
- [ ] Configure Zoho webhook
- [ ] Monitor performance
- [ ] Collect feedback and iterate

## 📞 Support

For questions or issues:
1. Check README.md for documentation
2. Review IMPLEMENTATION_PLAN.md for detailed steps
3. Check API docs: http://localhost:8000/docs
4. Review logs and error messages
