import os
import json
import requests
from datetime import datetime

def create_folder_and_upload_files(file_paths, folder_name='docOutput'):
    """
    Creates a folder and uploads files to the server
    
    Args:
        file_paths (list): List of file paths to upload
        folder_name (str): Name of the folder to create
    """
    server_url = 'https://mdsv-file-server.onrender.com'
    
    # Common headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Origin': 'http://localhost:3000',
        'Referer': 'http://localhost:3000/',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    
    try:
        # Step 1: Create the folder
        print(f"Creating folder: {folder_name}")
        
        create_folder_data = {
            "action": "create",
            "path": "/",
            "name": folder_name,
            "data": [{
                "name": "uploads",
                "size": "4.00 KB",
                "isFile": False,
                "dateModified": datetime.now().isoformat(),
                "dateCreated": datetime.now().isoformat(),
                "type": "",
                "filterPath": "",
                "permission": None,
                "hasChild": True,
                "_fm_id": "fe_tree"
            }]
        }
        
        create_folder_headers = headers.copy()
        create_folder_headers['Content-Type'] = 'application/json'
        
        create_response = requests.post(
            server_url + '/',
            headers=create_folder_headers,
            data=json.dumps(create_folder_data)
        )
        
        print(f"Create folder response: {create_response.status_code}")
        print(create_response.text)
        
        # Step 2: Upload each file
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            print(f"Uploading file: {file_name}")
            
            # Create folder data
            folder_data = {
                "name": folder_name,
                "size": "4.00 KB",
                "isFile": False,
                "dateModified": datetime.now().isoformat(),
                "dateCreated": datetime.now().isoformat(),
                "type": "",
                "filterPath": "",
                "permission": None,
                "hasChild": True,
                "_fm_id": "fe_tree"
            }
            
            # Prepare the multipart form data
            files = {
                'uploadFiles': (file_name, open(file_path, 'rb'), 'application/octet-stream')
            }
            
            upload_data = {
                'path': f"/{folder_name}/",
                'size': str(file_size),
                'action': 'save',
                'data': json.dumps(folder_data),
                'filename': file_name
            }
            
            upload_response = requests.post(
                server_url + '/Upload',
                headers=headers,
                files=files,
                data=upload_data
            )
            
            print(f"File upload response for {file_name}: {upload_response.status_code}")
            print(upload_response.text)
            
        print("All files uploaded successfully!")
    
    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage
if __name__ == "__main__":
    files = [
        'temp_uploads/ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd/docOutputs/8-Bit Capital.docx',
        'temp_uploads/ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd/docOutputs/Draper Cygnus.docx',
        'temp_uploads/ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd/docOutputs/Alpine VC.docx',
        'temp_uploads/ff7decd6-fa0f-4ae8-ae46-8fe9c5ee31dd/docOutputs/Feld Ventures.docx'
    ]
    
    create_folder_and_upload_files(files, 'docOutput')