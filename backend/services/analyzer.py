# services/analyzer.py

import json
import os
import tiktoken
from typing import Dict, List, Any, Optional
from services.analyzeDocuments import analyzeDocuments

# Configuration parameters
MAX_TOKENS_PER_API_CALL = 120000
MAX_TOKENS_PER_CHUNK = 25000
MAX_FILES_PER_CHUNK = 5
ERROR_RETRIES = 3
TOKEN_SAFETY_BUFFER = 1000

def get_encoder():
    """Get a token encoder for counting tokens."""
    try:
        return tiktoken.encoding_for_model("gpt-4")
    except:
        return tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count the number of tokens in text."""
    encoder = get_encoder()
    return len(encoder.encode(text))

def estimate_json_tokens(json_obj: Any) -> int:
    """Estimate tokens in a JSON object."""
    json_str = json.dumps(json_obj)
    return count_tokens(json_str)

def process_hierarchical_data(
    result_location: str, 
    system_prompt_excel: str, 
    system_prompt_doc: str,
    max_tokens: int = MAX_TOKENS_PER_API_CALL,
    max_chunk_tokens: int = MAX_TOKENS_PER_CHUNK,
    max_files_per_chunk: int = MAX_FILES_PER_CHUNK
) -> Dict:
    """
    Process a hierarchical JSON structure with nested folders and files.
    
    Args:
        result_location: Path to the JSON file with folder hierarchy
        system_prompt_excel: System prompt for Excel analysis
        system_prompt_doc: System prompt for document analysis
        max_tokens: Maximum tokens per API call
        max_chunk_tokens: Maximum tokens per content chunk
        max_files_per_chunk: Maximum files per chunk
        
    Returns:
        Dict with analysis results
    """
    print(f"Processing hierarchical data from {result_location}")
    
    try:
        # Load the JSON data
        with open(result_location, 'r') as f:
            data = json.load(f)
        
        # Initialize result structure with the same top-level directory
        result = {
            "directory": data.get("directory", "root"),
            "files": []
        }
        
        # Process each top-level folder
        for item in data.get("files", []):
            if "directory" in item:
                folder_name = item["directory"]
                print(f"Processing top-level folder: {folder_name}")
                
                # Process this folder and add to results
                folder_result = analyze_folder(
                    item, 
                    system_prompt_excel, 
                    system_prompt_doc,
                    max_tokens,
                    max_chunk_tokens,
                    max_files_per_chunk
                )
                result["files"].append(folder_result)
            else:
                # This is a file at the top level, just include it
                result["files"].append(item)
        
        # Save the result
        output_directory = os.path.dirname(result_location)
        output_path = os.path.join(output_directory, "final_result.json")
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
            
        print(f"Analysis complete. Results saved to {output_path}")
        return result
        
    except Exception as e:
        print(f"Error processing hierarchical data: {str(e)}")
        # Create a minimal result with error information
        return {
            "directory": data.get("directory", "root") if 'data' in locals() else "unknown",
            "error": str(e),
            "files": []
        }

def analyze_folder(
    folder: Dict, 
    system_prompt_excel: str, 
    system_prompt_doc: str,
    max_tokens: int = MAX_TOKENS_PER_API_CALL,
    max_chunk_tokens: int = MAX_TOKENS_PER_CHUNK,
    max_files_per_chunk: int = MAX_FILES_PER_CHUNK
) -> Dict:
    """
    Analyze a folder and its contents.
    
    Args:
        folder: Folder object with files and subfolders
        system_prompt_excel: System prompt for Excel analysis
        system_prompt_doc: System prompt for document analysis
        max_tokens: Maximum tokens per API call
        max_chunk_tokens: Maximum tokens per content chunk
        max_files_per_chunk: Maximum files per chunk
        
    Returns:
        Dict with folder analysis
    """
    folder_name = folder.get("directory", "Unknown")
    
    try:
        # Initialize the result structure
        folder_result = {
            "directory": folder_name,
            "files": folder.get("files", []),
            "analysis": {
                "excel_analysis": None,
                "doc_analysis": None
            }
        }
        
        # Extract all documents from this folder
        documents = []
        extract_documents(folder, documents)
        
        if not documents:
            print(f"No documents found in folder: {folder_name}")
            folder_result["analysis"]["excel_analysis"] = {
                "error": "No documents found in folder"
            }
            folder_result["analysis"]["doc_analysis"] = {
                "error": "No documents found in folder"
            }
            return folder_result
        
        # Calculate total tokens
        total_tokens = sum(estimate_document_tokens(doc) for doc in documents)
        print(f"Folder '{folder_name}' contains {len(documents)} documents ({total_tokens} tokens)")
        
        # Check if we need to chunk
        system_prompt_tokens = count_tokens(system_prompt_excel) + count_tokens(system_prompt_doc)
        available_tokens = max_tokens - system_prompt_tokens - TOKEN_SAFETY_BUFFER
        
        if total_tokens <= available_tokens and len(documents) <= max_files_per_chunk:
            # Can analyze all at once
            print(f"Analyzing folder '{folder_name}' in a single batch")
            excel_result = analyze_documents_with_retries(documents, system_prompt_excel)
            doc_result = analyze_documents_with_retries(documents, system_prompt_doc)
        else:
            # Need to chunk
            print(f"Splitting folder '{folder_name}' into chunks")
            chunks = split_into_chunks(documents, max_chunk_tokens, max_files_per_chunk)
            print(f"Created {len(chunks)} chunks for folder '{folder_name}'")
            
            # Process each chunk
            excel_results = []
            doc_results = []
            
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)} for folder '{folder_name}'")
                chunk_size = sum(estimate_document_tokens(doc) for doc in chunk)
                print(f"  Chunk size: {chunk_size} tokens, {len(chunk)} files")
                
                excel_chunk_result = analyze_documents_with_retries(chunk, system_prompt_excel)
                doc_chunk_result = analyze_documents_with_retries(chunk, system_prompt_doc)
                
                excel_results.append(excel_chunk_result)
                doc_results.append(doc_chunk_result)
            
            # Combine results
            excel_result = {
                "combined_analysis": True,
                "chunks": excel_results
            }
            
            doc_result = {
                "combined_analysis": True,
                "chunks": doc_results
            }
        
        # Add analysis to result
        folder_result["analysis"]["excel_analysis"] = excel_result
        folder_result["analysis"]["doc_analysis"] = doc_result
        
        return folder_result
        
    except Exception as e:
        print(f"Error analyzing folder '{folder_name}': {str(e)}")
        return {
            "directory": folder_name,
            "files": folder.get("files", []),
            "analysis": {
                "excel_analysis": {"error": str(e)},
                "doc_analysis": {"error": str(e)}
            }
        }

def extract_documents(folder: Dict, documents: List[Dict], path: str = "") -> None:
    """
    Extract all documents from a folder and its subfolders.
    
    Args:
        folder: Folder object to extract from
        documents: List to append documents to
        path: Current path for document references
    """
    current_path = path + "/" + folder.get("directory", "")
    
    for item in folder.get("files", []):
        if "directory" in item:
            # This is a subfolder, traverse it
            extract_documents(item, documents, current_path)
        elif "file" in item and "content" in item:
            # This is a document, add it to the list
            document = {
                "path": current_path + "/" + item["file"],
                "file": item["file"],
                "content": item["content"]
            }
            documents.append(document)

def estimate_document_tokens(document: Dict) -> int:
    """
    Estimate the number of tokens in a document.
    
    Args:
        document: Document object
        
    Returns:
        Estimated token count
    """
    # Content tokens
    content_tokens = count_tokens(document.get("content", ""))
    
    # Add tokens for metadata (path, filename)
    metadata_tokens = count_tokens(document.get("path", "")) + count_tokens(document.get("file", ""))
    
    # Add overhead tokens
    overhead_tokens = 20  # Tokens for JSON structure, field names, etc.
    
    return content_tokens + metadata_tokens + overhead_tokens

def analyze_documents_with_retries(
    documents: List[Dict], 
    system_prompt: str, 
    max_retries: int = ERROR_RETRIES
) -> Dict:
    """
    Analyze documents with retry logic.
    
    Args:
        documents: Documents to analyze
        system_prompt: System prompt for analysis
        max_retries: Maximum retry attempts
        
    Returns:
        Analysis result or error information
    """
    for retry in range(max_retries):
        try:
            print(f"Analyzing documents (attempt {retry+1}/{max_retries})")
            result = analyzeDocuments(documents, system_prompt)
            return result
        except Exception as e:
            error_msg = str(e)
            print(f"Error analyzing documents (attempt {retry+1}/{max_retries}): {error_msg}")
            
            # If last attempt, return error info
            if retry == max_retries - 1:
                return {
                    "error": f"Failed after {max_retries} attempts: {error_msg}"
                }

def split_into_chunks(
    documents: List[Dict], 
    max_tokens_per_chunk: int = MAX_TOKENS_PER_CHUNK,
    max_files_per_chunk: int = MAX_FILES_PER_CHUNK
) -> List[List[Dict]]:
    """
    Split documents into chunks that fit within token limits.
    
    Args:
        documents: Documents to split into chunks
        max_tokens_per_chunk: Maximum tokens per chunk
        max_files_per_chunk: Maximum files per chunk
        
    Returns:
        List of document chunks
    """
    # Sort documents by estimated size (largest first)
    sorted_docs = sorted(documents, key=estimate_document_tokens, reverse=True)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for doc in sorted_docs:
        doc_tokens = estimate_document_tokens(doc)
        
        # Handle documents that exceed chunk size on their own
        if doc_tokens > max_tokens_per_chunk:
            # If the document is too large, truncate its content
            content = doc.get("content", "")
            encoder = get_encoder()
            encoded_content = encoder.encode(content)
            
            # Calculate safe limit (accounting for metadata)
            metadata_tokens = doc_tokens - count_tokens(content)
            content_token_limit = max_tokens_per_chunk - metadata_tokens - 100  # 100 tokens buffer
            
            # Truncate content
            if content_token_limit > 0 and len(encoded_content) > content_token_limit:
                truncated_content = encoder.decode(encoded_content[:content_token_limit])
                truncated_content += "\n\n[CONTENT TRUNCATED DUE TO SIZE LIMITATIONS]"
                
                truncated_doc = doc.copy()
                truncated_doc["content"] = truncated_content
                
                # Create a separate chunk for this large document
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_tokens = 0
                
                chunks.append([truncated_doc])
                continue
        
        # Check if adding this document would exceed the chunk limits
        if (current_tokens + doc_tokens > max_tokens_per_chunk) or (len(current_chunk) >= max_files_per_chunk):
            # Start a new chunk
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [doc]
            current_tokens = doc_tokens
        else:
            # Add to current chunk
            current_chunk.append(doc)
            current_tokens += doc_tokens
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks