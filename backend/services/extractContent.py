from pypdf import PdfReader
import pandas as pd
import io
import os

def extractContent(file_path: str):
    print("Extracting content from file: ", file_path)
    
    if file_path.endswith(".pdf"):
        return extractPdfContent(file_path)
    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        return extractExcelContent(file_path)
    else:
        raise Exception("Unsupported file format")

def extractExcelContent(file_path: str):
    try:
        text = ""
        # Read the Excel file from the provided path
        excel_file = pd.ExcelFile(file_path)
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            text += f"Sheet: {sheet_name}\n\n{buffer.getvalue()}\n\n"
        
        return text
    except Exception as e:
        print(f"Error extracting Excel content from {file_path}: {str(e)}")
        return ""

def extractPdfContent(file_path: str):
    try:
        text = ""
        # Open the PDF file from the provided path
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            for index, page in enumerate(pdf.pages):
                if index != 0:
                    text += "\n\n"
                text += page.extract_text(extraction_mode="plain")
        
        return text
    except Exception as e:
        print(f"Error extracting PDF content from {file_path}: {str(e)}")
        return ""
