from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from services import OCRService, SearchService, TranslationService

load_dotenv()

app = FastAPI()

# Database Setup
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount static files
# Available even when upload image with the browser and mobile
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...), 
    lang: str = Form("en"),
    db: Session = Depends(get_db)
):
    # 1. Read Image
    contents = await file.read()
    
    # 2. OCR
    print("Starting OCR...")
    extracted_texts = OCRService.extract_text(contents)
    print(f"Extracted Text: {extracted_texts}")
    
    if not extracted_texts:
        raise HTTPException(status_code=400, detail="No text found in image")
    
    # 3. Search
    print("Searching DB...")
    drug_info = SearchService.search_drug(db, extracted_texts)
    
    if not drug_info:
        raise HTTPException(status_code=404, detail="Drug not found in database")
        
    # 4. Translate
    print(f"Translating to {lang}...")
    translated_info = TranslationService.translate_drug_info(drug_info, lang)
    
    return translated_info
