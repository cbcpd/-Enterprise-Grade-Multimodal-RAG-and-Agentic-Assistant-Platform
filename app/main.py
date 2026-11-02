from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.config import settings
from app.schemas import ChatRequest, ChatResponse, FeedbackRequest
from app.ingestion import ingest_file
from app.vectorstore import add_documents
from app.graph import ask
from app.feedback import save_feedback

app = FastAPI(
    title="Enterprise Multimodal RAG & Agentic Assistant",
    version="1.0.0",
    description="Multi-format document ingestion and evidence-grounded RAG API."
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "enterprise-multimodal-rag"}

@app.post("/documents/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if not suffix:
            raise HTTPException(400, "Uploaded file must have an extension.")
        safe_name = f"{uuid4().hex}_{Path(upload.filename).name}"
        destination = upload_dir / safe_name
        content = await upload.read()
        if len(content) > settings.max_file_mb * 1024 * 1024:
            raise HTTPException(413, f"{upload.filename} exceeds the file-size limit.")
        destination.write_bytes(content)
        try:
            docs = ingest_file(destination, settings.chunk_size, settings.chunk_overlap)
            add_documents(docs)
            results.append({"filename": upload.filename, "chunks_indexed": len(docs)})
        except Exception as exc:
            destination.unlink(missing_ok=True)
            raise HTTPException(400, f"Could not process {upload.filename}: {exc}") from exc
    return {"uploaded": results}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = ask(request.question, request.top_k)
        docs = result.get("documents", [])
        sources = []
        seen = set()
        for doc in docs:
            key = (doc.metadata.get("filename"), doc.metadata.get("page"))
            if key not in seen:
                seen.add(key)
                sources.append({
                    "filename": key[0] or "unknown",
                    "page": key[1],
                    "chunk_id": None
                })
        return ChatResponse(
            answer=result.get("answer", "No answer generated."),
            sources=sources,
            retrieved_chunks=len(docs),
        )
    except Exception as exc:
        raise HTTPException(500, f"Query failed: {exc}") from exc

@app.post("/feedback")
def feedback(request: FeedbackRequest):
    save_feedback(request.model_dump())
    return {"status": "saved"}
