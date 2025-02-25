import os
import tempfile
import requests
import json
from urllib.parse import quote

fileServer = "https://mdsv-file-server.onrender.com"
UPLOAD_DIR = "temp_uploads"

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def fetchFiles(path):
    response = requests.post(fileServer, json={
        "action": "read",
        "path": path,
        "showHiddenItems": False,
        "data": []
    })

    data = json.loads(json.loads(response.text))

    return data["files"]


def traverse_path(path):
    files = fetchFiles(path)
    tree = []
    for item in files:
        if item["isFile"]:
            tree.append(item["name"])
        else:
            subtree = traverse_path(path + "/" + item["name"])
            if subtree:
                tree.append({"directory": item["name"], "files": subtree})
    return tree


def listFiles():
    tree = traverse_path("/")
    # print(json.dumps(tree, indent=2))
    return tree

# Function to find "Alpine VC" files from the directory tree
def find_alpine_vc_files(files, current_path=""):
    """
    Recursively search the directory tree to build full relative paths
    for files in the "Alpine VC" directory.
    Returns a list of tuples: (relative_path, file_metadata)
    """
    alpine_files = []
    for item in files:
        if isinstance(item, dict):
            dir_name = item.get("directory")
            new_path = current_path + "/" + dir_name if current_path else "/" + dir_name
            if dir_name == "Alpine VC":
                for f in item.get("files", []):
                    if isinstance(f, str):  # it's a file name
                        file_relative_path = new_path + "/" + f
                        # Build minimal metadata (adjust as needed)
                        metadata = {
                            "name": f,
                            "isFile": True,
                            "filterPath": new_path + "/",
                            "type": os.path.splitext(f)[1]
                        }
                        alpine_files.append((file_relative_path, metadata))
            else:
                alpine_files.extend(find_alpine_vc_files(item.get("files", []), new_path))
    return alpine_files


def get_all_files(files, current_path=""):
    """
    Recursively search the directory tree to build full relative paths
    for all files and return them in an array with metadata.
    Each element in the returned list is a tuple: (relative_path, metadata)
    """
    all_files = []
    for item in files:
        if isinstance(item, dict):
            dir_name = item.get("directory")
            new_path = f"{current_path}/{dir_name}" if current_path else f"/{dir_name}"
            all_files.extend(get_all_files(item.get("files", []), new_path))
        elif isinstance(item, str):
            file_relative_path = f"{current_path}/{item}"
            metadata = {
                "name": item,
                "isFile": True,
                "filterPath": current_path + "/",
                "type": os.path.splitext(item)[1]
            }
            all_files.append((file_relative_path, metadata))
    return all_files

def download_files(file_tuples, folder_name):
    """
    For each file tuple (relative_path, metadata), send a POST request with
    form-encoded data to the /Download endpoint.
    
    Creates a folder named after the provided folder_name (converted to a string)
    under UPLOAD_DIR and replicates the source folder hierarchy when saving the files.
    """
    downloaded_files = []
    
    # Convert folder_name (UUID) to string and create the base folder.
    folder_name_str = str(folder_name)
    base_folder = os.path.join(UPLOAD_DIR, folder_name_str)
    os.makedirs(base_folder, exist_ok=True)
    
    for rel_path, metadata in file_tuples:
        # Split into directory and filename.
        directory, filename = os.path.split(rel_path)
        if not directory.endswith('/'):
            directory += '/'
        
        # Replicate the source hierarchy:
        # Remove any leading slash from the directory and join with base_folder.
        relative_dir = directory.lstrip('/')
        dest_dir = os.path.join(base_folder, relative_dir)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Build payload as before.
        payload_dict = {
            "action": "download",
            "path": directory,
            "names": [filename],
            "data": [metadata]
        }
        payload = {
            "downloadInput": json.dumps(payload_dict)
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://localhost:3000",
            "User-Agent": "Mozilla/5.0"
        }
        download_url = fileServer + "/Download"
        print("Downloading from:", download_url, "with payload:", payload)
        
        response = requests.post(download_url, data=payload, headers=headers)
        if response.status_code == 200:
            # Save the downloaded file in the proper subdirectory.
            file_path = os.path.join(dest_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            downloaded_files.append(file_path)
            print(f"Downloaded: {file_path}")
        else:
            print(f"Failed to download {filename} from {download_url}: {response.status_code}")
    return downloaded_files



if __name__ == "__main__":
    listFiles()
