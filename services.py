import base64
import requests
import re
import json
from deep_translator import GoogleTranslator
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from models import DrugBasic, DrugUsage, DrugWarning, DrugSideEffect, Manufacturer, SearchHistory

import os
from dotenv import load_dotenv

load_dotenv()

# Get Google Vision API credentials from .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_VISION_API_URL = os.getenv("GOOGLE_VISION_API_URL", "https://vision.googleapis.com/v1/images:annotate")

# Get OpenAI API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

print(f"Using Google Vision API with URL: {GOOGLE_VISION_API_URL}")
if OPENAI_API_KEY:
    print("OpenAI API key loaded successfully")
else:
    print("Warning: OPENAI_API_KEY not found in .env file")


def contains_korean(text: str) -> bool:
    """Check if text contains any Korean characters."""
    return bool(re.search(r'[가-힣]', text))
class OCRService:
    @staticmethod
    def extract_drug_name_with_vision(image_bytes: bytes) -> str | None:
        """
        Uses Google Cloud Vision API (REST) to extract drug name from image.
        Returns the extracted name as a string or None if failed.
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Create API request
            request_data = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [
                            {"type": "DOCUMENT_TEXT_DETECTION"}
                        ]
                    }
                ]
            }
            
            # Call Vision API
            response = requests.post(
                f"{GOOGLE_VISION_API_URL}?key={GOOGLE_API_KEY}",
                json=request_data
            )
            
            if response.status_code != 200:
                print(f"Vision API Error: {response.status_code}")
                print(response.text)
                return None
            
            result = response.json()
            
            # Check for errors in response
            if "error" in result:
                print(f"Vision API Error: {result['error']}")
                return None
            
            # Extract text annotations
            responses = result.get("responses", [])
            if not responses or not responses[0].get("textAnnotations"):
                print("No text detected in image")
                return None
            
            text_annotations = responses[0]["textAnnotations"]
            
            # First annotation contains full text
            full_text = text_annotations[0]["description"]
            print(f"Vision API Full Text:\n{full_text}")
            
            # Try to find drug name using keywords
            lines = full_text.split('\n')
            drug_name = None
            
            # Keywords that typically precede drug name
            KEYWORDS = ["제품명", "품목명", "약품명", "명칭", "상품명"]
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Check if line contains keyword
                for kw in KEYWORDS:
                    if kw in line_stripped:
                        # If keyword is alone on the line, get next line
                        if line_stripped == kw or line_stripped == f"{kw}:":
                            if i + 1 < len(lines):
                                drug_name = lines[i + 1].strip()
                                break
                        else:
                            # Extract name after keyword
                            parts = line_stripped.split(kw)
                            if len(parts) > 1:
                                extracted = parts[1].replace(":", "").strip()
                                if extracted:
                                    drug_name = extracted
                                    break
                if drug_name:
                    break
            
            # If no keyword found, use smart filtering to find the drug name
            if not drug_name and len(text_annotations) > 1:
                import re
                
                # Helper function to check if text contains Korean
                def contains_korean(text):
                    return bool(re.search(r'[가-힣]', text))
                
                # Helper function to check if text is only numbers/symbols
                def is_only_numbers_symbols(text):
                    return bool(re.match(r'^[0-9\s\.,\-\(\)\[\]]+$', text))
                
                # Collect all candidate texts with scoring
                candidates = []
                
                for annotation in text_annotations[1:]:  # Skip first as it's the full text
                    vertices = annotation.get("boundingPoly", {}).get("vertices", [])
                    if len(vertices) >= 4:
                        x_coords = [v.get("x", 0) for v in vertices]
                        y_coords = [v.get("y", 0) for v in vertices]
                        width = max(x_coords) - min(x_coords)
                        height = max(y_coords) - min(y_coords)
                        area = width * height
                        
                        text = annotation.get("description", "").strip()
                        
                        # Filter out invalid candidates
                        if len(text) < 2:  # Too short
                            continue
                        if is_only_numbers_symbols(text):  # Only numbers/symbols
                            continue
                        if text.upper() in ['SINCE', 'ANNIVERSARY', 'TH', 'ST', 'ND', 'RD', 'E']:  # Common non-drug words
                            continue
                        
                        # Calculate score
                        score = area
                        
                        # Boost score for Korean text (강력하게 우선순위 부여)
                        if contains_korean(text):
                            score *= 10.0  # 한글 텍스트에 10배 가중치
                        
                        # Penalize very short English-only text
                        if not contains_korean(text) and len(text) <= 3:
                            score *= 0.1
                        
                        # Penalize all-uppercase English words longer than 5 chars (likely labels)
                        if text.isupper() and len(text) > 5 and not contains_korean(text):
                            score *= 0.3
                        
                        candidates.append({
                            'text': text,
                            'score': score,
                            'area': area,
                            'has_korean': contains_korean(text)
                        })
                
                # Sort by score (highest first)
                candidates.sort(key=lambda x: x['score'], reverse=True)
                
                # Debug: print top candidates
                print("Top 5 candidates:")
                for i, c in enumerate(candidates[:5]):
                    print(f"  {i+1}. '{c['text']}' (score: {c['score']:.1f}, korean: {c['has_korean']})")
                
                # Select the best candidate
                if candidates:
                    drug_name = candidates[0]['text']

            
            if drug_name:
                # Clean up the name
                drug_name = drug_name.strip().replace(":", "").strip()
                print(f"Extracted Drug Name: {drug_name}")
                return drug_name
            
            return None
            
        except Exception as e:
            print(f"Vision API OCR Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def extract_text_with_weights(image_bytes: bytes) -> list:
        """
        Extracts text from an image using Google Cloud Vision API (REST).
        Returns a list of tuples (text, weight) based on bounding box size.
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Create API request
            request_data = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [
                            {"type": "DOCUMENT_TEXT_DETECTION"}
                        ]
                    }
                ]
            }
            
            # Call Vision API
            response = requests.post(
                f"{GOOGLE_VISION_API_URL}?key={GOOGLE_API_KEY}",
                json=request_data
            )
            
            if response.status_code != 200:
                print(f"Vision API Error: {response.status_code}")
                print(response.text)
                return []
            
            result = response.json()
            
            # Extract text annotations
            responses = result.get("responses", [])
            if not responses or not responses[0].get("textAnnotations"):
                return []
            
            text_annotations = responses[0]["textAnnotations"]
            
            if len(text_annotations) <= 1:
                return []
            
            # Calculate weighted results based on bounding box area
            weighted_results = []
            max_area = 0
            
            for annotation in text_annotations[1:]:  # Skip first annotation (full text)
                vertices = annotation.get("boundingPoly", {}).get("vertices", [])
                if len(vertices) >= 4:
                    x_coords = [v.get("x", 0) for v in vertices]
                    y_coords = [v.get("y", 0) for v in vertices]
                    width = max(x_coords) - min(x_coords)
                    height = max(y_coords) - min(y_coords)
                    area = width * height
                    
                    if area > max_area:
                        max_area = area
                    
                    weighted_results.append({
                        'text': annotation.get("description", ""),
                        'area': area
                    })
            
            if max_area == 0:
                return []
            
            # Normalize weights
            final_results = [
                (res['text'], res['area'] / max_area)
                for res in weighted_results
            ]
            
            return final_results
            
        except Exception as e:
            print(f"Vision API Extract Error: {e}")
            import traceback
            traceback.print_exc()
            return []

