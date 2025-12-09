# Medicine Info Translator - Presentation Slides Content

> **Group 4** | Presenter: Taejun | DBMS Final Project

---

## [Slide 1: Title Page]

### Text

```
💊 Medicine Info Translator
의약품 정보 번역 및 제공 서비스

Group 4
Presenter: Taejun

DBMS Final Project - 2024
```

### Visual

- 💊 아이콘과 함께 프로젝트 로고
- 배경: 약 패키지 이미지 또는 의료 관련 그래픽
- 색상: 다크 테마 (#0f0f23) + 그라데이션 악센트

---

## [Slide 2: Outline]

### Text

```
📋 Presentation Outline

1. Introduction........................3-4
2. DB Design & Modelling................5-7
3. SQL Statements......................8-9
4. GUI Design..........................10
5. Live Demo...........................11
6. Lessons Learned.....................12
7. Summary & Q&A.......................13
```

### Visual

- 아이콘이 포함된 수직 또는 수평 타임라인 형식
- 각 섹션을 색상으로 구분

---

## [Slide 3: Introduction - Problem & Goal]

### Text

```
🎯 Problem Statement

Target Users:
• 한국에 거주하는 외국인 (Foreigners in Korea)
• 의약품 라벨을 읽기 어려운 관광객

Problem:
• Korean drug labels are difficult to understand
• No centralized translation service exists
• Risk of misuse due to language barriers

Goal:
• Provide instant, accurate drug information
• Multi-language translation support
• Easy-to-use image/text search interface
```

### Visual

- 외국인이 약국에서 약을 들고 있는 이미지
- 한국어 약 라벨 → 번역된 정보 흐름 다이어그램

---

## [Slide 4: Introduction - Tech Stack]

### Text

```
🛠️ Technology Stack

Backend:
• Python 3.x (Core Language)
• FastAPI (Web Framework)
• SQLAlchemy ORM (Database Access)
• MySQL (Relational Database)

Frontend:
• HTML5, CSS3, JavaScript
• Responsive Web Design

AI/ML Services:
• Google Cloud Vision API (OCR)
• OpenAI GPT-4.1 mini (Foreign Med Alternatives)
• Google Translate API (Multi-language Support)

Data Processing:
• Pandas (Data Cleaning & Import)
• thefuzz (Fuzzy String Matching)
```

### Visual

```
┌──────────────────────────────────────────────────────────┐
│                      System Architecture                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│    ┌─────────┐     ┌──────────┐     ┌─────────────┐     │
│    │ Browser │────▶│ FastAPI  │────▶│   MySQL     │     │
│    │  (Web)  │◀────│  Server  │◀────│  Database   │     │
│    └─────────┘     └────┬─────┘     └─────────────┘     │
│                         │                                │
│         ┌───────────────┼───────────────┐               │
│         ▼               ▼               ▼               │
│   ┌──────────┐   ┌──────────┐   ┌──────────────┐       │
│   │Google    │   │OpenAI    │   │Google        │       │
│   │Vision OCR│   │GPT-4.1   │   │Translate API │       │
│   └──────────┘   └──────────┘   └──────────────┘       │
└──────────────────────────────────────────────────────────┘
```

---

## [Slide 5: DB Design - Data Acquisition]

### Text

```
📥 Data Acquisition

Source:
• Korean pharmaceutical dataset (drug_data_full.csv)
• Size: ~10MB, multiple drug records

Original Data Fields:
• pname (Product Name)
• cname (Company/Manufacturer Name)
• effect (효능)
• dosage (용법용량)
• dprecaution (주의사항)
• interaction (상호작용)
• side_effect (부작용)
• storage (보관방법)
```

### Visual

- CSV 파일 → 데이터베이스 흐름 다이어그램
- 원본 데이터 스니펫 예시

---

## [Slide 6: DB Design - Data Processing & Normalization]

### Text

```
🧹 Data Cleaning with Pandas

import pandas as pd

# 1. Read CSV
df = pd.read_csv("drug_data_full.csv")

# 2. Handle missing values
df = df.fillna("")

# 3. Process and import
for _, row in df.iterrows():
    manufacturer = get_or_create(row['cname'])
    drug = DrugBasic(name=row['pname'], ...)
    ...

────────────────────────────────────────

📐 3NF Normalization Applied

Before (1NF Issues):
• All data in single flat table
• Manufacturer name repeated for every drug
• Multiple side effects in single column

After (3NF):
✅ No transitive dependencies
✅ Manufacturer separated into own table
✅ Drug details split by category (Usage, Warning, SideEffect)
```

### Visual

- Before/After 테이블 비교
- 정규화 흐름도

---

## [Slide 7: DB Design - ER Diagram]

### Text

```
📊 Entity-Relationship Diagram

6 Tables with Clear Relationships:

• manufacturer (1) ────< (N) drug_basic
• drug_basic (1) ────── (1) drug_usage
• drug_basic (1) ────── (1) drug_warning
• drug_basic (1) ────── (1) drug_side_effect
• drug_basic (1) ────< (N) search_history
```

### Visual - ER Diagram

```
┌───────────────────┐
│   manufacturer    │
├───────────────────┤        ┌───────────────────┐
│ PK id            │───┐    │   drug_usage      │
│    name          │   │    ├───────────────────┤
└───────────────────┘   │    │ PK id            │
                        │    │ FK drug_id       │──┐
                        │    │    effect        │  │
                        │    │    dosage        │  │
                        │    └───────────────────┘  │
┌───────────────────┐   │                          │
│   drug_basic      │◀──┘    ┌───────────────────┐  │
├───────────────────┤        │   drug_warning    │  │
│ PK id            │◀────────┤ PK id            │◀─┤
│ FK manufacturer_id│        │ FK drug_id       │  │
│    name          │         │    precaution    │  │
│    storage       │         │    interaction   │  │
└───────────────────┘        └───────────────────┘  │
        │                                          │
        │            ┌────────────────────┐       │
        │            │  drug_side_effect  │       │
        │            ├────────────────────┤       │
        │            │ PK id             │◀───────┘
        │            │ FK drug_id        │
        │            │    side_effect    │
        │            └────────────────────┘
        │
        ▼
┌───────────────────┐
│  search_history   │
├───────────────────┤
│ PK id            │
│ FK drug_id       │
│    searched_text │
│    searched_at   │
└───────────────────┘
```

---

## [Slide 8: SQL Statements - SELECT & JOIN]

### Text

```
🔍 SELECT Query - Drug Search by Name

# Using fuzzy matching with thefuzz library
all_drugs = db.query(DrugBasic.name, DrugBasic.id).all()
best_match_name, score = process.extractOne(
    query, drug_names, scorer=fuzz.token_sort_ratio
)
if score >= 60:
    drug = db.query(DrugBasic).filter(
        DrugBasic.id == drug_id
    ).first()

────────────────────────────────────────

🔗 JOIN Query - Get Drugs by Manufacturer

results = db.query(
    DrugBasic.id,
    DrugBasic.name,
    DrugBasic.storage,
    Manufacturer.name.label('manufacturer_name')
).join(
    Manufacturer,
    DrugBasic.manufacturer_id == Manufacturer.id
).filter(
    Manufacturer.name.ilike(f"%{manufacturer_name}%")
).all()
```

### Visual

- 쿼리 결과 샘플 테이블
- JOIN 관계 다이어그램

---

## [Slide 9: SQL Statements - GROUP BY & INSERT]

### Text

```
📊 GROUP BY Query - Manufacturer Statistics

results = db.query(
    Manufacturer.name,
    func.count(DrugBasic.id).label('drug_count')
).join(
    DrugBasic,
    Manufacturer.id == DrugBasic.manufacturer_id
).group_by(
    Manufacturer.id, Manufacturer.name
).order_by(
    func.count(DrugBasic.id).desc()
).limit(10).all()

# Result Example:
# | manufacturer        | drug_count |
# |---------------------|------------|
# | 대웅제약            | 245        |
# | 한미약품            | 189        |
# | 유한양행            | 156        |

────────────────────────────────────────

➕ INSERT Query - Add Search History

history_entry = SearchHistory(
    drug_id=drug_id,
    searched_text=searched_text
)
db.add(history_entry)
db.commit()
```

### Visual

- GROUP BY 결과를 보여주는 막대 그래프
- INSERT 전/후 테이블 상태

---

## [Slide 10: GUI Design]

### Text

```
🖥️ User Interface Overview

Flow:
1. Language Selection → 2. Upload/Search → 3. View Results

Key Features:
• Multi-language support (13+ languages)
• Drag & Drop image upload
• Text-based search option
• Responsive dark theme design

Error Handling:
• Image upload validation
• "No matching drug found" message
• Foreign medicine alternative suggestions
• Loading states with spinners

Components:
• Header with Stats & History buttons
• Language selection grid
• Drop zone for image upload
• Search input field
• Result cards with drug details
```

### Visual - UI Wireframe

```
┌──────────────────────────────────────────┐
│  💊 Medicine Info Translator    [Stats][History] │
├──────────────────────────────────────────┤
│                                          │
│        Choose Your Language              │
│   ┌────┐ ┌────┐ ┌────┐ ┌────┐           │
│   │ EN │ │ CN │ │ JP │ │ VN │ ...       │
│   └────┘ └────┘ └────┘ └────┘           │
│                                          │
│      ┌─────────────────────────┐        │
│      │   📸 Drag & Drop or     │        │
│      │   Click to Upload       │        │
│      └─────────────────────────┘        │
│              ── OR ──                    │
│      [Enter drug name...] [Search]      │
│                                          │
└──────────────────────────────────────────┘
```

---

## [Slide 11: GUI Demo]

### Text

```
🎬 Live Application Demo

Demo Scenarios:

1️⃣ Image Upload Flow
   • Upload Korean medicine photo
   • OCR extracts text → DB search
   • Display translated results

2️⃣ Text Search Flow
   • Enter Korean drug name (e.g., "타이레놀")
   • Fuzzy matching finds best result
   • Show effect, dosage, precautions

3️⃣ Statistics & History
   • View manufacturer statistics (GROUP BY)
   • Click to see drugs by manufacturer (JOIN)
   • Check search history
```

### Note for Presenter

- 실제 앱 URL: http://localhost:8000
- 시연할 약: 타이레놀, 게보린, 부루펜
- 이미지 업로드 테스트 준비
- 통계 페이지 접근 시연

---

## [Slide 12: Lessons Learned]

### Text

```
📚 Lessons Learned

Challenges Faced:

1. Data Model Evolution
   • Initially: single flat table
   • Changed to: normalized 6-table structure
   • Reason: better query performance, data integrity

2. OCR Accuracy Issues
   • Problem: Korean text extraction errors
   • Solution: Switched to Google Cloud Vision API
   • Added weighted text extraction fallback

3. Foreign Medicine Handling
   • Challenge: Non-Korean medicines not in DB
   • Solution: OpenAI integration for alternatives

4. Character Encoding
   • UTF-8 consistency across CSV, DB, and API

────────────────────────────────────────

📅 Development Timeline

Week 1-2: Data collection & cleaning
Week 3:   Database design & normalization
Week 4:   Core API development
Week 5:   OCR & Translation integration
Week 6:   UI development & testing
Week 7:   Final testing & presentation prep
```

### Visual

- 타임라인 다이어그램 (가로 화살표 형식)
- 각 주요 마일스톤에 아이콘 추가

---

## [Slide 13: Summary & Q&A]

### Text

```
✨ Summary

What We Built:
✅ Medicine information translator for foreigners
✅ Image-based and text-based search
✅ Multi-language support (13+ languages)
✅ Foreign medicine alternatives feature

Technical Achievements:
✅ 6-table normalized database (3NF)
✅ Full CRUD operations with SQLAlchemy
✅ REST API with FastAPI
✅ AI integration (Vision OCR, OpenAI, Translation)

Key SQL Features:
✅ SELECT with fuzzy matching
✅ JOIN for manufacturer-drug relationships
✅ GROUP BY for statistics aggregation
✅ INSERT for search history tracking

────────────────────────────────────────

🙋 Questions & Answers

Thank you for listening!

GitHub: github.com/[repository]
```

### Visual

- 체크마크가 있는 요약 박스
- QR 코드 (GitHub 저장소 링크용)
- 팀 연락처 정보

---

## Appendix: Speaker Notes

### Slide 1 (30초)

"안녕하세요, Group 4의 Taejun입니다. 오늘 Medicine Info Translator 프로젝트를 발표하겠습니다."

### Slide 3-4 (2분)

"저희 프로젝트의 타겟 사용자는 한국에 거주하는 외국인입니다. 한국어 약 라벨을 읽기 어려운 분들을 위해 이미지 업로드나 텍스트 검색으로 번역된 약 정보를 제공합니다."

### Slide 5-7 (4분)

"데이터는 한국 의약품 데이터셋에서 수집했고, Pandas를 사용해 정제했습니다. 정규화를 통해 6개 테이블로 분리했으며, ER 다이어그램에서 볼 수 있듯이 manufacturer, drug_basic, drug_usage, drug_warning, drug_side_effect, search_history 테이블이 있습니다."

### Slide 8-9 (3분)

"프로젝트에서 사용한 SQL 쿼리 4가지를 보여드리겠습니다. SELECT는 fuzzy matching을 사용한 약 검색, JOIN은 제조사별 약품 조회, GROUP BY는 제조사별 약품 수 통계, INSERT는 검색 기록 저장에 사용됩니다."

### Slide 10-11 (3분)

"GUI는 웹 기반으로 구현했습니다. 언어 선택, 이미지 업로드, 결과 표시의 3단계 흐름입니다. 이제 실제 데모를 보여드리겠습니다."

### Slide 12 (2분)

"개발 중 직면한 주요 과제는 데이터 모델 변경, OCR 정확도 문제, 외국 약품 처리였습니다. 각각 정규화, Google Vision API, OpenAI 통합으로 해결했습니다."

### Slide 13 (30초)

"요약하면, 저희는 외국인을 위한 의약품 정보 번역 서비스를 구축했고, 정규화된 데이터베이스, REST API, AI 통합을 구현했습니다. 질문 있으시면 말씀해주세요."
