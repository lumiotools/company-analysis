from google import genai
import os
from services.extractContent import extract_excel_content
from prompts import system_prompt_excel, DOC_DATA_SYSTEM_PROMPT
import json
from concurrent.futures import ThreadPoolExecutor

# Initialize the Gemini client with your API key
api_key = os.getenv('GEMINI_API_KEY')  # Ensure your API key is set in the environment variables
client = genai.Client(api_key=api_key)

# def gemini_upload_files_direct(all_urls):
#     if not os.path.exists("temp"):
#         os.makedirs("temp")
#     def upload_single_file(file_url):
#         rel_path, metadata = file_url
#         directory, filename = os.path.split(rel_path)
#         if not directory.endswith('/'):
#             directory += '/'
        
#         # Build payload
#         payload_dict = {
#             "action": "download",
#             "path": directory,
#             "names": [filename],
#             "data": [metadata]
#         }
#         payload = {
#             "downloadInput": json.dumps(payload_dict)
#         }
#         headers = {
#             "Content-Type": "application/x-www-form-urlencoded",
#             "Origin": "http://localhost:3000",
#             "User-Agent": "Mozilla/5.0"
#         }
#         download_url = fileServer + "/Download"
#         print(f"Downloading from: {download_url} - File: {filename}")
        
#         try:
#             if ".docx" in metadata.get("type"):
#                 return None
#             response = requests.post(download_url, data=payload, headers=headers)
#             if response.status_code != 200:
#                 return None
#             if ".xlsx" in metadata.get("type"):
#                 return None
#                 # Extract content from Excel file
#                 # text = extract_excel_content_from_bytes(response.content)
#                 # uploaded_file = client.files.upload(file=text)
#             else:
#                 with open(f"temp/{uuid4()}{metadata.get("type")}", "wb") as f:
#                     f.write(response.content)
#                 uploaded_file = client.files.upload(file=f"temp/{uuid4()}{metadata.get("type")}")
#             print(f"Uploaded {metadata.get("name")} to Gemini.")
#             return uploaded_file
#             # if response.status_code == 200:
#             #     # Save the downloaded file in the proper subdirectory.
#             #     file_path = os.path.join(dest_dir, filename)
#             #     with open(file_path, 'wb') as f:
#             #         f.write(response.content)
#             #     print(f"Downloaded: {file_path}")
#             #     return file_path
#             # else:
#             #     print(f"Failed to download {filename} from {download_url}: {response.status_code}")
#             #     return None
#         except Exception as e:
#             print(str(e)[:200])
#             print(f"Error downloading {filename}")
#             return None

#     uploaded_files = []
#     with ThreadPoolExecutor(max_workers=20) as executor:
#         uploaded_files = list(executor.map(upload_single_file, all_urls))
#     return [file for file in uploaded_files if file is not None]

def gemini_upload_files(pdf_file_paths):
    def upload_single_file(pdf_path):
        if ".xlsx" in pdf_path:
            # Extract content from Excel file
            text = extract_excel_content(pdf_path)
            with open(pdf_path + ".txt", "w") as text_file:
                text_file.write(text)
            uploaded_file = client.files.upload(file=pdf_path+".txt")
        else:
            uploaded_file = client.files.upload(file=pdf_path)
        print(f"Uploaded {pdf_path} to Gemini.")
        return uploaded_file

    uploaded_files = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        uploaded_files = list(executor.map(upload_single_file, pdf_file_paths))
    return uploaded_files


def gemini_analyze_files_excel(uploaded_files):
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[
            system_prompt_excel,
            *uploaded_files
        ]
    )
    
    return json.loads(response.text.replace("```json\n", "").replace("```", ""))

def gemini_analyze_files_doc(uploaded_files):
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[
            DOC_DATA_SYSTEM_PROMPT,
            *uploaded_files
        ]
    )
    
    return json.loads(response.text.replace("```json\n", "").replace("```", ""))