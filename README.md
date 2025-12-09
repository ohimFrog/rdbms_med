# 💊 Medicine Info Translator

한국 약품 정보를 다국어로 번역해주는 웹 애플리케이션입니다.

## 📋 주요 기능

- 🤖 **Hybrid OCR**: Google Gemini API (primary) + EasyOCR (fallback) 이중 시스템
- 🔍 **텍스트 검색**: 약품명 직접 검색 기능 (Fuzzy Matching)
- 🌐 **다국어 번역**: 한국어, 영어, 중국어, 독일어, 카탈란어 지원
- � **검색 기록**: localStorage 기반 클라이언트 측 히스토리 (최대 20개)
- 🎨 **프리미엄 디자인**: 다크 모드 기반 글래스모피즘 UI

## 🚀 시작하기

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# .env 파일 설정
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/rdbms_med
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. 데이터베이스 초기화

```bash
# DB 생성
python scripts/create_db.py

# 테이블 생성 및 데이터 로드
python scripts/init_db.py
```

### 3. 서버 실행

```bash
uvicorn main:app --reload --port 8000
```

브라우저에서 `http://localhost:8000` 접속

## 📁 프로젝트 구조

```
rdbms_med/
├── main.py              # FastAPI 메인 애플리케이션
├── models.py            # SQLAlchemy 데이터베이스 모델
├── services.py          # OCR, 검색, 번역 서비스
├── requirements.txt     # Python 패키지 의존성
├── .env                 # 환경 변수 설정
│
├── static/              # 웹 프론트엔드
│   ├── index.html       # 메인 HTML
│   ├── style.css        # 다크 모드 디자인
│   └── script.js        # 클라이언트 로직
│
├── scripts/             # 유틸리티 스크립트
│   ├── create_db.py     # 데이터베이스 생성
│   ├── init_db.py       # 테이블 생성 및 데이터 로드
│   └── inspect_db.py    # DB 내용 확인
│
├── tests/               # 테스트 파일
│   ├── test_gemini.py
│   ├── test_search.py
│   └── create_test_image.py
│
├── data/                # 약품 데이터 CSV
└── rdbms/               # Legacy 데이터 폴더
```

## 🗄️ 데이터베이스 스키마

### 테이블 구조

#### 1. `manufacturer` - 제조사 정보

| 컬럼 | 타입         | 설명                         |
| ---- | ------------ | ---------------------------- |
| id   | INTEGER      | Primary Key (Auto Increment) |
| name | VARCHAR(255) | 제조사명 (Unique)            |

#### 2. `drug_basic` - 약품 기본 정보

| 컬럼            | 타입    | 설명                          |
| --------------- | ------- | ----------------------------- |
| id              | INTEGER | Primary Key (Auto Increment)  |
| name            | TEXT    | 약품명                        |
| manufacturer_id | INTEGER | Foreign Key → manufacturer.id |
| storage         | TEXT    | 보관 방법                     |

#### 3. `drug_usage` - 효능 및 용법

| 컬럼    | 타입    | 설명                                 |
| ------- | ------- | ------------------------------------ |
| id      | INTEGER | Primary Key (Auto Increment)         |
| drug_id | INTEGER | Foreign Key → drug_basic.id (Unique) |
| effect  | TEXT    | 효능 및 효과                         |
| dosage  | TEXT    | 용법 및 용량                         |

#### 4. `drug_warning` - 주의사항

| 컬럼        | 타입    | 설명                                 |
| ----------- | ------- | ------------------------------------ |
| id          | INTEGER | Primary Key (Auto Increment)         |
| drug_id     | INTEGER | Foreign Key → drug_basic.id (Unique) |
| precaution  | TEXT    | 주의사항                             |
| interaction | TEXT    | 약물 상호작용                        |

#### 5. `drug_side_effect` - 부작용

| 컬럼        | 타입    | 설명                                 |
| ----------- | ------- | ------------------------------------ |
| id          | INTEGER | Primary Key (Auto Increment)         |
| drug_id     | INTEGER | Foreign Key → drug_basic.id (Unique) |
| side_effect | TEXT    | 부작용 정보                          |

#### 6. `search_history` - 검색 기록

| 컬럼          | 타입      | 설명                         |
| ------------- | --------- | ---------------------------- |
| id            | INTEGER   | Primary Key (Auto Increment) |
| drug_id       | INTEGER   | Foreign Key → drug_basic.id  |
| searched_text | TEXT      | 검색어 (Nullable)            |
| searched_at   | TIMESTAMP | 검색 시각 (Default: NOW())   |

### ER 다이어그램 관계

- `manufacturer` 1:N `drug_basic`
- `drug_basic` 1:1 `drug_usage`
- `drug_basic` 1:1 `drug_warning`
- `drug_basic` 1:1 `drug_side_effect`
- `drug_basic` 1:N `search_history`

## 🛠️ 기술 스택

### Backend

- **FastAPI**: 웹 프레임워크
- **SQLAlchemy**: ORM
- **PyMySQL**: MySQL 드라이버
- **Google Gemini API**: 주요 OCR 엔진
- **EasyOCR**: Fallback OCR 엔진
- **OpenCV**: 이미지 전처리
- **thefuzz**: Fuzzy String Matching
- **deep-translator**: 번역 서비스

### Frontend

- **HTML5 + CSS3 + Vanilla JS**
- **Inter Font**: 타이포그래피
- **Glassmorphism**: 디자인 스타일
- **localStorage**: 클라이언트 측 히스토리 저장

## 📝 API 엔드포인트

- `GET /` - 메인 페이지
- `POST /upload` - 이미지 업로드 및 OCR 처리
  - Form Data: `file` (이미지), `lang` (언어 코드)
  - Response: 약품 정보 JSON
- `POST /search` - 텍스트 검색
  - JSON Body: `{"query": "약품명", "lang": "언어코드"}`
  - Response: 약품 정보 JSON
- `GET /history` - 서버 측 검색 기록 조회 (현재 미사용)

## 🔍 OCR 시스템

### Hybrid OCR Architecture

1. **Primary**: Google Gemini API
   - 높은 정확도의 약품명 추출
   - API Rate Limit 가능성
2. **Fallback**: EasyOCR
   - 이미지 전처리 (Upscaling, Denoising)
   - 키워드 감지 ("제품명", "성분" 등)
   - 텍스트 위치 기반 가중치 계산

### Search Algorithm

- **Fuzzy Matching**: thefuzz 라이브러리 사용
- **Token Sort Ratio**: 토큰 순서 무시한 매칭
- **Threshold**: Score ≥ 60 이상 매칭 성공

## 🎨 디자인 특징

- 다크 모드 기반 UI
- 글래스모피즘 효과
- 부드러운 애니메이션
- 완전한 반응형 디자인
- 그라디언트 버튼 및 텍스트
- Fixed Position History 버튼

## 👥 개발팀

Group 4 - RDBMS 프로젝트

## 📄 라이선스

Educational Project

---

## 🌐 언어 / Languages

- [한국어 README](README.md) (현재)
- [English README](README_EN.md)
