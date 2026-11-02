# Enterprise Multimodal RAG & Agentic Assistant

A portfolio-ready starter platform for ingesting corporate PDFs, images, spreadsheets, Word documents and text; indexing extracted content; and answering questions with citations using retrieval-augmented generation.

## Architecture

```text
PDF / DOCX / XLSX / CSV / TXT / PNG / JPG
                  |
             FastAPI upload
                  |
       Extract + normalize content
                  |
        Chunk + embedding model
                  |
          Chroma vector store
                  |
             User question
                  |
      LangGraph retrieve → answer
                  |
       Grounded answer + sources
```

## Features
- Multi-format ingestion: PDF, DOCX, XLSX, CSV, TXT, Markdown, PNG and JPEG.
- OCR for images and scanned PDFs (Tesseract must be installed).
- Chunking with overlap and metadata preservation.
- ChromaDB vector storage with sentence-transformer embeddings.
- LangGraph workflow for retrieval, evidence sufficiency check and answer generation.
- FastAPI endpoints for upload, query and health checks.
- Source filenames and page/sheet metadata returned with answers.
- Basic feedback endpoint for collecting user ratings.

## Quick start

### 1. Requirements
- Python 3.10 or 3.11
- Tesseract OCR installed and available on PATH (optional, needed for image OCR)
- An OpenAI API key for answer generation

### 2. Install

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Add `OPENAI_API_KEY` to `.env`.

### 3. Run API

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API documentation.

### 4. Ingest documents

Use the Swagger UI `POST /documents/upload` endpoint, or:

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload" \
  -F "files=@./sample_docs/employee_handbook.pdf"
```

### 5. Ask a question

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the annual leave policy?","top_k":5}'
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service status |
| POST | `/documents/upload` | Ingest one or more supported files |
| POST | `/chat` | Ask a question over indexed documents |
| POST | `/feedback` | Store a thumbs-up/down rating |

## Configuration

See `.env.example`. The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`; the first run downloads it. Chroma data is stored in `./chroma_db`.

## Project structure

```text
app/
  main.py             FastAPI routes
  config.py           Environment settings
  ingestion.py        Multi-format extraction and chunking
  vectorstore.py      Chroma persistence and retrieval
  graph.py            LangGraph retrieval/answer workflow
  schemas.py          Request/response models
  feedback.py         JSONL feedback collection
```

## Notes on reliability and security

- The assistant is instructed to answer only from retrieved evidence and to say when evidence is insufficient. This reduces unsupported answers but does not mathematically guarantee hallucination-free output.
- Validate and scan uploaded files before production use. Add authentication, authorization, tenant-level isolation, rate limits, file-size limits, malware scanning and audit logging before exposing the API publicly.
- Do not upload confidential corporate data to third-party model providers unless your organization's policies permit it.
- For production, consider object storage, a managed vector database, background ingestion workers, observability, evaluation datasets and hybrid BM25 + vector retrieval.
- OCR requires the Tesseract executable. If it is missing, image extraction returns a helpful error.

## Example resume description

**Enterprise-Grade Multimodal RAG and Agentic Assistant Platform**  
Built a FastAPI-based document intelligence platform that ingests PDF, image, spreadsheet and text files; extracts and chunks content; indexes embeddings in ChromaDB; and uses a LangGraph retrieval workflow to generate evidence-grounded answers with source metadata. Added feedback collection and configurable retrieval settings.

Only claim performance metrics after measuring them on a documented evaluation set.
