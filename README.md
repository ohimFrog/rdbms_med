# 💊 Medicine Info Translator

A web application that translates Korean medicine information into multiple languages.

## 📋 Key Features

- 🤖 **Hybrid OCR**: Google Gemini API (primary) + EasyOCR (fallback) dual system
- 🔍 **Text Search**: Direct drug name search with Fuzzy Matching
- 🌐 **Multi-language Translation**: Korean, English, Chinese, German, Catalan support
- 📚 **Search History**: Client-side localStorage-based history (max 20 items)
- 🎨 **Premium Design**: Dark mode glassmorphism UI

## 🚀 Getting Started

### 1. Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure .env file
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/rdbms_med
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Database Initialization

```bash
# Create database
python scripts/create_db.py

# Create tables and load data
python scripts/init_db.py
```

### 3. Run Server

```bash
uvicorn main:app --reload --port 8000
```

Access `http://localhost:8000` in your browser

## 📁 Project Structure

```
rdbms_med/
├── main.py              # FastAPI main application
├── models.py            # SQLAlchemy database models
├── services.py          # OCR, search, translation services
├── requirements.txt     # Python package dependencies
├── .env                 # Environment variables
│
├── static/              # Web frontend
│   ├── index.html       # Main HTML
│   ├── style.css        # Dark mode design
│   └── script.js        # Client logic
│
├── scripts/             # Utility scripts
│   ├── create_db.py     # Database creation
│   ├── init_db.py       # Table creation and data loading
│   └── inspect_db.py    # DB inspection
│
├── tests/               # Test files
│   ├── test_gemini.py
│   ├── test_search.py
│   └── create_test_image.py
│
├── data/                # Drug data CSV files
└── rdbms/               # Legacy data folder
```

## 🗄️ Database Schema

### Table Structure

#### 1. `manufacturer` - Manufacturer Information
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| name | VARCHAR(255) | Manufacturer name (Unique) |

#### 2. `drug_basic` - Basic Drug Information
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| name | TEXT | Drug name |
| manufacturer_id | INTEGER | Foreign Key → manufacturer.id |
| storage | TEXT | Storage method |

#### 3. `drug_usage` - Efficacy and Dosage
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| drug_id | INTEGER | Foreign Key → drug_basic.id (Unique) |
| effect | TEXT | Effect and efficacy |
| dosage | TEXT | Dosage and usage |

#### 4. `drug_warning` - Precautions
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| drug_id | INTEGER | Foreign Key → drug_basic.id (Unique) |
| precaution | TEXT | Precautions |
| interaction | TEXT | Drug interactions |

#### 5. `drug_side_effect` - Side Effects
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| drug_id | INTEGER | Foreign Key → drug_basic.id (Unique) |
| side_effect | TEXT | Side effect information |

#### 6. `search_history` - Search History
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key (Auto Increment) |
| drug_id | INTEGER | Foreign Key → drug_basic.id |
| searched_text | TEXT | Search query (Nullable) |
| searched_at | TIMESTAMP | Search timestamp (Default: NOW()) |

### ER Diagram Relationships
- `manufacturer` 1:N `drug_basic`
- `drug_basic` 1:1 `drug_usage`
- `drug_basic` 1:1 `drug_warning`
- `drug_basic` 1:1 `drug_side_effect`
- `drug_basic` 1:N `search_history`

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **PyMySQL**: MySQL driver
- **Google Gemini API**: Primary OCR engine
- **EasyOCR**: Fallback OCR engine
- **OpenCV**: Image preprocessing
- **thefuzz**: Fuzzy String Matching
- **deep-translator**: Translation service

### Frontend
- **HTML5 + CSS3 + Vanilla JS**
- **Inter Font**: Typography
- **Glassmorphism**: Design style
- **localStorage**: Client-side history storage

## API Endpoints

- `GET /` - Main page
- `POST /upload` - Image upload and OCR processing
  - Form Data: `file` (image), `lang` (language code)
  - Response: Drug information JSON
- `POST /search` - Text search
  - JSON Body: `{"query": "drug_name", "lang": "language_code"}`
  - Response: Drug information JSON
- `GET /history` - Server-side search history (currently unused)

## OCR System

### Hybrid OCR Architecture
1. **Primary**: Google Gemini API
   - High accuracy drug name extraction
   - Potential API rate limits
2. **Fallback**: EasyOCR
   - Image preprocessing (Upscaling, Denoising)
   - Keyword detection ("제품명", "성분", etc.)
   - Text position-based weight calculation

### Search Algorithm
- **Fuzzy Matching**: Using thefuzz library
- **Token Sort Ratio**: Matching ignoring token order
- **Threshold**: Score ≥ 60 for successful matching

## Design Features

- Dark mode-based UI
- Glassmorphism effects
- Smooth animations
- Fully responsive design
- Gradient buttons and text
- Fixed position History button

## 👥 Development Team

Group 4 - RDBMS Project

## 📄 License

Educational Project

---

## 🌐 Languages

- [한국어 README](README.md)
- [English README](README_EN.md) (Current)
