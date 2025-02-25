import os
import json

from services.extractContent import extractContent

UPLOAD_DIR = "temp_uploads"

def write_extracted_content_json(folder_name):
    """
    Walks through the directory tree starting at UPLOAD_DIR/folder_name and writes a nested JSON structure
    directly to a file named 'result.json' in that folder. For each file, it extracts its content using extractContent()
    and writes an entry with "file" and "content".
    
    The JSON structure looks like:
    {
       "directory": <folder name>,
       "files": [
           { "file": <file name>, "content": <extracted content> },
           { "directory": <subfolder name>, "files": [ ... ] },
           ...
       ]
    }
    
    This function streams the output directly to disk and returns the location of the result file.
    """
    base_folder = os.path.join(UPLOAD_DIR, folder_name)
    result_file = os.path.join(base_folder, "result.json")
    
    with open(result_file, "w", encoding="utf-8") as fp:
        def write_directory(dir_path, fp):
            # Write the start of a directory object.
            dirname = os.path.basename(dir_path)
            fp.write('{"directory": ' + json.dumps(dirname) + ', "files": [')
            
            items = sorted(os.listdir(dir_path))
            first_item = True
            for item in items:
                full_path = os.path.join(dir_path, item)
                # Write a comma between items if needed.
                if not first_item:
                    fp.write(",")
                else:
                    first_item = False

                if os.path.isdir(full_path):
                    # Recursively write the subdirectory.
                    write_directory(full_path, fp)
                elif os.path.isfile(full_path):
                    # Extract content from the file and write its JSON representation.
                    content = extractContent(full_path)  # Assumes extractContent is implemented
                    file_obj = {"file": item, "content": content}
                    fp.write(json.dumps(file_obj))
            fp.write("]}")
        
        # Start writing at the base folder.
        write_directory(base_folder, fp)
    
    return result_file

# Example usage:
# folder_name = "your_folder_name"  # Provided folder name (string)
# result_location = write_extracted_content_json(folder_name)
# print("Result JSON file written to:", result_location)
