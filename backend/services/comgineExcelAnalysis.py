# combine_excel_analyses.py

import json
import os
from typing import List, Dict, Any
from services.analyzeDocuments import analyzeDocuments

# System prompt for fund data standardization and deduplication
FUND_DATA_SYSTEM_PROMPT = """You are an expert financial analyst specializing in venture capital and private equity.
Review the provided fund data and consolidate it into a single, accurate dataset with no duplicates.

First, identify and merge any duplicate funds. Consider these as duplicates:
- Entries with the same Fund Manager name
- Entries with very similar Fund Manager names (e.g., "8-Bit Capital", "8-BIT CAPITAL GP I, LLC", "8-Bit Capital I, L.P." likely refer to the same fund or fund family)
- Entries that clearly refer to the same entity despite name differences (use fund size, location, and focus areas as additional indicators)

For fund families with multiple funds (e.g., Fund I, Fund II), create separate entries for each distinct fund.

When merging duplicate entries, follow these rules:
1. Keep the most descriptive Fund Manager name that includes the specific fund identifier (e.g., prefer "8-BIT CAPITAL GP I, LLC" over generic "8-Bit Capital" when describing the first fund)
2. For each field, select the most complete/specific value among duplicates
3. For conflicting numerical values, prefer the more recent or more precise data
4. Preserve the most detailed Summary field, or combine information if they provide complementary details
5. For boolean fields, select "true" if any of the duplicate entries indicate "true"

Extract and standardize these specific data points for each unique fund:
- Fund Manager (name of the fund management company including the specific fund number if applicable)
- TVPI (Total Value to Paid-In capital ratio)
- Location (headquarters location)
- URL (website)
- Summary (brief description of the fund's strategy)
- Fund Stage (early, growth, late, etc.)
- Fund Size (target or current AUM)
- Invested to Date (amount deployed)
- Minimum Check Size (smallest investment amount)
- # of Portfolio Companies
- Stage Focus (what stages the fund invests in)
- Sectors (industries of focus)
- Market Validated Outlier (true/false/null)
- Female Partner in Fund (true/false/null)
- Minority (BIPOC) Partner in Fund (true/false/null)

Return your analysis as a structured JSON with an "analysis" array containing unique fund objects.
For any fields where information is not available, use null.
Convert all boolean fields to true, false, or null values.
"""

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
        
        # Use the advanced prompt to deduplicate and standardize
        unique_funds = standardize_and_deduplicate_funds(all_funds)
        
        # Save the combined result
        output_directory = os.path.dirname(final_result_location)
        output_path = os.path.join(output_directory, "combined_fund_data.json")
        with open(output_path, 'w') as f:
            json.dump({"success": True, "analysis": unique_funds}, f, indent=2)
        
        print(f"Combined into {len(unique_funds)} unique fund records, saved to {output_path}")
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

def standardize_and_deduplicate_funds(funds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Standardize and deduplicate fund data using analyzeDocuments with the advanced prompt.
    
    Args:
        funds: List of fund data to process
        
    Returns:
        List of unique standardized fund data
    """
    try:
        # Convert funds to a single document
        fund_doc = {
            "name": "fund_data.json",
            "content": json.dumps(funds, indent=2)
        }
        
        print(f"Processing {len(funds)} fund records")
        
        # Use analyzeDocuments with the deduplication prompt
        print("Analyzing and deduplicating fund data...")
        result = analyzeDocuments([fund_doc], FUND_DATA_SYSTEM_PROMPT)
        
        # Extract the unique funds from the result
        if isinstance(result, dict) and "analysis" in result and isinstance(result["analysis"], list):
            return result["analysis"]
        elif isinstance(result, list):
            return result
        else:
            print("Unexpected result format from analysis")
            return []
            
    except Exception as e:
        print(f"Error standardizing and deduplicating funds: {str(e)}")
        return []

# Example usage
if __name__ == "__main__":
    final_result_location = "temp_uploads/89eb76fb-1954-4053-abd3-3da48633136d/final_result.json"
    funds = combine_excel_analyses(final_result_location)
    print(f"Processed into {len(funds)} unique funds")