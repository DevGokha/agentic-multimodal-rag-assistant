import time
import logging
from fastapi import APIRouter, UploadFile, File
import os
from app.utils.rag import process_pdf
from app.utils.image import analyze_image

# Step 0: Create a logger for the upload route
logger = logging.getLogger("upload")

router = APIRouter()

UPLOAD_DIR = "data/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Step 1: Endpoint for uploading PDF files (processed for RAG)
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info("PDF upload: %s", file.filename)
    start_time = time.time()
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = process_pdf(file_path)
    elapsed = time.time() - start_time
    logger.info("PDF processed: %s | Time: %.2fs", file.filename, elapsed)

    return {"message": result}


# Step 2: Endpoint for uploading images (analyzed by vision model)
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    logger.info("Image upload: %s", file.filename)
    start_time = time.time()
    # Step 2a: Save the uploaded image to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Step 2b: Send the image to the Ollama vision model for analysis
    description = analyze_image(file_path)
    elapsed = time.time() - start_time
    logger.info("Image analyzed: %s | Time: %.2fs", file.filename, elapsed)

    # Step 2c: Return the AI-generated description
    return {"description": description}