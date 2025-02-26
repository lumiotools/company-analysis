import json
import os

from prompts import DOC_DATA_SYSTEM_PROMPT
from services.analyzeDocuments import analyzeDocuments


def combine_doc_analyses(input_file_path):
    """
    Processes fund documentation by combining all document chunks and analyzing them.
    
    Args:
        input_file_path (str): Path to the JSON file containing document chunks or
                               Path to a text file containing already parsed JSON chunks
    
    Returns:
        dict: Structured fund data or error information
    """
    try:
        # Read the input file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        
        # Print a debugging summary
        print(f"Processing document with {len(file_content)} characters")
        
        # Count how many potential fund entries we have in the input
        fund_count_estimate = file_content.count('"Fund Name"')
        print(f"Estimated number of fund entries in input: {fund_count_estimate}")
        
        # Prepare the input for the analyzeDocuments function
        input_data = {
            "combinedDocumentText": file_content
        }
        
        # Call the analyzeDocuments function with the combined input and system prompt
        structured_fund_data = analyzeDocuments(input_data, DOC_DATA_SYSTEM_PROMPT)
        
        # Validate that we got multiple funds in the output
        if isinstance(structured_fund_data, dict) and "analysis" in structured_fund_data:
            fund_count = len(structured_fund_data["analysis"])
            print(f"Number of unique funds found in analysis: {fund_count}")
            
            # Check if we have fewer funds than expected
            if fund_count < fund_count_estimate / 5:  # Rough heuristic allowing for duplicates
                print("Warning: Fewer unique funds than expected. Some funds may have been missed.")
        
        # Return the structured fund data
        return structured_fund_data
    
    except Exception as e:
        error_message = f"Error in combine_doc_analyses: {str(e)}"
        print(error_message)
        return {"error": str(e), "message": error_message}