class SearchService:
    @staticmethod
    def add_to_history(db: Session, drug_id: int, searched_text: str):
        """Adds a search result to the history."""
        history_entry = SearchHistory(
            drug_id=drug_id,
            searched_text=searched_text
        )
        db.add(history_entry)
        db.commit()

    @staticmethod
    def get_search_history(db: Session, limit: int = 20) -> list[dict]:
        """Gets the search history, most recent first."""
        history = db.query(SearchHistory).order_by(desc(SearchHistory.searched_at)).limit(limit).all()
        
        return [
            {
                "drug_name": item.drug.name,
                "searched_at": item.searched_at.strftime("%Y-%m-%d %H:%M")
            }
            for item in history
        ]

    @staticmethod
    def search_drug_by_single_name(db: Session, drug_name_query: str) -> tuple[dict | None, str | None]:
        """
        Searches for a drug using the name extracted by Vision API.
        """
        if not drug_name_query:
            return None, None

        from thefuzz import process, fuzz
        
        # Fetch all drug names
        all_drugs = db.query(DrugBasic.name, DrugBasic.id).all()
        drug_names = [d.name for d in all_drugs]
        drug_map = {d.name: d.id for d in all_drugs}
        
        if not drug_names:
            return None, None

        # Use thefuzz to find the best match
        best_match_name, score = process.extractOne(drug_name_query, drug_names, scorer=fuzz.token_sort_ratio)
        
        print(f"Vision Name: '{drug_name_query}', Best Match: '{best_match_name}', Score: {score}")
        
        if score >= 60:
            drug_id = drug_map[best_match_name]
            drug = db.query(DrugBasic).filter(DrugBasic.id == drug_id).first()
            return SearchService._format_drug_info(drug), drug_name_query
        
        return None, None

    @staticmethod
    def search_drug_weighted(db: Session, weighted_texts: list) -> tuple[dict | None, str | None]:
        """
        Searches for a drug using a list of weighted texts from OCR.
        """
        if not weighted_texts:
            return None, None

        from thefuzz import process, fuzz
        
        all_drugs = db.query(DrugBasic.name, DrugBasic.id).all()
        drug_names = [d.name for d in all_drugs]
        drug_map = {d.name: d.id for d in all_drugs}
        
        if not drug_names:
            return None, None

        best_match_name = None
        best_match_text = None
        best_overall_score = 0.0
        
        # Size weight factor
        SIZE_WEIGHT_FACTOR = 0.5
        
        # Keywords
        KEYWORDS = ["제품명", "품목명", "약품명", "명칭", "이름"]

        for i, (text, weight) in enumerate(weighted_texts):
            clean_text = text.strip()
            if len(clean_text) < 2:
                continue
            
            # Check if this text IS a keyword or CONTAINS a keyword
            for kw in KEYWORDS:
                if kw in clean_text:
                    if clean_text == kw and i + 1 < len(weighted_texts):
                        next_text, next_weight = weighted_texts[i+1]
                        weighted_texts[i+1] = (next_text, next_weight + 2.0) 
                    elif len(clean_text) > len(kw):
                        extracted = clean_text.replace(kw, "").replace(":", "").strip()
                        if len(extracted) > 1:
                            clean_text = extracted
                            weight += 2.0
                    break
            
            match, score = process.extractOne(clean_text, drug_names, scorer=fuzz.token_sort_ratio)
            adjusted_score = score * (1 + (weight * SIZE_WEIGHT_FACTOR))
            
            if adjusted_score > best_overall_score:
                best_overall_score = adjusted_score
                best_match_name = match
                best_match_text = clean_text
        
        print(f"Best Overall Match: '{best_match_name}' (Score: {best_overall_score:.2f})")
        
        if best_match_name and best_overall_score >= 70:
            drug_id = drug_map[best_match_name]
            drug = db.query(DrugBasic).filter(DrugBasic.id == drug_id).first()
            return SearchService._format_drug_info(drug), best_match_text
        
        return None, None

    @staticmethod
    def search_drug_by_name(db: Session, query: str) -> tuple[dict | None, str | None]:
        """
        Searches for a drug by a given text query.
        Returns the best match.
        """
        if not query or len(query.strip()) < 2:
            return None, None

        from thefuzz import process, fuzz

        # Fetch all drug names (optimized query)
        all_drugs = db.query(DrugBasic.name, DrugBasic.id).all()
        drug_names = [d.name for d in all_drugs]
        drug_map = {d.name: d.id for d in all_drugs}

        if not drug_names:
            return None, None
        
        # Use thefuzz to find the best match among ALL drugs
        best_match_name, score = process.extractOne(query, drug_names, scorer=fuzz.token_sort_ratio)

        print(f"Text Search: Query '{query}', Best Match: '{best_match_name}', Score: {score}")

        if score >= 60:
            drug_id = drug_map[best_match_name]
            drug = db.query(DrugBasic).filter(DrugBasic.id == drug_id).first()
            return SearchService._format_drug_info(drug), query

        return None, None

    @staticmethod
    def get_drugs_by_manufacturer(db: Session, manufacturer_name: str) -> list[dict]:
        """
        [Explicit JOIN Query]
        Retrieves all drugs for a given manufacturer using explicit SQL JOIN.
        This satisfies the project requirement for a JOIN query.
        """
        results = db.query(
            DrugBasic.id,
            DrugBasic.name,
            DrugBasic.storage,
            Manufacturer.name.label('manufacturer_name')
        ).join(
            Manufacturer, DrugBasic.manufacturer_id == Manufacturer.id
        ).filter(
            Manufacturer.name.ilike(f"%{manufacturer_name}%")
        ).all()
        
        return [
            {
                "id": r.id,
                "name": r.name,
                "storage": r.storage,
                "manufacturer": r.manufacturer_name
            }
            for r in results
        ]

    @staticmethod
    def get_manufacturer_statistics(db: Session) -> list[dict]:
        """
        [GROUP BY Aggregation Query]
        Returns statistics of drug count per manufacturer using GROUP BY.
        This satisfies the project requirement for an aggregation query.
        """
        results = db.query(
            Manufacturer.name,
            func.count(DrugBasic.id).label('drug_count')
        ).join(
            DrugBasic, Manufacturer.id == DrugBasic.manufacturer_id
        ).group_by(
            Manufacturer.id, Manufacturer.name
        ).order_by(
            func.count(DrugBasic.id).desc()
        ).limit(10).all()
        
        return [
            {
                "manufacturer": r.name,
                "drug_count": r.drug_count
            }
            for r in results
        ]

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


