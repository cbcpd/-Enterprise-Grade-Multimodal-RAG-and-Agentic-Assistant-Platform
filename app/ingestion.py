from pathlib import Path
from typing import Iterable
import csv
import io

import pandas as pd
from docx import Document
from PIL import Image
import pytesseract
from pypdf import PdfReader

from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

SUPPORTED = {".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt", ".md", ".png", ".jpg", ".jpeg"}

def _extract(path: Path) -> list[tuple[str, str]]:
    suffix = path.suffix.lower()
    output: list[tuple[str, str]] = []

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        for idx, page in enumerate(reader.pages, start=1):
            output.append((page.extract_text() or "", str(idx)))
    elif suffix == ".docx":
        doc = Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                text += "\n" + " | ".join(cell.text for cell in row.cells)
        output.append((text, "document"))
    elif suffix in {".xlsx", ".xls"}:
        workbook = pd.ExcelFile(path)
        for sheet in workbook.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet).fillna("")
            output.append((f"Sheet: {sheet}\n" + df.to_csv(index=False), sheet))
    elif suffix == ".csv":
        df = pd.read_csv(path).fillna("")
        output.append((df.to_csv(index=False), "CSV"))
    elif suffix in {".txt", ".md"}:
        output.append((path.read_text(encoding="utf-8", errors="replace"), "text"))
    elif suffix in {".png", ".jpg", ".jpeg"}:
        try:
            text = pytesseract.image_to_string(Image.open(path))
        except Exception as exc:
            raise RuntimeError(
                "Image OCR failed. Install Tesseract OCR and ensure it is on PATH. "
                f"Details: {exc}"
            ) from exc
        output.append((text, "image"))
    return output

def ingest_file(path: Path, chunk_size: int, chunk_overlap: int) -> list[LCDocument]:
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks: list[LCDocument] = []
    for text, page in _extract(path):
        if not text.strip():
            continue
        base = LCDocument(
            page_content=text,
            metadata={"filename": path.name, "page": page, "file_type": path.suffix.lower()}
        )
        chunks.extend(splitter.split_documents([base]))
    return chunks
