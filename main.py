from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from typing import List

from services import OCRService, SearchService, TranslationService, ForeignMedicineService, contains_korean
from models import Base # Import Base
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

# Pydantic model for text search
class SearchQuery(BaseModel):
    query: str
    lang: str

# Database Setup
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    """Endpoint to get the search history."""
    return SearchService.get_search_history(db)

@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...), 
    lang: str = Form("en"),
    db: Session = Depends(get_db)
):
    # 1. Read Image
    contents = await file.read()
    
    # 2. OCR using Google Cloud Vision API
    print("Starting OCR with Google Cloud Vision...")
    
    # Try primary Vision API extraction
    drug_name = OCRService.extract_drug_name_with_vision(contents)
    
    # Also get full text for Korean detection
    weighted_texts = OCRService.extract_text_with_weights(contents)
    full_text = " ".join([t[0] for t in weighted_texts]) if weighted_texts else (drug_name or "")
    
    # Check if text contains Korean
    has_korean = contains_korean(full_text)
    print(f"OCR text contains Korean: {has_korean}")
    
    # If no Korean, this is likely a foreign medicine
    if not has_korean and full_text:
        print("Foreign medicine detected! Returning for alternative search...")
        return {
            "is_foreign": True,
            "extracted_text": drug_name or full_text[:200],  # Limit text length
            "message": "Foreign medicine detected. Please search for alternatives."
        }
    
    if drug_name:
        print(f"Vision API extracted name: {drug_name}")
        print("Searching DB with Vision API result...")
        drug_info, best_text = SearchService.search_drug_by_single_name(db, drug_name)
    else:
        print("Primary extraction failed. Using weighted text extraction...")
        
        if not weighted_texts:
            raise HTTPException(status_code=400, detail="No text could be extracted from the image.")
            
        print("Searching DB with weighted text (Fallback)...")
        drug_info, best_text = SearchService.search_drug_weighted(db, weighted_texts)
    
    if not drug_info:
        raise HTTPException(status_code=404, detail="No matching drug found in the database.")
    
    # 4. Add to history (if found)
    SearchService.add_to_history(db, drug_id=drug_info['id'], searched_text=best_text)
        
    # 5. Translate
    print(f"Translating to {lang}...")
    translated_info = TranslationService.translate_drug_info(drug_info, lang)
    
    return translated_info

@app.post("/search")
async def search_by_text(
    search: SearchQuery,
    db: Session = Depends(get_db)
):
    # 1. Search DB using the text query
    print(f"Searching DB with query: '{search.query}'...")
    drug_info, best_text = SearchService.search_drug_by_name(db, search.query)
    
    if not drug_info:
        raise HTTPException(status_code=404, detail="No matching drug found in the database.")
    
    # 2. Add to history
    SearchService.add_to_history(db, drug_id=drug_info['id'], searched_text=best_text)
        
    # 3. Translate
    print(f"Translating to {search.lang}...")
    translated_info = TranslationService.translate_drug_info(drug_info, search.lang)
    
    return translated_info

@app.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """
    [GROUP BY Query Endpoint]
    Returns manufacturer statistics (drug count per manufacturer).
    Uses SQL GROUP BY aggregation.
    Manufacturer names are kept in Korean.
    """
    stats = SearchService.get_manufacturer_statistics(db)
    return stats

@app.get("/drugs/by-manufacturer/{manufacturer_name}")
async def get_drugs_by_manufacturer(
    manufacturer_name: str,
    db: Session = Depends(get_db)
):
    """
    [JOIN Query Endpoint]
    Returns all drugs for a given manufacturer.
    Uses explicit SQL JOIN between drug_basic and manufacturer tables.
    """
    results = SearchService.get_drugs_by_manufacturer(db, manufacturer_name)
    if not results:
        raise HTTPException(status_code=404, detail="No drugs found for this manufacturer.")
    return results


class AlternativeQuery(BaseModel):
    foreign_drug_text: str
    lang: str = "en"


@app.post("/find-alternatives")
async def find_alternatives(
    query: AlternativeQuery,
    db: Session = Depends(get_db)
):
    """
    Finds Korean medicine alternatives for a foreign medicine.
    Uses OpenAI GPT-4.1 mini to identify alternatives, then searches DB.
    """
    print(f"Finding alternatives for: {query.foreign_drug_text}")
    
    # 1. Use OpenAI to find Korean alternatives
    alternative_names = ForeignMedicineService.find_korean_alternatives(query.foreign_drug_text)
    
    if not alternative_names:
        raise HTTPException(
            status_code=404, 
            detail="Could not find Korean alternatives for this medicine."
        )
    
    # 2. Search for alternatives in DB
    alternatives = ForeignMedicineService.search_alternatives_in_db(alternative_names, db)
    
    if not alternatives:
        raise HTTPException(
            status_code=404, 
            detail="No matching medicines found in database."
        )
    
    # 3. Translate manufacturer names if needed
    if query.lang != 'ko':
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target=query.lang)
        for item in alternatives:
            try:
                item['manufacturer'] = translator.translate(item['manufacturer'])
            except:
                pass
    
    return {
        "alternatives": alternatives,
        "original_query": query.foreign_drug_text
    }
