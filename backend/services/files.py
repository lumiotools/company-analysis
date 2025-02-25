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
    print(json.dumps(tree, indent=2))
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

def download_files(file_tuples):
    """
    For each file tuple (relative_path, metadata), send a POST request with
    form-encoded data to the /Download endpoint.
    Save the downloaded file in the UPLOAD_DIR directory.
    """
    downloaded_files = []
    for rel_path, metadata in file_tuples:
        # Split into directory and filename.
        directory, filename = os.path.split(rel_path)
        if not directory.endswith('/'):
            directory += '/'
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
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            downloaded_files.append(file_path)
            print(f"Downloaded: {file_path}")
        else:
            print(f"Failed to download {filename} from {download_url}: {response.status_code}")
    return downloaded_files




if __name__ == "__main__":
    listFiles()
