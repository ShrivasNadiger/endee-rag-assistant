# RAG Application with Endee Vector Database

A production-ready Retrieval Augmented Generation (RAG) web application demonstrating the power of **Endee** as a high-performance vector database.

## 🎯 Overview

This application allows users to:
- Upload PDF and Word documents
- Automatically chunk and embed documents using OpenAI
- Store embeddings in Endee vector database
- Query documents using natural language
- Receive AI-generated answers with inline citations
- View retrieval performance metrics highlighting Endee's speed

## 🏗️ Architecture

### Backend (Python FastAPI)
- **FastAPI** - REST API framework
- **Endee Python SDK** - Vector database operations
- **OpenAI API** - Embeddings and text generation
- **PyPDF2 & python-docx** - Document parsing

### Frontend (React + Tailwind CSS)
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling with custom dark theme
- **Axios** - HTTP client

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Docker (for Endee)
- OpenAI API key

## 🚀 Quick Start

### 1. Start Endee Vector Database

Endee should already be running at `http://localhost:8080` via Docker.

If not, start it using:
```bash
cd docker
docker-compose up -d
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here

# Start backend server
python main.py
```

Backend will run at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at `http://localhost:3000`

## 📖 Usage

1. **Upload Documents**
   - Drag and drop PDF or DOCX files into the upload area
   - Click "Upload & Process" to ingest documents
   - Documents are chunked, embedded, and stored in Endee

2. **Ask Questions**
   - Type your question in the chat input
   - The system retrieves relevant chunks from Endee
   - AI generates an answer with inline citations
   - View retrieval latency metrics

3. **View Retrieved Chunks**
   - The metadata panel shows which chunks were retrieved
   - See source document, page/paragraph numbers
   - View similarity scores and chunk IDs

## 🔧 Configuration

Edit `backend/.env` to customize:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo-preview

# Endee Configuration
ENDEE_BASE_URL=http://localhost:8080/api/v1
ENDEE_INDEX_NAME=rag_documents

# Chunking Configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

## 📊 API Endpoints

### POST /ingest
Upload and process documents
```bash
curl -X POST http://localhost:8000/ingest \
  -F "files=@document.pdf"
```

### POST /query
Query the RAG system
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "top_k": 5}'
```

### GET /stats
Get system statistics
```bash
curl http://localhost:8000/stats
```

## 🎨 Features

### Endee Integration
- ✅ Native Python SDK usage
- ✅ Vector upsert with metadata
- ✅ Similarity search with filters
- ✅ Latency tracking for performance metrics
- ✅ Cosine similarity distance metric

### RAG Pipeline
- ✅ Multi-format document support (PDF, DOCX)
- ✅ Intelligent text chunking with overlap
- ✅ OpenAI embeddings (text-embedding-3-small)
- ✅ Context-aware answer generation
- ✅ Automatic citation formatting

### UI/UX
- ✅ Modern dark theme with glassmorphism
- ✅ Drag-and-drop file upload
- ✅ Real-time chat interface
- ✅ Inline citations in answers
- ✅ Performance metrics display
- ✅ Responsive layout

## 🔍 How It Works

1. **Document Ingestion**
   ```
   Upload → Parse → Chunk → Embed → Store in Endee
   ```

2. **Query Processing**
   ```
   Query → Embed → Search Endee → Retrieve Chunks → Generate Answer → Add Citations
   ```

3. **Endee Operations**
   - Index creation with dimension matching embedding size
   - Vector upsert with metadata (document name, page, chunk index)
   - Similarity search with configurable top_k and ef parameters
   - Latency measurement for performance tracking

## 📁 Project Structure

```
endee-rag-assistant/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── endee_client.py      # Endee SDK wrapper
│   ├── ingest.py            # Ingestion pipeline
│   ├── retriever.py         # Vector retrieval
│   ├── rag_pipeline.py      # RAG answer generation
│   ├── utils/
│   │   ├── pdf_loader.py    # PDF text extraction
│   │   ├── docx_loader.py   # DOCX text extraction
│   │   └── chunker.py       # Text chunking
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── MetadataPanel.jsx
│   │   │   └── ChatPanel.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── index.css
│   ├── package.json
│   └── tailwind.config.js
└── docker/
    └── docker-compose.yml
```

## 🐛 Troubleshooting

**Endee connection failed**
- Ensure Endee is running: `docker ps`
- Check URL in `.env` matches Endee port

**OpenAI API errors**
- Verify API key in `.env`
- Check API quota and billing

**Upload fails**
- Ensure file is PDF or DOCX
- Check file size (large files may timeout)

## 📝 License

MIT

## 🙏 Acknowledgments

- **Endee** - High-performance vector database
- **OpenAI** - Embeddings and language models
- **FastAPI** - Modern Python web framework
- **React** - UI library
