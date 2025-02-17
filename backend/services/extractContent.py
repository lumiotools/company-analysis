from fastapi import UploadFile
from pypdf import PdfReader
import pandas as pd
import io

def extractContent(file: UploadFile):
    print("Extracting content from file: ", file.filename)
    if file.filename.endswith(".pdf"):
        return extractPdfContent(file)
    elif file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
        return extractExcelContent(file)
    else:
        raise Exception("Unsupported file format")

def extractExcelContent(file: UploadFile):
    try:
        content = file.file.read()
        excel_file = pd.ExcelFile(io.BytesIO(content))
        text = ""

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            text += f"Sheet: {sheet_name}\n\n{buffer.getvalue()}\n\n"

        return text
    except Exception as e:
        print(str(e))
        return ""

def extractPdfContent(file: UploadFile):
    try:
        text = ""
        pdf = PdfReader(file.file)
        for index, page in enumerate(pdf.pages):
            if index != 0:
                text += "\n\n"

            text += page.extract_text(
                extraction_mode="plain"
            )
        
        return text
    except Exception as e:
        print(str(e))
        return ""
