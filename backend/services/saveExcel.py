import os
import pandas as pd

UPLOAD_DIR = "temp_uploads"
EXCEL_FILENAME = "extracted_results.xlsx"

def save_to_excel(result_dict, filename=EXCEL_FILENAME):
    """
    Appends the given result_dict (a dictionary with the required keys) as a new row to an Excel file.
    If the file does not exist, it creates one with the appropriate columns.
    This function also handles null values by replacing them with an empty string.
    """
    print("result dict",result_dict)
    # Ensure the upload directory exists
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Clean the dictionary: replace None with an empty string.
    cleaned_result = {k: ("" if v is None else v) for k, v in result_dict.items()}
    
    # Create a DataFrame from the cleaned dictionary.
    new_row = pd.DataFrame([cleaned_result])
    
    if os.path.exists(file_path):
        # If the file exists, read the current file, append the new row, then write back.
        try:
            existing_df = pd.read_excel(file_path)
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
        except Exception as e:
            print("Error reading existing Excel file:", e)
            updated_df = new_row
    else:
        # No existing file; use the new row as the DataFrame.
        updated_df = new_row

    # Write the updated DataFrame back to the Excel file.
    updated_df.to_excel(file_path, index=False)
    print(f"Data successfully saved to {file_path}")