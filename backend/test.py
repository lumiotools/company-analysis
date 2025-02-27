import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
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

pdf_path = "Alpine VC Overview.pdf"
extracted_text = extract_text_from_pdf(pdf_path)
print(extracted_text)
