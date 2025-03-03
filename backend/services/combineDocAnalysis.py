import json
import os

from prompts import DOC_DATA_SYSTEM_PROMPT
from services.analyzeDocuments import analyzeDocuments
from services.getProfileData import search_contactout


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


import json
import os

from prompts import DOC_DATA_SYSTEM_PROMPT
from services.analyzeDocuments import analyzeDocuments


def combine_doc_analyses(input_file_path):
    """
    Processes fund documentation by combining all document chunks and analyzing them.
    If only one fund is detected, returns it directly without further processing.
    
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
        
        # If we estimate only one fund, try to parse it directly
        if fund_count_estimate == 1:
            print("Only one fund detected, processing directly without advanced analysis")
            try:
                # Try to parse as JSON first
                try:
                    parsed_data = json.loads(file_content)
                    
                    # Check if it's already in the expected format
                    if isinstance(parsed_data, dict) and "Fund Name" in parsed_data:
                        # Wrap in the expected return format
                        result = {"success": True, "analysis": [parsed_data]}
                        
                        # Save the single fund result
                        output_directory = os.path.dirname(input_file_path)
                        output_path = os.path.join(output_directory, "combined_doc_data.json")
                        with open(output_path, 'w') as f:
                            json.dump(result, f, indent=2)
                            
                        return result
                except json.JSONDecodeError:
                    # Not valid JSON, continue with regular process
                    pass
            except Exception as parse_error:
                print(f"Error trying to parse single fund directly: {str(parse_error)}")
                # Continue with regular process
        
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
        
        # Save the result
        output_directory = os.path.dirname(input_file_path)
        output_path = os.path.join(output_directory, "combined_doc_data.json")
        with open(output_path, 'w') as f:
            json.dump(structured_fund_data, f, indent=2)
        
        
        try:
            company = structured_fund_data["fund"]["general_information"]["name"]
            name = structured_fund_data["fund"]["primary_contact"]["name"]
            print(f"Company: {company}, Name: {name}")
            user_data = search_contactout(name, [company.split(" ")[0]])
            linkedins = list(dict(user_data["profiles"]).keys())
            print(f"Linkedins: {linkedins}")
            structured_fund_data["fund"]["primary_contact"]["linkedin"] = linkedins[0] if len(linkedins) > 0 else "Not Found"
        except Exception as e:
            try:
                structured_fund_data["fund"]["primary_contact"]["linkedin"] = "Not Found"
            except Exception as e:
                print(f"Error in search_contactout: {str(e)}")
        
        # Return the structured fund data
        return structured_fund_data
    
    except Exception as e:
        error_message = f"Error in combine_doc_analyses: {str(e)}"
        print(error_message)
        return {"error": str(e), "message": error_message}