import os
from docx import Document
from docx.shared import Pt

UPLOAD_DIR = "temp_uploads"
DEFAULT_DOCX_FILENAME = "doc_extracted_results.docx"

def add_dict_to_doc(document, data, indent=0):
    """
    Recursively adds dictionary data to a docx document.
    Each key is added in bold with an indent based on its level.
    Lists are iterated through; nested dictionaries within lists are processed recursively.
    Null values (None) are handled gracefully.
    """
    indent_space = Pt(indent * 20)
    for key, value in data.items():
        # Create a paragraph for the key
        p_key = document.add_paragraph()
        p_key.paragraph_format.left_indent = indent_space
        run = p_key.add_run(f"{key}:")
        run.bold = True
        
        if isinstance(value, dict):
            # Process nested dictionaries recursively
            add_dict_to_doc(document, value, indent=indent+1)
        elif isinstance(value, list):
            # Process lists by iterating through their items
            for item in value:
                if isinstance(item, dict):
                    add_dict_to_doc(document, item, indent=indent+1)
                else:
                    p_item = document.add_paragraph()
                    p_item.paragraph_format.left_indent = Pt((indent+1) * 20)
                    # If item is None, convert to string "None"
                    p_item.add_run(f"- {item if item is not None else 'None'}")
        else:
            # For simple values, create a new paragraph
            p_value = document.add_paragraph()
            p_value.paragraph_format.left_indent = Pt((indent+1) * 20)
            # Convert None to string "None"
            text = str(value) if value is not None else "Not Found"
            p_value.add_run(text)

def save_doc_to_docx(doc_data, filename=DEFAULT_DOCX_FILENAME):
    """
    Saves the nested dictionary (doc_data) to a DOCX file.
    The data is recursively added with indentation reflecting the nested structure.
    A custom filename can be provided; otherwise, a default is used.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    file_path = os.path.join(UPLOAD_DIR, filename)
    document = Document()
    
    # Optional title or heading
    document.add_heading("Document Data", level=1)
    
    add_dict_to_doc(document, doc_data)
    
    document.save(file_path)
    print(f"Document saved to {file_path}")