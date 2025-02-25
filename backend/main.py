from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from services.files import download_files, find_alpine_vc_files, listFiles
from services.extractContent import extractContent
from services.analyzeDocuments import analyzeDocuments
import os
import tempfile
import requests
from prompts import system_prompt, system_prompt_doc, system_prompt_excel
from services.saveExcel import save_to_excel
from services.saveDoc import save_doc_to_docx

UPLOAD_DIR = "temp_uploads"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_company():
    try:
        # Get the list of files from the server
        files = listFiles()  # Get the list of all files
        # print("files",files)
        alpine_vc_file_urls = find_alpine_vc_files(files)  # Find files under 'Alpine VC'

        print("Alpine VC files to download:", alpine_vc_file_urls)

        # Download the files
        downloaded_files = download_files(alpine_vc_file_urls)

        print("Downloaded files:", downloaded_files)
        downloaded_files=['temp_uploads/Alpine VC Overview.pdf', 'temp_uploads/Ed Suh Deal Sheet (Current & Prior) (1).xlsx']

        # Here, you would extract content from the downloaded files
        extracted_content = []
        for file_path in downloaded_files:
            content = extractContent(file_path)  # Assuming extractContent function is implemented
            extracted_content.append({"name": os.path.basename(file_path), "content": content})
        
        print("extracted content",extracted_content)


        # Analyze the extracted content
        excel_analysis = analyzeDocuments(extracted_content,system_prompt_excel) 
        doc_analysis = analyzeDocuments(extracted_content,system_prompt_doc)
        
        
        save_to_excel(excel_analysis)
        save_doc_to_docx(doc_analysis)


        # Return the analysis result
        return JSONResponse(content={"success": True, "doc":doc_analysis,"excel":excel_analysis}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)
