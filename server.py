import os
import hashlib
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, status

app = FastAPI(title="Stolen Identity Docs")

# creating the storage dir to store the documents
STORAGE_DIR = "./storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

API_KEY = os.getenv("API_KEY", "random-api-123")

@app.post("/api/v1/upload")
async def upload_document(
    file: UploadFile = File(...),
    recieved_api_key: str = Header(...)
):
    # checks the api key providede is valid
    if recieved_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    # loads the entire file and then hashes the content of the file
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # this saves the file as: [hash].[file extension]
    # this is done so that if there is 2 identity docs with the same name they dont collide when attempting to save them
    file_extension = os.path.splitext(file.filename)[1].lower()
    safe_filename = f"{file_hash}{file_extension.lower()}"
    target_path = os.path.join(STORAGE_DIR, safe_filename)
    
    # actually saving the file
    with open(target_path, "wb") as f:
        f.write(content)
        
    # general return variables
    return {
        "status": "success",
        "saved_as": safe_filename,
        "bytes_received": len(content)
    }

# allows me to run the file to make a temp server for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)