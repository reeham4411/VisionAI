from fastapi import APIRouter, UploadFile, File
from app.services.vision_service import analyze_image

router = APIRouter()

@router.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    image_bytes = await file.read()
    return analyze_image(image_bytes)
