"""
File extraction utilities.  This module implements functions to extract text from
uploaded files of different types.  Extraction is asynchronous where possible to
avoid blocking the event loop.  Image OCR is stubbed out for future
implementation.
"""
import asyncio
import csv
import io
import mimetypes
import os
from typing import List, Dict, Optional

import pdfplumber
import pandas as pd
from docx import Document


async def extract_text_from_files(files: Optional[List[Dict[str, str]]]) -> str:
    """
    Concatenate the extracted text from a list of files.  Each file dict must
    include the path to the stored file and optionally the MIME type.  The
    returned string contains a newline between files.
    """
    if not files:
        return ""
    tasks = [extract_text_from_file(f["path"], f.get("content_type")) for f in files]
    texts = await asyncio.gather(*tasks)
    return "\n\n".join(texts)


async def extract_text_from_file(path: str, content_type: Optional[str] = None) -> str:
    """
    Extract text from a single file based on its MIME type or extension.
    """
    if content_type is None:
        content_type, _ = mimetypes.guess_type(path)
    extension = os.path.splitext(path)[1].lower()
    if content_type == "application/pdf" or extension == ".pdf":
        return await extract_pdf_text(path)
    elif content_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword") or extension == ".docx":
        return await extract_docx_text(path)
    elif content_type == "text/plain" or extension in (".txt", ".log"):
        return await extract_txt_text(path)
    elif content_type == "text/csv" or extension == ".csv":
        return await extract_csv_text(path)
    elif content_type and content_type.startswith("image/") or extension in (".png", ".jpg", ".jpeg", ".bmp"):
        return await extract_image_text(path)
    else:
        return ""


async def extract_pdf_text(path: str) -> str:
    def _extract() -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"
        return text
    return await asyncio.to_thread(_extract)


async def extract_docx_text(path: str) -> str:
    def _extract() -> str:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    return await asyncio.to_thread(_extract)


async def extract_txt_text(path: str) -> str:
    def _extract() -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return await asyncio.to_thread(_extract)


async def extract_csv_text(path: str) -> str:
    def _extract() -> str:
        df = pd.read_csv(path)
        return df.to_csv(index=False)
    return await asyncio.to_thread(_extract)


async def extract_image_text(path: str) -> str:
    """
    OCR extraction stub.  For production use, integrate pytesseract or another OCR
    library.  Here we return an empty string.
    """
    # Placeholder: implement OCR with pytesseract or similar
    return ""