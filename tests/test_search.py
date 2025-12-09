from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services import SearchService
from models import DrugBasic
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

def test_search(query_texts):
    print(f"Testing with query: {query_texts}")
    result, match_text = SearchService.search_drug(session, query_texts)
    if result:
        print(f"Found: {result['name']} (ID: {result['id']}) from text '{match_text}'")
    else:
        print("Not found")
    print("-" * 20)

if __name__ == "__main__":
    # Case 1: Exact match
    # Simulate weighted texts from OCR
    # (text, weight)
    weighted_texts = [("활명수", 1.0)]
    test_search(weighted_texts)
    
    # Case 2: Partial match / Surrounded text
    test_search([("이 약은 활명수 입니다.", 0.8), ("효능효과: 소화불량", 0.5)])
    
    # Case 3: Keyword usage
    test_search([("제품명: 활명수", 0.9), ("제조사: 동화약품", 0.6)])
    
    # Case 4: Typo
    test_search([("활명슈", 0.9)]) # Typo
    
    # Case 5: Multiple irrelevant texts
    test_search([("사용상 주의사항", 0.5), ("1. 다음 환자에는 투여하지 말 것", 0.5), ("활명수", 0.8), ("보관방법", 0.5)])

    # Case 6: Text Search with Typo (New Feature)
    print("Testing Text Search with Typo: '활명슈'")
    result, match_text = SearchService.search_drug_by_name(session, "활명슈")
    if result:
        print(f"Found: {result['name']} (ID: {result['id']}) from query '{match_text}'")
    else:
        print("Not found")
    print("-" * 20)
