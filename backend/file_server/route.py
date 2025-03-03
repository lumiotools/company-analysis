from fastapi import APIRouter, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import aiofiles
import asyncio
from typing import List, Optional, Dict, Any

router = APIRouter()

UPLOAD_DIR = "uploads"  # Root directory for storing uploaded files

# 🚀 API: Upload Files & Folders (Preserving Structure)
@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    file_paths: List[str] = Form(...)
):
    """
    Uploads files while maintaining folder structure.
    - `files`: List of uploaded files.
    - `file_paths`: Corresponding relative paths for each file.
    """

    tasks = []
    for file, relative_path in zip(files, file_paths):
        # Ensure safe relative path
        relative_path = relative_path.replace("\\", "/").lstrip("/")
        destination = os.path.join(UPLOAD_DIR, relative_path)

        # Create nested folders
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        # Save file asynchronously
        tasks.append(save_file(file, destination))

    await asyncio.gather(*tasks)

    return {"message": "Upload successful", "root_path": UPLOAD_DIR}

async def save_file(file: UploadFile, file_location: str):
    """Save an uploaded file asynchronously."""
    async with aiofiles.open(file_location, "wb") as f:
        while chunk := await file.read(1024):
            await f.write(chunk)

# 🚀 API: Get Files & Folders (Nested Structure)
@router.get("/files")
def list_files(folder: str = "") -> Dict[str, Any]:
    """
    List all files and folders inside the given directory.
    - `folder`: Path relative to the root `uploads/` folder.
    """
    base_path = os.path.join(UPLOAD_DIR, folder)
    
    if not os.path.exists(base_path):
        return JSONResponse(status_code=404, content={"error": "Folder not found"})

    def scan_directory(directory: str):
        """ Recursively scan a directory and return a tree structure """
        tree = {"name": os.path.basename(directory), "type": "folder", "children": []}

        try:
            for entry in os.scandir(directory):
                if entry.is_dir():
                    tree["children"].append(scan_directory(entry.path))
                else:
                    tree["children"].append({"name": entry.name, "type": "file"})
        except PermissionError:
            return {"error": "Permission denied"}

        return tree

    return scan_directory(base_path)

# 🚀 API: Delete Files or Folders
@router.delete("/delete")
def delete_file_or_folder(path: str):
    """
    Delete a file or folder recursively.
    - `path`: Relative path from `uploads/` directory.
    """
    full_path = os.path.join(UPLOAD_DIR, path)

    if os.path.exists(full_path):
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return {"message": f"Deleted {path}"}
    
    return JSONResponse(status_code=404, content={"error": "File or folder not found"})
