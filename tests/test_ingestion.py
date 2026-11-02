from pathlib import Path
from app.ingestion import ingest_file

def test_text_ingestion(tmp_path: Path):
    file_path = tmp_path / "policy.txt"
    file_path.write_text("Annual leave is 20 days.", encoding="utf-8")
    docs = ingest_file(file_path, chunk_size=100, chunk_overlap=10)
    assert docs
    assert "Annual leave" in docs[0].page_content
    assert docs[0].metadata["filename"] == "policy.txt"
