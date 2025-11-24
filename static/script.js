document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const langSelect = document.getElementById('langSelect');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const imagePreview = document.getElementById('imagePreview');

    let selectedFile = null;

    // Translations
    const translations = {
        "en": {
            "appTitle": "💊 Medicine Info Translator",
            "appDesc": "Upload a photo of your Korean medicine to get translated information.",
            "dropZoneText": "Drag & Drop or Click to Upload",
            "translateTo": "Translate to:",
            "analyzeBtn": "Analyze Medicine",
            "analyzing": "Analyzing image and searching database...",
            "effectLabel": "📋 Effect & Efficacy",
            "dosageLabel": "💊 Dosage & Usage",
            "precautionLabel": "⚠️ Precautions",
            "sideEffectLabel": "❌ Side Effects",
            "storageLabel": "📦 Storage"
        },
        "ko": {
            "appTitle": "💊 약품 정보 번역기",
            "appDesc": "한국 약품 사진을 업로드하여 번역된 정보를 확인하세요.",
            "dropZoneText": "클릭하거나 파일을 드래그하여 업로드",
            "translateTo": "번역 언어:",
            "analyzeBtn": "약품 분석하기",
            "analyzing": "이미지 분석 및 데이터베이스 검색 중...",
            "effectLabel": "📋 효능 및 효과",
            "dosageLabel": "💊 용법 및 용량",
            "precautionLabel": "⚠️ 주의사항",
            "sideEffectLabel": "❌ 부작용",
            "storageLabel": "📦 보관 방법"
        },
        "zh-CN": {
            "appTitle": "💊 药品信息翻译器",
            "appDesc": "上传您的韩国药品照片以获取翻译信息。",
            "dropZoneText": "拖放或点击上传",
            "translateTo": "翻译成：",
            "analyzeBtn": "分析药品",
            "analyzing": "正在分析图像并搜索数据库...",
            "effectLabel": "📋 功效与作用",
            "dosageLabel": "💊 用法与用量",
            "precautionLabel": "⚠️ 注意事项",
            "sideEffectLabel": "❌ 副作用",
            "storageLabel": "📦 储存方法"
        },
        "de": {
            "appTitle": "💊 Medikamenten-Info-Übersetzer",
            "appDesc": "Laden Sie ein Foto Ihres koreanischen Medikaments hoch, um übersetzte Informationen zu erhalten.",
            "dropZoneText": "Ziehen & Ablegen oder Klicken zum Hochladen",
            "translateTo": "Übersetzen nach:",
            "analyzeBtn": "Medikament analysieren",
            "analyzing": "Bild wird analysiert und Datenbank durchsucht...",
            "effectLabel": "📋 Wirkung & Wirksamkeit",
            "dosageLabel": "💊 Dosierung & Anwendung",
            "precautionLabel": "⚠️ Vorsichtsmaßnahmen",
            "sideEffectLabel": "❌ Nebenwirkungen",
            "storageLabel": "📦 Lagerung"
        },
        "ca": {
            "appTitle": "💊 Traductor d'Informació de Medicaments",
            "appDesc": "Pugeu una foto del vostre medicament coreà per obtenir informació traduïda.",
            "dropZoneText": "Arrossegueu i deixeu anar o feu clic per pujar",
            "translateTo": "Traduir a:",
            "analyzeBtn": "Analitzar Medicament",
            "analyzing": "Analitzant imatge i cercant a la base de dades...",
            "effectLabel": "📋 Efecte i Eficàcia",
            "dosageLabel": "💊 Dosi i Ús",
            "precautionLabel": "⚠️ Precaucions",
            "sideEffectLabel": "❌ Efectes Secundaris",
            "storageLabel": "📦 Emmagatzematge"
        }
    };

    function updateUIText(lang) {
        const t = translations[lang] || translations['en'];
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (t[key]) {
                element.textContent = t[key];
            }
        });
    }

    // Initial translation
    updateUIText(langSelect.value);

    langSelect.addEventListener('change', (e) => {
        updateUIText(e.target.value);
    });

    // Drag & Drop
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }
        selectedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreview.classList.remove('hidden');
            dropZone.querySelector('.icon').classList.add('hidden');
            dropZone.querySelector('p').classList.add('hidden');
        };
        reader.readAsDataURL(file);

        uploadBtn.disabled = false;
        result.classList.add('hidden');
        errorDiv.classList.add('hidden');
    }

    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        loading.classList.remove('hidden');
        result.classList.add('hidden');
        errorDiv.classList.add('hidden');
        uploadBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('lang', langSelect.value);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to process image');
            }

            displayResult(data);
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
            uploadBtn.disabled = false;
        }
    });

    function displayResult(data) {
        document.getElementById('drugName').textContent = data.name;
        document.getElementById('manufacturer').textContent = data.manufacturer;
        document.getElementById('drugEffect').textContent = data.effect || 'No information available';
        document.getElementById('drugDosage').textContent = data.dosage || 'No information available';
        document.getElementById('drugPrecaution').textContent = data.precaution || 'No information available';
        document.getElementById('drugSideEffect').textContent = data.side_effect || 'No information available';
        document.getElementById('drugStorage').textContent = data.storage || 'No information available';

        result.classList.remove('hidden');
    }
});
