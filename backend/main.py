from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from services.files import listFiles
from services.extractContent import extractContent
from services.analyzeDocuments import analyzeDocuments

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_company(files: List[UploadFile]):
    try:
        files = listFiles()
        extractedContent = [{"name": file.filename, "content": extractContent(file)} for file in files]
        analysis = analyzeDocuments(extractedContent)
        return JSONResponse(content={"success": True, "text": analysis}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)
