import easyocr
from deep_translator import GoogleTranslator
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import DrugBasic, DrugUsage, DrugWarning, DrugSideEffect, Manufacturer

# Initialize OCR reader once (it's heavy)
reader = easyocr.Reader(['ko', 'en'], gpu=False)

class OCRService:
    @staticmethod
    def extract_text(image_bytes: bytes) -> list[str]:
        """
        Extracts text from image bytes using EasyOCR.
        Returns a list of detected strings.
        """
        try:
            result = reader.readtext(image_bytes, detail=0)
            return result
        except Exception as e:
            print(f"OCR Error: {e}")
            return []

class SearchService:
    @staticmethod
    @staticmethod
    def search_drug(db: Session, query_texts: list[str]) -> dict | None:
        """
        Searches for a drug in the database using a list of query texts (extracted from OCR).
        Uses keyword detection and fuzzy matching to find the best match.
        """
        from thefuzz import process, fuzz
        
        # 1. Fetch all drug names from DB (caching recommended for production)
        all_drugs = db.query(DrugBasic.name, DrugBasic.id).all()
        drug_names = [d.name for d in all_drugs]
        drug_map = {d.name: d.id for d in all_drugs}
        
        if not drug_names:
            return None

        best_match_name = None
        best_score = 0
        
        # 2. Iterate through OCR texts
        for text in query_texts:
            clean_text = text.strip()
            if len(clean_text) < 2:
                continue
                
            # Keyword Heuristic: If line contains "제품명" or similar, the rest is likely the name
            keywords = ["제품명", "품목명", "약품명", "상품명"]
            for kw in keywords:
                if kw in clean_text:
                    # Extract text after keyword
                    parts = clean_text.split(kw, 1)
                    if len(parts) > 1:
                        candidate = parts[1].strip(" :")
                        if candidate:
                            # Fuzzy match this candidate
                            match, score = process.extractOne(candidate, drug_names, scorer=fuzz.token_sort_ratio)
                            if score > best_score:
                                best_score = score
                                best_match_name = match

            # Standard Fuzzy Match on the whole line
            match, score = process.extractOne(clean_text, drug_names, scorer=fuzz.partial_ratio)
            
            # Boost score if it's a very close match
            if score > best_score:
                best_score = score
                best_match_name = match
        
        print(f"Best Match: {best_match_name} (Score: {best_score})")
        
        # Threshold for acceptance (e.g., 60%)
        if best_match_name and best_score >= 60:
            drug_id = drug_map[best_match_name]
            drug = db.query(DrugBasic).filter(DrugBasic.id == drug_id).first()
            return SearchService._format_drug_info(drug)
        
        return None

    @staticmethod
    def _format_drug_info(drug: DrugBasic) -> dict:
        return {
            "id": drug.id,
            "name": drug.name,
            "manufacturer": drug.manufacturer.name if drug.manufacturer else "",
            "storage": drug.storage,
            "effect": drug.usage.effect if drug.usage else "",
            "dosage": drug.usage.dosage if drug.usage else "",
            "precaution": drug.warning.precaution if drug.warning else "",
            "interaction": drug.warning.interaction if drug.warning else "",
            "side_effect": drug.side_effect.side_effect if drug.side_effect else ""
        }

class TranslationService:
    @staticmethod
    def translate_drug_info(drug_info: dict, target_lang: str) -> dict:
        """
        Translates the drug information values to the target language.
        """
        if target_lang == 'ko':
            return drug_info
            
        translator = GoogleTranslator(source='auto', target=target_lang)
        
        translated_info = drug_info.copy()
        fields_to_translate = [
            "storage", "effect", "dosage", 
            "precaution", "interaction", "side_effect"
        ]
        
        for field in fields_to_translate:
            text = drug_info.get(field, "")
            if text and len(text) > 0:
                try:
                    # Split into smaller chunks if too long (Google Translate limit is usually 5000 chars)
                    if len(text) > 4000:
                        text = text[:4000] + "..."
                    
                    translated_info[field] = translator.translate(text)
                except Exception as e:
                    print(f"Translation Error for {field}: {e}")
                    translated_info[field] = text # Fallback to original
                    
        return translated_info
