import asyncio
import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from services.fileUpload import create_folder_and_upload_files
from services.combineDocAnalysis import combine_doc_analyses
from services.comgineExcelAnalysis import combine_excel_analyses
from services.analyzer import process_hierarchical_data
from services.saveJosn import write_extracted_content_json
from services.files import download_files, find_alpine_vc_files, listFiles, get_all_files
from services.extractContent import extractContent
from services.analyzeDocuments import analyzeDocuments
import os
import tempfile
import requests
from prompts import system_prompt, system_prompt_doc, system_prompt_excel
from services.saveExcel import save_to_excel
from services.saveDoc import save_multiple_analyses_to_docx
import shutil

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
        #print("files",files)
        all_file_urls = get_all_files(files)  # Find files under 'Alpine VC'

        # print("All files to download:", all_file_urls)
        folder_name=uuid.uuid4()
        # folder_name="ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd"

        # Download the files
        downloaded_files = download_files(all_file_urls,folder_name)

        print("Downloaded files:", downloaded_files)
        folder_name = str(folder_name)
        # downloaded_files=['temp_uploads/Alpine VC Overview.pdf', 'temp_uploads/Ed Suh Deal Sheet (Current & Prior) (1).xlsx']

        # # Here, you would extract content from the downloaded files
        # extracted_content = []
        # for file_path in downloaded_files:
        #     content = extractContent(file_path)  # Assuming extractContent function is implemented
        #     extracted_content.append({"name": os.path.basename(file_path), "content": content})

        result_location = write_extracted_content_json(folder_name)
        # print("Result JSON file written to:", result_location)
        # result_location="temp_uploads/89eb76fb-1954-4053-abd3-3da48633136d/result.json"
        
        # print("extracted content",extracted_content)


        # # Analyze the extracted content
        # excel_analysis = analyzeDocuments(extracted_content,system_prompt_excel) 
        # doc_analysis = analyzeDocuments(extracted_content,system_prompt_doc)

        final_result_location = process_hierarchical_data(result_location, system_prompt_excel, system_prompt_doc)
        # print("final result", final_result,"final path",final_path)

        # final_result_location = f"temp_uploads/{folder_name}/final_result.json"
        combinedExcelAnalysis=combine_excel_analyses(final_result_location)
        combinedDocAnalysis=combine_doc_analyses(final_result_location)
        saved_files = save_multiple_analyses_to_docx(combinedDocAnalysis,folder_name)
        # print("saved files",saved_files)
        # saved_files=['temp_uploads/ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd/docOutputs/8-Bit Capital.docx', 'temp_uploads/ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd/docOutputs/Draper Cygnus.docx', 'temp_uploads/ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd/docOutputs/Alpine VC.docx', 'temp_uploads/ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd/docOutputs/Feld Ventures.docx']
        create_folder_and_upload_files(saved_files, 'docOutput')

        
        # save_to_excel(excel_analysis)
        # save_doc_to_docx(doc_analysis)


        # Return the analysis result
        return JSONResponse(content={"success": True,"excel":combinedExcelAnalysis, "doc":combinedDocAnalysis})
        return JSONResponse(content={"success": True, "doc":doc_analysis,"excel":excel_analysis}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)
    finally:
        folder_path = os.path.join(UPLOAD_DIR, folder_name)
        # Clean up the temporary folder
        try:
            if os.path.exists(folder_path):
                print(f"Cleaning up temporary folder: {folder_path}")
                shutil.rmtree(folder_path)
                print(f"Successfully removed {folder_path}")
            else:
                print(f"Folder {folder_path} does not exist, no cleanup needed")
        except Exception as cleanup_error:
            print(f"Error during cleanup: {str(cleanup_error)}")




@app.post("/api/analyze2")
async def analyze_company():
    await asyncio.sleep(30)  # Simulates a 30-second delay

    return {
        "Fund Manager": "Alpine VC",
        "TVPI": None,
        "Location": "United States",
        "URL": None,
        "Summary": "Alpine VC is a data-driven seed firm supporting outlier outsider founders by providing insider advantages through unique data models and a diversified investment strategy across various markets.",
        "Fund Stage": "Seed",
        "Fund Size": "$20M USD",
        "Invested to Date": "$15M",
        "Minimum Check Size": "$10,000",
        "# of Portfolio Companies": "20-25 Target Companies",
        "Stage Focus": "Seed",
        "Sectors": "Consumer tech, SMB software",
        "Market Validated Outlier": None,
        "Female Partner in Fund": None,
        "Minority (BIPOC) Partner in Fund": None
    }


