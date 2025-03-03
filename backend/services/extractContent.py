from pypdf import PdfReader
import pandas as pd
import io
import os
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


import os
from llama_parse import LlamaParse
from dotenv import load_dotenv
load_dotenv()

# Initialize the LlamaParse client
parser = LlamaParse(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),  # Use os.getenv() not os.getenv[]
    result_type="markdown"  # Options: "markdown", "text", or "elements"
)


def extractContent(file_path: str):
    print("Extracting content from file:", file_path)
    
    try:
        if file_path.endswith(".pdf"):
            return extract_text_pdf_llama_parser(file_path)
        elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            return extract_excel_content(file_path)
        else:
            print(f"Warning: Unsupported file format for file {file_path}. Skipping extraction.")
            return ""
    except Exception as e:
        print(f"Error extracting content from {file_path}: {str(e)}")
        return ""

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
    
def extract_text_pdf_llama_parser(pdf_path: str):
    documents = parser.load_data(pdf_path)
    
    text = documents[0].text
    print(text)
    return text
    
def extract_text_from_pdf(pdf_path: str):
    text = ""
    doc = fitz.open(pdf_path)
    
    for page in doc:
        text += page.get_text("text")  # Extract text directly
    
    if text.strip():  
        return text  # Return extracted text if available

    # If no text, perform OCR on images
    images = convert_from_path(pdf_path)  
    ocr_text = "\n".join([pytesseract.image_to_string(img) for img in images])
    
    return ocr_text

def extract_excel_content(file_path: str) -> str:
    try:
        excel_file = pd.ExcelFile(file_path, engine="openpyxl")  # Efficient for .xlsx

        with io.StringIO() as buffer:
            for sheet_name in excel_file.sheet_names:
                df = excel_file.parse(sheet_name)  # Read sheet
                if df.empty:
                    continue  # Skip empty sheets

                buffer.write(f"Sheet: {sheet_name}\n\n")  # Add sheet name
                df.to_csv(buffer, index=False)  # Convert DataFrame to CSV
                buffer.write("\n\n")

            return buffer.getvalue()  # Get full extracted content

    except Exception as e:
        return f"Error extracting Excel content from {file_path}: {str(e)}"