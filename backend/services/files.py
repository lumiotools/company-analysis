import os
import tempfile
import requests
import json
from urllib.parse import quote
import concurrent.futures

fileServer = "https://company-analysis-y7dw.onrender.com"
UPLOAD_DIR = "temp_uploads"
MAX_CONCURRENT_DOWNLOADS = 5  # Set the maximum number of concurrent downloads

# Define file extensions to skip (audio and video files)
SKIP_EXTENSIONS = [
    # Video formats
    '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp',
    # Audio formats
    '.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a', '.wma', '.aiff', '.alac'
]

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

def download_single_file(rel_path, metadata, base_folder):
    """
    Download a single file specified by rel_path and metadata
    and save it to the appropriate location under base_folder.
    Returns the path of the downloaded file or None if download failed.
    """
    # Split into directory and filename.
    directory, filename = os.path.split(rel_path)
    if not directory.endswith('/'):
        directory += '/'
    
    # Replicate the source hierarchy:
    # Remove any leading slash from the directory and join with base_folder.
    relative_dir = directory.lstrip('/')
    dest_dir = os.path.join(base_folder, relative_dir)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Build payload
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
    print(f"Downloading from: {download_url} - File: {filename}")
    
    try:
        response = requests.post(download_url, data=payload, headers=headers)
        if response.status_code == 200:
            # Save the downloaded file in the proper subdirectory.
            file_path = os.path.join(dest_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {file_path}")
            return file_path
        else:
            print(f"Failed to download {filename} from {download_url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return None

def download_files(file_tuples, folder_name):
    """
    For each file tuple (relative_path, metadata), download the file using
    a thread pool to handle concurrent downloads.
    
    Creates a folder named after the provided folder_name (converted to a string)
    under UPLOAD_DIR and replicates the source folder hierarchy when saving the files.
    
    Uses MAX_CONCURRENT_DOWNLOADS to limit the number of concurrent downloads.
    Skips audio and video files based on their extensions.
    """
    downloaded_files = []
    failed_downloads = []
    skipped_files = []
    
    # Convert folder_name (UUID) to string and create the base folder.
    folder_name_str = str(folder_name)
    base_folder = os.path.join(UPLOAD_DIR, folder_name_str)
    os.makedirs(base_folder, exist_ok=True)
    
    # Filter out audio and video files
    filtered_file_tuples = []
    for rel_path, metadata in file_tuples:
        file_ext = os.path.splitext(rel_path)[1].lower()
        if file_ext in SKIP_EXTENSIONS:
            print(f"Skipping audio/video file: {rel_path}")
            skipped_files.append(rel_path)
        else:
            filtered_file_tuples.append((rel_path, metadata))
    
    print(f"Starting download of {len(filtered_file_tuples)} files (skipped {len(skipped_files)} audio/video files) with max {MAX_CONCURRENT_DOWNLOADS} concurrent downloads")
    
    # If no files to download after filtering
    if not filtered_file_tuples:
        print("No files to download after filtering out audio/video files.")
        return []
    
    # Use ThreadPoolExecutor to handle concurrent downloads
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
        # Submit all download tasks
        future_to_file = {
            executor.submit(download_single_file, rel_path, metadata, base_folder): (rel_path, metadata)
            for rel_path, metadata in filtered_file_tuples
        }
        
        # Process completed downloads
        for future in concurrent.futures.as_completed(future_to_file):
            rel_path, metadata = future_to_file[future]
            try:
                file_path = future.result()
                if file_path:
                    downloaded_files.append(file_path)
                else:
                    failed_downloads.append((rel_path, metadata))
            except Exception as e:
                print(f"Exception occurred while downloading {os.path.basename(rel_path)}: {str(e)}")
                failed_downloads.append((rel_path, metadata))
    
    print(f"Download complete. Successfully downloaded {len(downloaded_files)} files.")
    if failed_downloads:
        print(f"Failed to download {len(failed_downloads)} files.")
    if skipped_files:
        print(f"Skipped {len(skipped_files)} audio/video files.")
    
    return downloaded_files

def find_directory_by_name_in_list(structure, target_name):
    """
    Find a directory with the given name in the list structure and return the list 
    containing it along with the index of the directory in that list.
    
    Args:
        structure (list or dict): The nested file system structure
        target_name (str): The name of the directory to find
        
    Returns:
        tuple: (containing_list, index) or (None, None) if not found
    """
    if isinstance(structure, list):
        # Check each item in the list
        for i, item in enumerate(structure):
            # If the item is a dictionary with a 'directory' key matching the target
            if isinstance(item, dict) and 'directory' in item and item['directory'] == target_name:
                return structure, i
            
            # If it's a dictionary with 'directory' and 'files' keys, search in the 'files'
            if isinstance(item, dict) and 'directory' in item and 'files' in item:
                result, idx = find_directory_by_name_in_list(item['files'], target_name)
                if result is not None:
                    return result, idx
                    
    elif isinstance(structure, dict):
        # If it has 'files', search within them
        if 'files' in structure:
            result, idx = find_directory_by_name_in_list(structure['files'], target_name)
            if result is not None:
                return result, idx
                
    return None, None

def get_directory_list(structure, directory_name):
    """
    Takes a structure and directory name and returns a list containing only that directory.
    
    Args:
        structure (list or dict): The directory structure
        directory_name (str): Name of the directory to find
        
    Returns:
        list or None: A list containing just the found directory or None if not found
    """
    # Find the containing list and index
    containing_list, idx = find_directory_by_name_in_list(structure, directory_name)
    
    if containing_list is not None and idx is not None:
        # Return a new list with just that item
        return [containing_list[idx]]
    
    return None
if __name__ == "__main__":
    listFiles()