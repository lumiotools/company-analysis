import os
import asyncio
from typing import List, Dict, Any
import tiktoken
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: The text to count tokens for
        model: The model to use for tokenization
        
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base encoding if model-specific encoding not found
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))

def chunk_document_by_tokens(document: str, max_tokens: int = 120000, model: str = "gpt-4o") -> List[str]:
    """
    Split a document into chunks based on token count.
    
    Args:
        document: The document string to chunk
        max_tokens: Maximum tokens per chunk (accounting for prompt space)
        model: The model to use for tokenization
        
    Returns:
        List of document chunks
    """
    # Reserve 2000 tokens for the prompt and other message components
    max_chunk_tokens = max_tokens - 2000
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(document)
    total_tokens = len(tokens)
    
    # If document fits in one chunk, return it
    if total_tokens <= max_chunk_tokens:
        return [document]
    
    # Otherwise, split into chunks
    chunks = []
    current_chunk_tokens = []
    
    for token in tokens:
        current_chunk_tokens.append(token)
        
        if len(current_chunk_tokens) >= max_chunk_tokens:
            chunk_text = encoding.decode(current_chunk_tokens)
            chunks.append(chunk_text)
            current_chunk_tokens = []
    
    # Add the last chunk if there's anything left
    if current_chunk_tokens:
        chunk_text = encoding.decode(current_chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks

async def process_chunk_async(chunk: str, chunk_index: int, total_chunks: int, prompt: str, model: str) -> Dict:
    """
    Process a single chunk asynchronously.
    
    Args:
        chunk: The chunk text to process
        chunk_index: The index of this chunk (1-based)
        total_chunks: Total number of chunks
        prompt: The system prompt
        model: The model to use
        
    Returns:
        Analysis result for this chunk
    """
    chunk_prompt = f"""
    {prompt}
    
    This is part {chunk_index}/{total_chunks} of a large document. 
    Process this part and extract all fund data that you can find.
    """
    
    messages = [
        {"role": "system", "content": chunk_prompt},
        {"role": "user", "content": f"Input Document Part {chunk_index}: {chunk}"}
    ]
    
    try:
        response = await async_client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        chunk_analysis = json.loads(response.choices[0].message.content)
        print(f"Successfully processed chunk {chunk_index}")
        return chunk_analysis
    except Exception as e:
        print(f"Error processing chunk {chunk_index}: {str(e)}")
        # Return an empty result on error
        return {"error": str(e), "chunk": chunk_index}

def process_chunk(chunk: str, chunk_index: int, total_chunks: int, prompt: str, model: str) -> Dict:
    """
    Process a single chunk synchronously.
    
    Args:
        chunk: The chunk text to process
        chunk_index: The index of this chunk (1-based)
        total_chunks: Total number of chunks
        prompt: The system prompt
        model: The model to use
        
    Returns:
        Analysis result for this chunk
    """
    chunk_prompt = f"""
    {prompt}
    
    This is part {chunk_index}/{total_chunks} of a large document. 
    Process this part and extract all fund data that you can find.
    """
    
    messages = [
        {"role": "system", "content": chunk_prompt},
        {"role": "user", "content": f"Input Document Part {chunk_index}: {chunk}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        chunk_analysis = json.loads(response.choices[0].message.content)
        print(f"Successfully processed chunk {chunk_index}")
        return chunk_analysis
    except Exception as e:
        print(f"Error processing chunk {chunk_index}: {str(e)}")
        # Return an empty result on error
        return {"error": str(e), "chunk": chunk_index}

async def process_chunks_parallel_async(chunks: List[str], prompt: str, model: str, max_parallel: int = 5) -> List[Dict]:
    """
    Process chunks in parallel using async/await.
    
    Args:
        chunks: List of document chunks
        prompt: System prompt
        model: Model to use
        max_parallel: Maximum number of parallel requests
        
    Returns:
        List of analysis results
    """
    results = []
    
    # Process in batches of max_parallel
    for i in range(0, len(chunks), max_parallel):
        batch = chunks[i:i+max_parallel]
        batch_indices = list(range(i+1, i+len(batch)+1))
        
        print(f"Processing batch of {len(batch)} chunks in parallel")
        tasks = [
            process_chunk_async(chunk, idx, len(chunks), prompt, model)
            for chunk, idx in zip(batch, batch_indices)
        ]
        
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
    
    return results

def process_chunks_parallel(chunks: List[str], prompt: str, model: str, max_parallel: int = 5) -> List[Dict]:
    """
    Process chunks in parallel using ThreadPoolExecutor.
    
    Args:
        chunks: List of document chunks
        prompt: System prompt
        model: Model to use
        max_parallel: Maximum number of parallel requests
        
    Returns:
        List of analysis results
    """
    results = [None] * len(chunks)  # Pre-allocate list with correct size
    
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(
                process_chunk, 
                chunk, 
                idx+1, 
                len(chunks), 
                prompt, 
                model
            ): idx 
            for idx, chunk in enumerate(chunks)
        }
        
        # Process results as they complete
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                result = future.result()
                results[idx] = result
                print(f"Completed chunk {idx+1}/{len(chunks)}")
            except Exception as e:
                print(f"Exception processing chunk {idx+1}: {str(e)}")
                results[idx] = {"error": str(e), "chunk": idx+1}
    
    return results

def analyzeDocuments(documents, prompt, model="gpt-4o-mini", max_parallel=5):
    """
    Analyze documents using OpenAI API with proper token management and parallel processing.
    
    Args:
        documents: The documents to analyze
        prompt: The system prompt to use for analysis
        model: The model to use for analysis
        max_parallel: Maximum number of parallel chunks to process
        
    Returns:
        Analysis results
    """
    print("Analyzing documents")
    
    document = str(documents)
    prompt_tokens = count_tokens(prompt)
    document_tokens = count_tokens(document)
    
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Document tokens: {document_tokens}")
    
    # Max context size for the model (reserving 2000 tokens for the output)
    max_context = 126000  # 128000 - 2000
    
    # If it all fits in one request
    if prompt_tokens + document_tokens <= max_context:
        try:
            print("Document fits in a single request. Processing...")
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Input Document: {document}"}
            ]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            analysis = response.choices[0].message.content
            print("Analysis complete with full document")
            return json.loads(analysis)
            
        except Exception as e:
            print(f"Error with full document: {str(e)}")
            print("Falling back to chunk processing...")
    else:
        print(f"Document too large for single processing: {prompt_tokens + document_tokens} tokens")
    
    # Process in chunks
    chunks = chunk_document_by_tokens(document, max_context - prompt_tokens, model)
    print(f"Split document into {len(chunks)} chunks")
    
    # Process chunks in parallel
    print(f"Processing chunks in parallel with max {max_parallel} concurrent requests")
    
    # Use thread-based parallel processing 
    chunk_results = process_chunks_parallel(chunks, prompt, model, max_parallel)
    
    # Remove any error results and handle missing chunks
    valid_results = [result for result in chunk_results if "error" not in result]
    
    print(f"Successfully processed {len(valid_results)} of {len(chunks)} chunks")
    
    # If we only have one valid result, return it
    if len(valid_results) == 1:
        return valid_results[0]
    
    # If we have no valid results, return an error
    if not valid_results:
        return {"error": "All chunks failed to process"}
    
    # Phase 2: Consolidate results in manageable batches if needed
    print("Phase 1 complete. Starting final consolidation...")
    
    # Try to consolidate all results at once first
    consolidated_prompt = f"""
    {prompt}
    
    You are now processing the results from multiple chunks of a large document.
    Your task is to combine these results into a single, consolidated result.
    Remove any duplicates and ensure the final output matches the expected format.
    """
    
    # Convert chunk results to a string
    chunk_results_str = json.dumps(valid_results, indent=2)
    consolidation_tokens = count_tokens(consolidated_prompt) + count_tokens(chunk_results_str)
    
    if consolidation_tokens <= max_context:
        try:
            print("Attempting to consolidate all results at once...")
            consolidation_messages = [
                {"role": "system", "content": consolidated_prompt},
                {"role": "user", "content": f"Intermediate Results from Chunks: {chunk_results_str}"}
            ]
            
            consolidation_response = client.chat.completions.create(
                model=model,
                messages=consolidation_messages,
                response_format={"type": "json_object"}
            )
            
            final_analysis = json.loads(consolidation_response.choices[0].message.content)
            print("Final consolidation complete")
            return final_analysis
            
        except Exception as consolidation_error:
            print(f"Error during final consolidation: {str(consolidation_error)}")
    else:
        print(f"Consolidation would exceed token limit: {consolidation_tokens} tokens")
    
    # If consolidation in one go fails or would exceed the limit, process in batches
    print("Processing consolidation in batches...")
    
    # Consolidate in batches of 2-3 results at a time
    batch_size = 2
    batched_results = valid_results
    
    while len(batched_results) > 1:
        new_results = []
        
        # Process batches in parallel where possible
        for i in range(0, len(batched_results), batch_size):
            batch = batched_results[i:i+batch_size]
            
            if len(batch) == 1:
                new_results.append(batch[0])
                continue
            
            batch_str = json.dumps(batch, indent=2)
            batch_tokens = count_tokens(consolidated_prompt) + count_tokens(batch_str)
            
            if batch_tokens > max_context:
                print(f"Batch {i//batch_size + 1} too large: {batch_tokens} tokens. Adding results individually.")
                new_results.extend(batch)
                continue
            
            try:
                batch_messages = [
                    {"role": "system", "content": consolidated_prompt},
                    {"role": "user", "content": f"Intermediate Results Batch: {batch_str}"}
                ]
                
                batch_response = client.chat.completions.create(
                    model=model,
                    messages=batch_messages,
                    response_format={"type": "json_object"}
                )
                
                batch_analysis = json.loads(batch_response.choices[0].message.content)
                new_results.append(batch_analysis)
                print(f"Successfully consolidated batch {i//batch_size + 1}")
            except Exception as batch_error:
                print(f"Error consolidating batch {i//batch_size + 1}: {str(batch_error)}")
                # On error, just add the individual results
                new_results.extend(batch)
        
        # Update results for next iteration
        batched_results = new_results
        
        # If we're down to 3 or fewer results, increase batch size for final consolidation
        if 1 < len(batched_results) <= 3:
            batch_size = 3
    
    # Return the final consolidated result
    print("Batch consolidation complete")
    return batched_results[0]