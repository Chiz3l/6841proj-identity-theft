import os
import requests
from classification_pipeline import run_pipeline

# Constants for config
SERVER_URL = "http://127.0.0.1:8000/api/v1/upload"
API_KEY = "random-api-123"
# TARGET_EXTENSIONS = {'.pdf', '.docx', '.png', '.jpg', '.jpeg'} # this allows me to easily filter out if i want to search images or not
TARGET_EXTENSIONS = {'.pdf', '.docx'} # i realise i have a like a trillion screenshots so i have it disabled for now
HIGH_VALUE_CATEGORIES = {'IDENTIFICATION', 'FINANCIAL', 'LEGAL'} # ive left TECHNICAL out for now

def crawller(search_directory):
    print(f"check documents in: {search_directory}")
    
    # os walk will also ignore any files that you dont have access to incase they are encrypted 
    for root, _, files in os.walk(search_directory):
        for file in files:
            extension = os.path.splitext(file)[1].lower()
            if extension in TARGET_EXTENSIONS:
                file_path = os.path.join(root, file)
                
                try:
                    # try to classify if the document is imporant
                    metadata = run_pipeline(file_path)
                    category = metadata.get("category", "GENERAL_DOCUMENT")
                    
                    print(f"Found: {file} | Category: {category} | (Time to proccess: {metadata['total_time_sec']}s)")
                    
                    # upload the file to the server
                    if category in HIGH_VALUE_CATEGORIES:
                        upload_file_to_server(file_path, metadata)
                        
                # if for some reason a file was corrupted or an error occured
                except Exception as e:
                    print(f"error processing the file: {file_path}: {e}")

# upload files considered imporant to the server
def upload_file_to_server(file_path, metadata):
    api_key = {"X-API-Key": API_KEY}
    
    # uploading the files to the server
    with open(file_path, "rb") as f:
        # since we wont be sure of the exact file format it is safest to just upload it as octet-steam aka an 8 byte file when sleecting th emedia type
        files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
        response = requests.post(SERVER_URL, headers=api_key, files=files, timeout=10)
        
    if response.status_code == 200:
        print(f"Uploaded {os.path.basename(file_path)} to server")
    else:
        print(f"upload failed ({response.status_code}): {response.text}")

if __name__ == "__main__":
    # currently just targeting the documents tab
    target_dir =  os.path.expanduser("~/Documents")
    crawller(target_dir)