class ForeignMedicineService:
    """Service for handling foreign medicine alternatives using OpenAI."""
    
    @staticmethod
    def find_korean_alternatives(foreign_drug_text: str) -> list[str]:
        """
        Uses OpenAI GPT-4.1 mini to find Korean medicine alternatives.
        Returns a list of Korean drug names.
        """
        if not OPENAI_API_KEY:
            print("OpenAI API key not configured")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""You are a pharmaceutical expert. Given the following foreign medicine name or text from a medicine package, provide Korean medicine alternatives.

Foreign medicine text: "{foreign_drug_text}"

Instructions:
1. First, identify what this medicine is (active ingredient, purpose).
2. Find Korean medicines that can be used as alternatives.
3. Return ONLY a JSON array of Korean medicine names (in Korean), nothing else.
4. If you can't identify the medicine, return an empty array [].
5. Return at most 5 alternatives.

Example response format:
["타이레놀정", "게보린정", "이지엔6이브정"]

Response (JSON array only):"""

            data = {
                "model": "gpt-4.1-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 200
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"OpenAI API Error: {response.status_code}")
                print(response.text)
                return []
            
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Parse JSON array from response
            # Clean up the response in case it has extra text
            if '[' in content and ']' in content:
                json_start = content.index('[')
                json_end = content.rindex(']') + 1
                json_str = content[json_start:json_end]
                alternatives = json.loads(json_str)
                print(f"OpenAI found alternatives: {alternatives}")
                return alternatives
            
            return []
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def search_alternatives_in_db(names: list[str], db: Session) -> list[dict]:
        """
        Searches for the given drug names in the database using fuzzy matching.
        Returns a list of matching drugs with basic info.
        """
        from thefuzz import process, fuzz
        
        if not names:
            return []
        
        # Get all drugs from DB
        all_drugs = db.query(DrugBasic.name, DrugBasic.id).all()
        drug_names = [d.name for d in all_drugs]
        drug_map = {d.name: d.id for d in all_drugs}
        
        if not drug_names:
            return []
        
        results = []
        seen_ids = set()
        
        for name in names:
            # Find best match for each alternative name
            matches = process.extract(name, drug_names, scorer=fuzz.token_sort_ratio, limit=3)
            
            for match_name, score in matches:
                if score >= 50:  # Lower threshold for alternatives
                    drug_id = drug_map[match_name]
                    if drug_id not in seen_ids:
                        seen_ids.add(drug_id)
                        drug = db.query(DrugBasic).filter(DrugBasic.id == drug_id).first()
                        if drug:
                            results.append({
                                "id": drug.id,
                                "name": drug.name,
                                "manufacturer": drug.manufacturer.name if drug.manufacturer else "",
                                "match_score": score
                            })
        
        # Sort by match score
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:10]  # Return top 10
