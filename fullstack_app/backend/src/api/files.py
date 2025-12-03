"""
File upload API.  Handles receiving user files, validating MIME types, and
storing them on disk.  Returns metadata needed by the agent pipeline.  Also
exposes an endpoint to list supported file types for tooltips on the client.
"""
import os
import shutil
from typing import List

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

SUPPORTED_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/csv": ".csv",
    "image/png": ".png",
    "image/jpeg": ".jpg",
}

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploaded_files"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/types")
async def get_supported_types():
    """Return supported file types for client-side tooltips."""
    return JSONResponse({"supported_types": list(SUPPORTED_TYPES.keys())})


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload one or more files.  Unsupported file types are rejected.  The files
    are stored in the server's upload directory and returned with metadata.
    """
    metadata = []
    for file in files:
        if file.content_type not in SUPPORTED_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
        # Save file to disk
        file_ext = SUPPORTED_TYPES[file.content_type]
        file_name = file.filename or f"upload{file_ext}"
        dest_path = os.path.join(UPLOAD_DIR, file_name)
        # Avoid collisions
        base, ext = os.path.splitext(dest_path)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = f"{base}_{counter}{ext}"
            counter += 1
        with open(dest_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
        metadata.append({"filename": file_name, "path": dest_path, "content_type": file.content_type})
    return JSONResponse({"files": metadata})