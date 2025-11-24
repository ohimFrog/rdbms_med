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
    result = SearchService.search_drug(session, query_texts)
    if result:
        print(f"Found: {result['name']} (ID: {result['id']})")
    else:
        print("Not found")
    print("-" * 20)

if __name__ == "__main__":
    # Case 1: Exact match
    test_search(["활명수"])
    
    # Case 2: Partial match / Surrounded text
    test_search(["이 약은 활명수 입니다.", "효능효과: 소화불량"])
    
    # Case 3: Keyword usage
    test_search(["제품명: 활명수", "제조사: 동화약품"])
    
    # Case 4: Typo
    test_search(["활명슈"]) # Typo
    
    # Case 5: Multiple irrelevant texts
    test_search(["사용상 주의사항", "1. 다음 환자에는 투여하지 말 것", "활명수", "보관방법"])
