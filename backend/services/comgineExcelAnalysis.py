import json
import os
from typing import List, Dict, Any
from prompts import FUND_DATA_SYSTEM_PROMPT
from services.analyzeDocuments import analyzeDocuments


def combine_excel_analyses(final_result_location: str) -> List[Dict[str, Any]]:
    """
    Combine all Excel analyses from the final result JSON and standardize fund data.
    
    Args:
        final_result_location: Path to the final result JSON file
        
    Returns:
        List of unique fund data objects in standardized format
    """
    try:
        # Load the final result JSON
        with open(final_result_location, 'r') as f:
            final_result = json.load(f)
        
        # Extract all Excel analyses into a single list
        all_funds = []
        extract_all_funds(final_result, all_funds)
        
        if not all_funds:
            print("No fund data found in the result")
            return []
        
        print(f"Extracted {len(all_funds)} fund records")
        
        # Convert funds to a single document
        fund_doc = {
            "content": json.dumps(all_funds)
        }
        
        # Use analyzeDocuments with the deduplication prompt
        print("Analyzing and deduplicating fund data...")
        result = analyzeDocuments(fund_doc, FUND_DATA_SYSTEM_PROMPT)
        print("result:" , result)
        
        # Handle different result formats
        unique_funds = []
        if isinstance(result, dict):
            if "analysis" in result and isinstance(result["analysis"], list):
                unique_funds = result["analysis"]
            else:
                # If result is a single fund record, add it to the list
                unique_funds = [result]
        elif isinstance(result, list):
            unique_funds = result
        
        # Save the combined result - always save what we got even if it's just one record
        output_directory = os.path.dirname(final_result_location)
        output_path = os.path.join(output_directory, "combined_fund_data.json")
        with open(output_path, 'w') as f:
            json.dump({"success": True, "analysis": unique_funds}, f, indent=2)
        
        print(f"Combined fund data saved to {output_path}")
        return unique_funds
        
    except Exception as e:
        print(f"Error combining Excel analyses: {str(e)}")
        return []


def extract_all_funds(result_data: Any, funds_list: List[Dict[str, Any]]) -> None:
    """
    Recursively extract all fund data from the result.
    
    Args:
        result_data: Result data to extract from
        funds_list: List to append fund data to
    """
    if isinstance(result_data, dict):
        # Check if this is fund data
        if "Fund Manager" in result_data:
            funds_list.append(result_data)
            return
            
        # Check if this is a folder with Excel analysis
        if "analysis" in result_data and "excel_analysis" in result_data["analysis"]:
            excel_analysis = result_data["analysis"]["excel_analysis"]
            
            # Handle combined analysis with chunks
            if isinstance(excel_analysis, dict) and "chunks" in excel_analysis:
                for chunk in excel_analysis["chunks"]:
                    extract_all_funds(chunk, funds_list)
            else:
                extract_all_funds(excel_analysis, funds_list)
        
        # Recurse into all fields that are dicts or lists
        for value in result_data.values():
            if isinstance(value, (dict, list)):
                extract_all_funds(value, funds_list)
                
    elif isinstance(result_data, list):
        # Recurse into each item
        for item in result_data:
            extract_all_funds(item, funds_list)


# Example usage
if __name__ == "__main__":
    final_result_location = "temp_uploads/89eb76fb-1954-4053-abd3-3da48633136d/final_result.json"
    funds = combine_excel_analyses(final_result_location)
    print(f"Processed {len(funds)} funds")