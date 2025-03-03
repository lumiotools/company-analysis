import os
import json
import concurrent.futures
from services.extractContent import extractContent

UPLOAD_DIR = "temp_uploads"

def process_file(file_path, file_name):
    """Standalone function to extract content from a file."""
    content = extractContent(file_path)
    return {"file": file_name, "content": content}

def write_extracted_content_json(folder_name):
    base_folder = os.path.join(UPLOAD_DIR, folder_name)
    result_file = os.path.join(base_folder, "result.json")

    with open(result_file, "w", encoding="utf-8") as fp:
        def write_directory(dir_path, fp):
            """Recursively writes directory structure in JSON format."""
            dirname = os.path.basename(dir_path)
            fp.write('{"directory": ' + json.dumps(dirname) + ', "files": [')

            items = sorted(os.listdir(dir_path))
            files = []
            subdirectories = []

            for item in items:
                full_path = os.path.join(dir_path, item)
                if os.path.isdir(full_path):
                    subdirectories.append(full_path)
                elif os.path.isfile(full_path):
                    files.append((full_path, item))

            # Process files in parallel (Standalone function to avoid pickling issues)
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = executor.map(process_file, [f[0] for f in files], [f[1] for f in files])

            # Write processed files
            first_item = True
            for result in results:
                if not first_item:
                    fp.write(",")
                fp.write(json.dumps(result))
                first_item = False

            # Process subdirectories recursively
            for subdir in subdirectories:
                if not first_item:
                    fp.write(",")
                write_directory(subdir, fp)
                first_item = False

            fp.write("]}")

        # Start writing at the base folder.
        write_directory(base_folder, fp)

    return result_file
