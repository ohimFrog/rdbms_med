# Medicine Info Translator - Presentation Script & Slides

## [Slide 1: Title Page]

- **Text:**
  - **Project Title:** Medicine Info Translator (의약품 정보 번역 및 제공 서비스)
  - **Team:** Group 4
  - **Presenter:** Taejun
- **Visual:**
  - 배경에 희미하게 약국이나 의약품 관련 이미지를 깔끔하게 배치.
  - 중앙에 프로젝트 로고 혹은 심플한 약 알약 아이콘과 돋보기 모양의 아이콘을 배치하여 "검색"과 "의약품"의 이미지를 강조.
  - 하단에 학교 로고나 강의명 배치 (옵션).

## [Slide 2: Outline]

- **Text:**
  1. Introduction
  2. DB Design & Modelling
  3. SQL Statements
  4. GUI Design
  5. Demo
  6. Lessons Learned
  7. Summary

## [Slide 3: Introduction - Problems & Goal]

- **Text:**
  - **Target User & Problem:**
    - 한국에 거주하는 외국인 또는 여행객.
    - 한국 의약품의 포장지나 설명서가 모두 한글로 되어 있어 이해하기 어려움.
    - "이 약이 내 증상에 맞는가?" 확인 불가능.
  - **Goal (Solution):**
    - 이미지(OCR) 또는 텍스트 검색을 통해 한국 의약품 정보를 영어 등 다국어로 번역 제공.
    - 증상별 약품 검색 및 복용법, 주의사항, 부작용 정보의 명확한 전달.
- **Visual:**
  - 외국인이 약국에서 곤란해하는 사진 vs 앱을 통해 정보를 확인하고 안도하는 사진 대조.

## [Slide 4: Introduction - Tech Stack & Architecture]

- **Text:**
  - **Language:** Python 3.9+
  - **Web Framework:** FastAPI (High performance, Easy API building)
  - **Database:** MySQL 8.0 (Relational Data Storage)
  - **ORM:** SQLAlchemy (Efficient DB handling)
  - **Frontend:** HTML5, CSS3, Vanilla JS
  - **External API:** Google Cloud Vision API (OCR), ChatGPT-4o mini (Translation & Foreign Pill Search)
- **Visual:**
  - **System Architecture Diagram:**
    - [Client (Browser)] <-> [FastAPI Server]
    - [FastAPI Server] <-> [MySQL Database]
    - [FastAPI Server] <-> [Google Vision API]
    - [FastAPI Server] <-> [OpenAI API]

## [Slide 5: DB Design - Data Acquisition]

- **Text:**
  - **Data Source:** 공공데이터포털 (식품의약품안전처\_의약품개요정보).
  - **Data Size:** 약 20,000+ 건의 의약폼 기본 정보 (CSV 포맷).
  - **Preprocessing (Pandas):**
    - `pd.read_csv('drug_data_full.csv')` 로 로드.
    - `.fillna("")` 로 결측치(NaN) 제거 및 빈 문자열 처리.
    - `.strip()` 으로 제조사명 등의 불필요한 공백 제거.
    - `itertuples()` 또는 `iterrows()`를 사용하여 정제된 데이터를 DB 객체로 변환.

## [Slide 6: DB Design - ER Diagram]

- **Text:**
  - **Key Tables:**
    1. **Manufacturer** (제조사 정보, 1:N)
    2. **DrugBasic** (의약품 기본 정보, Main Table)
    3. **DrugUsage** (효능 및 복용법, 1:1)
    4. **DrugWarning** (주의사항, 1:1)
    5. **DrugSideEffect** (부작용, 1:1)
    6. **SearchHistory** (검색 기록, 1:N)
