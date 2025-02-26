import json
import os
import concurrent.futures
from services.analyzeDocuments import analyzeDocuments
import tiktoken
from typing import Dict, List, Any, Optional

# Configuration parameters
MAX_TOKENS_PER_API_CALL = 120000
MAX_TOKENS_PER_CHUNK = 25000
MAX_FILES_PER_CHUNK = 5
ERROR_RETRIES = 3
TOKEN_SAFETY_BUFFER = 1000
PARALLEL_JOBS = 5  # Number of parallel processing jobs


# Helper functions
def get_encoder():
    """Get a token encoder for counting tokens."""
    try:
        return tiktoken.encoding_for_model("gpt-4")
    except Exception:
        return tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count the number of tokens in text."""
    if not isinstance(text, str):
        text = json.dumps(text)
    encoder = get_encoder()
    return len(encoder.encode(text))

def clean_json_string(obj):
    """Clean JSON strings by removing problematic characters."""
    if isinstance(obj, dict):
        return {k: clean_json_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_string(item) for item in obj]
    elif isinstance(obj, str):
        # Replace problematic characters
        return obj.replace('\x00', '').replace('\x1a', '')
    else:
        return obj

def estimate_document_tokens(document: Any) -> int:
    """
    Estimate the number of tokens in a document.
    
    Args:
        document: Document object
        
    Returns:
        Estimated token count
    """
    if isinstance(document, str):
        # If the document is already a string, count tokens directly
        return count_tokens(document)
    
    # Content tokens
    content_tokens = count_tokens(document.get("content", ""))
    
    # Add tokens for metadata (path, filename)
    metadata_tokens = count_tokens(document.get("path", "")) + count_tokens(document.get("file", ""))
    
    # Add overhead tokens for JSON structure, field names, etc.
    overhead_tokens = 20
    return content_tokens + metadata_tokens + overhead_tokens

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
            if isinstance(doc, str):
                try:
                    doc_obj = json.loads(doc)
                    content = doc_obj.get("content", "")
                except Exception:
                    content = doc
                    doc_obj = {"content": content}
            else:
                content = doc.get("content", "")
                doc_obj = doc
                
            encoder = get_encoder()
            encoded_content = encoder.encode(content)
            
            # Calculate safe limit (accounting for metadata)
            metadata_tokens = doc_tokens - count_tokens(content)
            content_token_limit = max_tokens_per_chunk - metadata_tokens - 100  # 100 tokens buffer
            
            # Truncate content if needed
            if content_token_limit > 0 and len(encoded_content) > content_token_limit:
                truncated_content = encoder.decode(encoded_content[:content_token_limit])
                truncated_content += "\n\n[CONTENT TRUNCATED DUE TO SIZE LIMITATIONS]"
                
                truncated_doc = doc_obj.copy() if isinstance(doc_obj, dict) else {"content": content}
                truncated_doc["content"] = truncated_content
                
                # If there's an ongoing chunk, finish it first
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_tokens = 0
                
                chunks.append([truncated_doc])
                continue
        
        # Check if adding this document would exceed the chunk limits
        if (current_tokens + doc_tokens > max_tokens_per_chunk) or (len(current_chunk) >= max_files_per_chunk):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [doc]
            current_tokens = doc_tokens
        else:
            current_chunk.append(doc)
            current_tokens += doc_tokens
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def process_hierarchical_data(
    result_location: str, 
    system_prompt_excel: str, 
    system_prompt_doc: str,
    max_tokens: int = MAX_TOKENS_PER_API_CALL,
    max_chunk_tokens: int = MAX_TOKENS_PER_CHUNK,
    max_files_per_chunk: int = MAX_FILES_PER_CHUNK,
    parallel_jobs: int = PARALLEL_JOBS
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
        parallel_jobs: Number of parallel processing jobs
        
    Returns:
        Dict with analysis results
    """
    print(f"Processing hierarchical data from {result_location}")
    
    try:
        with open(result_location, 'r') as f:
            data = json.load(f)
        
        result = {
            "directory": data.get("directory", "root"),
            "files": []
        }
        
        for item in data.get("files", []):
            if "directory" in item:
                folder_name = item["directory"]
                print(f"Processing top-level folder: {folder_name}")
                
                folder_result = analyze_folder(
                    item, 
                    system_prompt_excel, 
                    system_prompt_doc,
                    max_tokens,
                    max_chunk_tokens,
                    max_files_per_chunk,
                    parallel_jobs
                )
                result["files"].append(folder_result)
            else:
                result["files"].append(item)
        
        output_directory = os.path.dirname(result_location)
        output_path = os.path.join(output_directory, "final_result.json")
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
            
        print(f"Analysis complete. Results saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error processing hierarchical data: {str(e)}")
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
    max_files_per_chunk: int = MAX_FILES_PER_CHUNK,
    parallel_jobs: int = PARALLEL_JOBS
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
        parallel_jobs: Number of parallel processing jobs
        
    Returns:
        Dict with folder analysis
    """
    folder_name = folder.get("directory", "Unknown")
    
    try:
        folder_result = {
            "directory": folder_name,
            "files": folder.get("files", []),
            "analysis": {
                "excel_analysis": None,
                "doc_analysis": None
            }
        }
        
        documents = []
        extract_documents(folder, documents)
        
        if not documents:
            print(f"No documents found in folder: {folder_name}")
            folder_result["analysis"]["excel_analysis"] = {"error": "No documents found in folder"}
            folder_result["analysis"]["doc_analysis"] = {"error": "No documents found in folder"}
            return folder_result
        
        cleaned_documents = [clean_json_string(doc) for doc in documents]
        total_tokens = sum(estimate_document_tokens(doc) for doc in cleaned_documents)
        print(f"Folder '{folder_name}' contains {len(documents)} documents ({total_tokens} tokens)")
        
        # Check if we're within limits for a single batch
        system_prompt_tokens = count_tokens(system_prompt_excel) + count_tokens(system_prompt_doc)
        available_tokens = max_tokens - system_prompt_tokens - TOKEN_SAFETY_BUFFER
        
        # Key fix: instead of sending all documents at once, we need to format each document
        # as an individual user message, which is what the analyzeDocuments function expects
        if total_tokens <= available_tokens and len(documents) <= max_files_per_chunk:
            print(f"Analyzing folder '{folder_name}' in a single batch")
            # Format documents in the way analyzeDocuments expects
            excel_result = analyze_documents_with_retries(cleaned_documents, system_prompt_excel)
            doc_result = analyze_documents_with_retries(cleaned_documents, system_prompt_doc)
        else:
            print(f"Splitting folder '{folder_name}' into chunks")
            chunks = split_into_chunks(cleaned_documents, max_chunk_tokens, max_files_per_chunk)
            print(f"Created {len(chunks)} chunks for folder '{folder_name}'")
            
            excel_results = process_chunks_in_parallel(chunks, system_prompt_excel, parallel_jobs, "Excel analysis")
            doc_results = process_chunks_in_parallel(chunks, system_prompt_doc, parallel_jobs, "Document analysis")
            
            excel_result = {"combined_analysis": True, "chunks": excel_results}
            doc_result = {"combined_analysis": True, "chunks": doc_results}
        
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

def process_chunks_in_parallel(
    chunks: List[List[Dict]], 
    system_prompt: str, 
    parallel_jobs: int,
    analysis_type: str
) -> List[Dict]:
    """
    Process document chunks in parallel.
    
    Args:
        chunks: List of document chunks to process
        system_prompt: System prompt for analysis
        parallel_jobs: Maximum number of parallel jobs
        analysis_type: Type of analysis for logging
        
    Returns:
        List of analysis results
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_jobs) as executor:
        future_to_chunk = {
            executor.submit(analyze_chunk_with_logging, chunk, system_prompt, i+1, len(chunks), analysis_type): i
            for i, chunk in enumerate(chunks)
        }
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk_idx = future_to_chunk[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Completed chunk {chunk_idx+1}/{len(chunks)} for {analysis_type}")
            except Exception as e:
                print(f"Error processing chunk {chunk_idx+1}/{len(chunks)} for {analysis_type}: {str(e)}")
                results.append({"error": str(e)})
    
    return results

def analyze_chunk_with_logging(
    chunk: List[Dict], 
    system_prompt: str, 
    chunk_num: int, 
    total_chunks: int,
    analysis_type: str
) -> Dict:
    """
    Analyze a chunk with logging.
    
    Args:
        chunk: Document chunk to analyze
        system_prompt: System prompt for analysis
        chunk_num: Current chunk number
        total_chunks: Total number of chunks
        analysis_type: Type of analysis for logging
        
    Returns:
        Analysis result
    """
    chunk_size = sum(estimate_document_tokens(doc) for doc in chunk)
    print(f"Processing chunk {chunk_num}/{total_chunks} for {analysis_type}")
    print(f"  Chunk size: {chunk_size} tokens, {len(chunk)} files")
    
    # Clean each document individually to avoid list-level cleaning
    cleaned_chunk = [clean_json_string(doc) for doc in chunk]
    
    # Apply additional compression for large chunks
    if chunk_size > MAX_TOKENS_PER_CHUNK * 0.8:
        print(f"  Chunk size is large, applying additional compression")
        for doc in cleaned_chunk:
            if isinstance(doc, dict) and "content" in doc:
                doc["content"] = " ".join(doc["content"].split())
    
    # Now send for analysis
    result = analyze_documents_with_retries(cleaned_chunk, system_prompt)
    return result

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
            extract_documents(item, documents, current_path)
        elif "file" in item and "content" in item:
            document = {
                "path": current_path + "/" + item["file"],
                "file": item["file"],
                "content": item["content"]
            }
            documents.append(document)

def analyze_documents_with_retries(
    documents: List[Dict], 
    system_prompt: str, 
    max_retries: int = ERROR_RETRIES
) -> Dict:
    """
    Analyze documents with retry logic, adapting to analyzeDocuments API.
    
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
            
            # Check if we have too many documents
            if len(documents) > 40:  # Set a reasonable limit to avoid API errors
                print(f"Warning: Large number of documents ({len(documents)}). Reducing to 40.")
                documents = documents[:40]
            
            # Convert documents to strings if they're not already
            document_strings = []
            for doc in documents:
                if isinstance(doc, str):
                    document_strings.append(doc)
                else:
                    document_strings.append(json.dumps(doc))
            
            # Count tokens to anticipate API issues
            total_tokens = sum(count_tokens(doc) for doc in document_strings)
            print(f"Total document tokens: {total_tokens}")
            
            if total_tokens > MAX_TOKENS_PER_API_CALL - 5000:  # Leave room for system prompt
                print(f"Warning: Documents exceed API token limit. Truncating...")
                # Keep reducing until we're under the limit
                while len(document_strings) > 1 and total_tokens > MAX_TOKENS_PER_API_CALL - 5000:
                    document_strings = document_strings[:-1]  # Remove the last document
                    total_tokens = sum(count_tokens(doc) for doc in document_strings)
                print(f"Reduced to {len(document_strings)} documents ({total_tokens} tokens)")
            
            # Key fix: We're passing the document strings directly to analyzeDocuments
            # This function expects to add each document as a separate message
            result = analyzeDocuments(document_strings, system_prompt)
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error analyzing documents (attempt {retry+1}/{max_retries}): {error_msg}")
            
            if "array too long" in error_msg.lower():
                print("Array length issue detected. Reducing number of documents.")
                # Cut the number of documents in half each time
                documents = documents[:len(documents)//2]
            elif "token" in error_msg.lower() and len(documents) > 1:
                print("Token limit issue detected. Reducing content size.")
                # Try to reduce the size of each document
                for i, doc in enumerate(documents):
                    if isinstance(doc, dict) and "content" in doc:
                        content_len = len(doc["content"])
                        doc["content"] = doc["content"][:content_len//2] + "\n\n[TRUNCATED]"
                    documents = documents[:len(documents)//2]
            
            if retry == max_retries - 1:
                return {"error": f"Failed after {max_retries} attempts: {error_msg}"}

if __name__ == "__main__":
    # Sample execution
    import sys
    if len(sys.argv) < 2:
        print("Usage: python document_analyzer.py <json_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    excel_prompt = "Analyze the Excel files in these documents and provide insights."
    doc_prompt = "Analyze the textual content in these documents and provide insights."
    
    result = process_hierarchical_data(file_path, excel_prompt, doc_prompt)
    print("Process complete!")