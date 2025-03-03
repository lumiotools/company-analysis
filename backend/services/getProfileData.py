import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def search_contactout(name, companies):
    """
    Search for contacts using the ContactOut API.
    
    Args:
        name (str): The name of the person to search for
        companies (list): List of company names to search
        
    Returns:
        dict: JSON response from the ContactOut API
        
    Example:
        >>> search_contactout("Subhajit Hait", ["Stealth Startup"])
    """
    # Get API token from environment variables
    api_token = os.getenv("CONTACTOUT_API_TOKEN")
    
    if not api_token:
        raise ValueError("CONTACTOUT_API_TOKEN not found in environment variables")
    
    # API endpoint
    url = "https://api.contactout.com/v1/people/search"
    
    # Headers
    headers = {
        "token": api_token,
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "name": name,
        "company": companies
    }
    
    # Make the API request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Check if the request was successful
    response.raise_for_status()
    
    # Return the JSON response
    return response.json()