- **Visual:**
  - **ER Diagram 이미지:** (Crow's Foot notation 권장)
    - `Manufacturer` --< `DrugBasic` (One Manufacturer checks many Drugs)
    - `DrugBasic` -- `DrugUsage` (One to One)
    - `DrugBasic` -- `DrugWarning` (One to One)
    - `DrugBasic` -- `DrugSideEffect` (One to One)
    - `DrugBasic` --< `SearchHistory` (One Drug appears in many Histories)

## [Slide 7: DB Design - Normalization (3NF)]

- **Text:**
  - **Applicaton of 3NF:**
    - **1NF:** 모든 컬럼은 원자값(Atomic Value)을 가짐. (리스트 형태 데이터 없음)
    - **2NF:** 모든 Non-key attribute가 Primary Key에 완전 함수 종속.
    - **3NF (Transitive Dependency Removal):**
      - 기존 데이터셋은 `Drug` 정보 안에 수많은 컬럼이 평면적(Flat)으로 존재.
      - **Before:** `Drug` 테이블 안에 `Manufacturer_Name`이 반복적으로 등장 -> 이행적 종속성 발생 가능.
      - **After:** `Manufacturer` 테이블을 분리하고 `manufacturer_id` (FK)로 참조.
      - `Usage`, `Warning` 등 성격이 다른 텍스트 데이터를 별도 테이블로 1:1 분리하여 관리 효율성 증대.

## [Slide 8: SQL Statements (1/2)]

- **Text:**
  - **Query 1: SELECT (Search Feature)**
    - 특정 이름을 포함하는 의약품 검색.
    ```sql
    SELECT id, name, storage
    FROM drug_basic
    WHERE name LIKE '%타이레놀%';
    ```
  - **Query 2: JOIN (Detail View)**
    - 의약품 상세 정보와 제조사 이름을 함께 조회.
    ```sql
    SELECT d.name, m.name as manufacturer, u.effect
    FROM drug_basic d
    JOIN manufacturer m ON d.manufacturer_id = m.id
    JOIN drug_usage u ON d.id = u.drug_id
    WHERE d.id = 101;
    ```

## [Slide 9: SQL Statements (2/2)]

- **Text:**
  - **Query 3: GROUP BY (Statistics)**
    - 제조사별 등록된 의약품 수 통계.
    ```sql
    SELECT m.name, COUNT(d.id) as drug_count
    FROM manufacturer m
    JOIN drug_basic d ON m.id = d.manufacturer_id
    GROUP BY m.name
    ORDER BY drug_count DESC
    LIMIT 5;
    ```
  - **Query 4: INSERT (History Logging)**
    - 사용자가 검색한 약품 기록 저장.
    ```sql
    INSERT INTO search_history (drug_id, searched_text, searched_at)
    VALUES (101, 'Tylenol', NOW());
    ```

## [Slide 10: GUI Design]

- **Text:**
  - **Web Interface:** 직관적인 Single Page Application (SPA) 스타일.
  - **User Flow:**
    1. 이미지 업로드 (Drag & Drop) 또는 텍스트 입력.
    2. 언어 선택 (영어, 일본어, 중국어 등).
    3. 결과 카드 출력 (약 이름, 제조사, 효능, 주의사항).
  - **Error Handling:**
    - OCR 실패 시: "텍스트 인식 실패, 직접 입력해주세요" 알림.
    - DB 검색 실패 시: "해당 약품 정보가 없습니다" (404 Error) 및 붉은색 경고 UI.
- **Visual:**
  - [Search Bar]와 [Upload Area]가 중앙에 위치한 메인 화면 스크린샷.
  - 번역된 결과가 깔끔하게 카드 형태로 보여지는 결과 화면 스크린샷.

## [Slide 11: Demo]

- **Text:**
  - **Application Demo Video / Live**
  - **Scenario:**
    1. **Input:** 한국어 약통 사진을 업로드.
    2. **Process:** OCR로 '게보린' 텍스트 추출 -> DB 검색 -> 영어로 번역.
    3. **Result:** 'Geworin'의 효능(두통 완화)과 복용법(성인 1일 3회)이 영어로 출력됨을 확인.
    4. **Extra:** 외국 약 검색 시 "대체 약품(Alternative)" 추천 기능 시연.

## [Slide 12: Lessons Learned]

- **Text:**
  - **Challenges & Solutions:**
    1. **OCR 정확도 문제:** 조명이나 각도에 따라 인식률 저하 -> **Google Cloud Vision API** 도입으로 해결.
    2. **데이터 정규화:** 초기 단일 테이블 구조에서 데이터 중복 발생 -> **ERD 재설계 및 테이블 분리(3NF)**로 해결.
    3. **인코딩 문제:** 한글 데이터의 특수문자 깨짐 -> **UTF-8 mb4** 설정 및 Pandas 전처리 강화.
  - **Timeline:**
    - Week 1: 주제 선정 및 요구사항 분석
    - Week 2: DB 스키마 설계 및 데이터 수집/정제
    - Week 3: Backend API (FastAPI) 구현 & SQL 작성
    - Week 4: Frontend UI 연동 및 테스트/버그 수정

## [Slide 13: Summary]

- **Text:**
  - **Conclusion:**
    - 외로운 타지 생활, 아플 때 가장 필요한 정보 제공.
    - 데이터베이스 기술을 활용하여 실생활의 문제를 해결한 유의미한 프로젝트.
  - **Future Work:**
    - 약국 위치 지도 연동 (Map API).
    - 유저 리뷰 기능 고도화.
  - **Q & A**
