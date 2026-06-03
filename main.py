from fastapi import FastAPI, UploadFile, File, HTTPException, status
from script.data_ingest import load_documents
from pathlib import Path
import shutil

app = FastAPI()

# Absolute base path: dynamic directory where this app file lives + /data
DOWNLOADS_DIR = Path(__file__).resolve().parent / "data"

ALLOWED_MIMETYPES = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/csv": ".csv",
}

@app.get("/health")
def health_check():
    return {"status": "server is Running"}

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = file.filename or ""
        extension = f".{filename.split('.')[-1]}".lower() if "." in filename else ""
        
        # 1. Validate extension
        if extension not in ALLOWED_MIMETYPES.values():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extension '{extension}' not allowed. Allowed: {list(ALLOWED_MIMETYPES.values())}"
            )
        
        # 2. Match directory generation with path generation (e.g., data/pdf/)
        sub_dir = DOWNLOADS_DIR / extension[1:]
        sub_dir.mkdir(parents=True, exist_ok=True)
        file_path = (sub_dir / filename).resolve()

        # 3. SAVE the binary payload from memory/temp space into your file path
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. VALIDATE file exists and contains actual data before running ingestion
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File upload failed: File could not be written to disk."
            )

        # 5. Process the verified file
        load_documents(file_path, extension)
        
        # 6. Return JSON response to client confirming receipt
        return {"filename": filename, "message": "File uploaded successfully"}
        
    except HTTPException as http_exc:
        # Prevent the general Exception catch-all from changing 400 Bad Request into a 500 error
        raise http_exc
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
