document.addEventListener('DOMContentLoaded', () => {
    // State
    let selectedFile = null;
    let selectedLang = null;

    // Views
    const views = {
        langSelect: document.getElementById('language-selection-view'),
        upload: document.getElementById('upload-view'),
        result: document.getElementById('result-view'),
        history: document.getElementById('history-view'),
        statistics: document.getElementById('statistics-view'),
        manufacturerDrugs: document.getElementById('manufacturer-drugs-view'),
        alternatives: document.getElementById('alternatives-view')
    };

    // Elements
    const languageGrid = document.getElementById('language-grid');
    const backToLangBtn = document.getElementById('back-to-lang');
    const startOverBtn = document.getElementById('start-over');

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const imagePreview = document.getElementById('imagePreview');
    const textSearchInput = document.getElementById('textSearchInput');
    const textSearchBtn = document.getElementById('textSearchBtn');

    const loading = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');

    // Translations Data
    const translations = {
        "en": { "name": "English", "appTitle": "💊 Medicine Info Translator", "appDesc": "Upload a photo of your Korean medicine to get translated information.", "languageTitle": "Choose Your Language", "backBtn": "Back", "startOverBtn": "Start Over", "dropZoneText": "Drag & Drop or Click to Upload", "analyzeBtn": "Analyze Medicine", "analyzing": "Analyzing image and searching database...", "effectLabel": "📋 Effect & Efficacy", "dosageLabel": "💊 Dosage & Usage", "precautionLabel": "⚠️ Precautions", "sideEffectLabel": "❌ Side Effects", "storageLabel": "📦 Storage", "historyTitle": "Search History", "orDivider": "OR", "searchBtn": "Search", "statsTitle": "📊 Manufacturer Statistics", "statsSubtitle": "Click on a manufacturer to see their drugs" },
        "ko": { "name": "한국어", "appTitle": "💊 약품 정보 번역기", "appDesc": "한국 약품 사진을 업로드하여 번역된 정보를 확인하세요.", "languageTitle": "언어를 선택하세요", "backBtn": "뒤로", "startOverBtn": "처음부터", "dropZoneText": "클릭하거나 파일을 드래그하여 업로드", "analyzeBtn": "약품 분석하기", "analyzing": "이미지 분석 및 데이터베이스 검색 중...", "effectLabel": "📋 효능 및 효과", "dosageLabel": "💊 용법 및 용량", "precautionLabel": "⚠️ 주의사항", "sideEffectLabel": "❌ 부작용", "storageLabel": "📦 보관 방법", "historyTitle": "검색 기록", "orDivider": "또는", "searchBtn": "검색", "statsTitle": "📊 제조사별 통계", "statsSubtitle": "제조사를 클릭하면 약품 목록을 볼 수 있습니다" },
        "de": { "name": "Deutsch", "appTitle": "💊 Medikamenten-Info-Übersetzer", "appDesc": "Laden Sie ein Foto Ihres koreanischen Medikaments hoch, um übersetzte Informationen zu erhalten.", "languageTitle": "Wähle deine Sprache", "backBtn": "Zurück", "startOverBtn": "Von vorn anfangen", "dropZoneText": "Ziehen & Ablegen oder Klicken zum Hochladen", "analyzeBtn": "Medikament analysieren", "analyzing": "Bild wird analysiert und Datenbank durchsucht...", "effectLabel": "📋 Wirkung & Wirksamkeit", "dosageLabel": "💊 Dosierung & Anwendung", "precautionLabel": "⚠️ Vorsichtsmaßnahmen", "sideEffectLabel": "❌ Nebenwirkungen", "storageLabel": "📦 Lagerung", "historyTitle": "Suchverlauf", "orDivider": "ODER", "searchBtn": "Suchen", "statsTitle": "📊 Herstellerstatistik", "statsSubtitle": "Klicken Sie auf einen Hersteller, um seine Medikamente zu sehen" },
        "ca": { "name": "Catalan", "appTitle": "💊 Traductor d'Informació de Medicaments", "appDesc": "Pugeu una foto del vostre medicament coreà per obtenir informació traduïda.", "languageTitle": "Trieu el vostre idioma", "backBtn": "Enrere", "startOverBtn": "Començar de nou", "dropZoneText": "Arrossegueu i deixeu anar o feu clic per pujar", "analyzeBtn": "Analitzar Medicament", "analyzing": "Analitzant imatge i cercant a la base de dades...", "effectLabel": "📋 Efecte i Eficàcia", "dosageLabel": "💊 Dosi i Ús", "precautionLabel": "⚠️ Precaucions", "sideEffectLabel": "❌ Efectes Secundaris", "storageLabel": "📦 Emmagatzematge", "historyTitle": "Historial de cerques", "orDivider": "O", "searchBtn": "Cerca", "statsTitle": "📊 Estadístiques dels fabricants", "statsSubtitle": "Feu clic en un fabricant per veure els seus medicaments" }
    };

    // --- Functions ---

    function showView(viewName) {
        Object.values(views).forEach(view => view.classList.add('hidden'));
        if (views[viewName]) {
            views[viewName].classList.remove('hidden');
        }
    }

    function updateUIText(lang) {
        const t = translations[lang] || translations['en'];
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (t[key]) {
                element.textContent = t[key];
            }
        });
    }

    function populateLanguageGrid() {
        languageGrid.innerHTML = '';
        for (const [code, details] of Object.entries(translations)) {
            const card = document.createElement('div');
            card.className = 'lang-card';
            card.dataset.lang = code;
            card.innerHTML = `
                <span class="lang-code">${code.toUpperCase()}</span>
                <span class="lang-name">${details.name}</span>
            `;
            card.addEventListener('click', () => {
                selectedLang = code;
                stopHeaderAnimation(); // Stop animation
                updateUIText(selectedLang);
                showView('upload');

                // Show header buttons (Stats and History)
                const headerButtons = document.getElementById('headerButtons');
                if (headerButtons) {
                    headerButtons.style.display = 'flex';
                }
            });
            languageGrid.appendChild(card);
        }
    }

    function resetState() {
        selectedFile = null;
        fileInput.value = ''; // Clear file input
        imagePreview.classList.add('hidden');
        imagePreview.src = '';
        dropZone.querySelector('.icon').classList.remove('hidden');
        dropZone.querySelector('p').classList.remove('hidden');
        uploadBtn.disabled = true;
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        loading.classList.add('hidden');
    }

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }
        selectedFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreview.classList.remove('hidden');
            dropZone.querySelector('.icon').classList.add('hidden');
            dropZone.querySelector('p').classList.add('hidden');
        };
        reader.readAsDataURL(file);

        uploadBtn.disabled = false;
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
    }

    function displayResult(data) {
        document.getElementById('drugName').textContent = data.name;
        document.getElementById('manufacturer').textContent = data.manufacturer;
        document.getElementById('drugEffect').textContent = data.effect || 'No information available';
        document.getElementById('drugDosage').textContent = data.dosage || 'No information available';
        document.getElementById('drugPrecaution').textContent = data.precaution || 'No information available';
        document.getElementById('drugSideEffect').textContent = data.side_effect || 'No information available';
        document.getElementById('drugStorage').textContent = data.storage || 'No information available';
        resultDiv.classList.remove('hidden');
    }



    // --- Event Listeners ---

    backToLangBtn.addEventListener('click', () => {
        resetState();
        showView('langSelect');
        startHeaderAnimation(); // Restart animation
        // Hide header buttons
        const headerButtons = document.getElementById('headerButtons');
        if (headerButtons) headerButtons.style.display = 'none';
    });

    startOverBtn.addEventListener('click', () => {
        resetState();
        showView('langSelect');
        startHeaderAnimation(); // Restart animation
        // Hide header buttons
        const headerButtons = document.getElementById('headerButtons');
        if (headerButtons) headerButtons.style.display = 'none';
    });

    const backFromHistory = document.getElementById('back-from-history');
    if (backFromHistory) {
        backFromHistory.addEventListener('click', () => {
            showView('upload');
        });
    }

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    async function handleTextSearch() {
        const query = textSearchInput.value;
        if (!query || !selectedLang) return;

        showView('result');
        loading.classList.remove('hidden');
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        textSearchBtn.disabled = true;

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query, lang: selectedLang }),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to find medicine');
            }
            displayResult(data);
            // Save to history
            const drugName = data.name || data.drug_name;
            if (drugName) {
                console.log('Saving to history:', drugName);
                saveToHistory(drugName);
            }
        } catch (err) {
            console.error('Search error:', err);
            alert('Search failed. Please try again.');
        } finally {
            loading.classList.add('hidden');
            // Reset button state
            textSearchBtn.innerHTML = originalBtnContent;
            textSearchBtn.disabled = false;
        }
    }

    textSearchBtn.addEventListener('click', handleTextSearch);

    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile || !selectedLang) return;

        showView('result');
        loading.classList.remove('hidden');
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        uploadBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('lang', selectedLang);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            // Check if foreign medicine was detected
            if (data.is_foreign) {
                console.log('Foreign medicine detected:', data.extracted_text);
                loading.classList.add('hidden');
                // Search for alternatives
                await findAlternatives(data.extracted_text);
                return;
            }
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to process image');
            }
            displayResult(data);
            // Save to history
            const drugName = data.name || data.drug_name;
            if (drugName) {
                console.log('Saving to history:', drugName);
                saveToHistory(drugName);
            }
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
        }
    });

    // --- Header Animation ---
    const header = document.querySelector('header');
    const headerTitle = header.querySelector('h1');
    const headerDesc = header.querySelector('p');
    const langCodes = Object.keys(translations);
    let currentLangIndex = 0;

    let headerAnimationInterval = null;

    function animateHeader() {
        // 1. Fade out
        headerTitle.classList.add('fade-out');
        headerDesc.classList.add('fade-out');

        setTimeout(() => {
            // 2. Change text
            currentLangIndex = (currentLangIndex + 1) % langCodes.length;
            const nextLangCode = langCodes[currentLangIndex];
            const t = translations[nextLangCode];

            if (t) {
                headerTitle.textContent = t.appTitle;
                headerDesc.textContent = t.appDesc;
            }

            // 3. Fade in
            headerTitle.classList.remove('fade-out');
            headerDesc.classList.remove('fade-out');
        }, 300); // Corresponds to the CSS transition time
    }

    function startHeaderAnimation() {
        if (!headerAnimationInterval) {
            headerAnimationInterval = setInterval(animateHeader, 3500);
        }
    }

    function stopHeaderAnimation() {
        clearInterval(headerAnimationInterval);
        headerAnimationInterval = null;
    }

    // --- History Logic ---
    const historyBtn = document.getElementById('historyBtn');

    if (historyBtn) {
        historyBtn.addEventListener('click', () => {
            renderHistory();
            showView('history');
        });
    }

    function saveToHistory(drugName) {
        let history = JSON.parse(localStorage.getItem('drugSearchHistory') || '[]');

        // Remove duplicate if exists
        history = history.filter(item => item !== drugName);

        // Add to top
        history.unshift(drugName);

        // Limit to 20
        if (history.length > 20) history.pop();

        localStorage.setItem('drugSearchHistory', JSON.stringify(history));
    }

    function renderHistory() {
        const historyList = document.getElementById('history-list');
        const history = JSON.parse(localStorage.getItem('drugSearchHistory') || '[]');

        historyList.innerHTML = '';

        if (history.length === 0) {
            historyList.innerHTML = '<div class="empty-state">No search history yet.</div>';
            return;
        }

        history.forEach(drugName => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `
                <span style="font-size: 1.2rem;">🔍</span>
                <span>${drugName}</span>
                <span style="font-size: 0.9rem;">›</span>
            `;
            item.onclick = () => {
                showView('upload');
                // Wait for view transition
                setTimeout(() => {
                    const searchInput = document.getElementById('textSearchInput');
                    if (searchInput) {
                        searchInput.value = drugName;
                        handleTextSearch();
                    }
                }, 100);
            };
            historyList.appendChild(item);
        });
    }

    // --- Statistics Logic ---
    const statsBtn = document.getElementById('statsBtn');
    const backFromStats = document.getElementById('back-from-stats');
    const backFromDrugs = document.getElementById('back-from-drugs');

    if (statsBtn) {
        statsBtn.addEventListener('click', async () => {
            showView('statistics');
            await loadStatistics();
        });
    }

    if (backFromStats) {
        backFromStats.addEventListener('click', () => {
            showView('upload');
        });
    }

    if (backFromDrugs) {
        backFromDrugs.addEventListener('click', () => {
            showView('statistics');
        });
    }

    async function loadStatistics() {
        const statsList = document.getElementById('stats-list');
        statsList.innerHTML = '<div class="loading-state">Loading statistics...</div>';

        try {
            const response = await fetch('/statistics');
            if (!response.ok) throw new Error('Failed to load statistics');
            const data = await response.json();

            if (data.length === 0) {
                statsList.innerHTML = '<div class="empty-state">No statistics available.</div>';
                return;
            }

            statsList.innerHTML = '';
            data.forEach((item, index) => {
                const statItem = document.createElement('div');
                statItem.className = 'stat-item';
                statItem.innerHTML = `
                    <span class="stat-rank">#${index + 1}</span>
                    <span class="stat-name">${item.manufacturer}</span>
                    <span class="stat-count">${item.drug_count} drugs</span>
                    <span class="stat-arrow">›</span>
                `;
                statItem.onclick = () => loadManufacturerDrugs(item.manufacturer);
                statsList.appendChild(statItem);
            });
        } catch (err) {
            console.error('Statistics error:', err);
            statsList.innerHTML = '<div class="error-state">Failed to load statistics.</div>';
        }
    }

    async function loadManufacturerDrugs(manufacturerName) {
        showView('manufacturerDrugs');
        const drugsList = document.getElementById('drugs-list');
        const title = document.getElementById('manufacturer-drugs-title');
        
        title.textContent = `💊 ${manufacturerName}`;
        drugsList.innerHTML = '<div class="loading-state">Loading drugs...</div>';

        try {
            const response = await fetch(`/drugs/by-manufacturer/${encodeURIComponent(manufacturerName)}`);
            if (!response.ok) throw new Error('Failed to load drugs');
            const data = await response.json();

            if (data.length === 0) {
                drugsList.innerHTML = '<div class="empty-state">No drugs found.</div>';
                return;
            }

            drugsList.innerHTML = '';
            data.forEach(drug => {
                const drugItem = document.createElement('div');
                drugItem.className = 'drug-item';
                drugItem.innerHTML = `
                    <span class="drug-icon">💊</span>
                    <div class="drug-info">
                        <span class="drug-name">${drug.name}</span>
                        <span class="drug-storage">${drug.storage || 'No storage info'}</span>
                    </div>
                `;
                drugItem.onclick = () => {
                    // Search for this drug
                    showView('upload');
                    setTimeout(() => {
                        const searchInput = document.getElementById('textSearchInput');
                        if (searchInput) {
                            searchInput.value = drug.name;
                            handleTextSearch();
                        }
                    }, 100);
                };
                drugsList.appendChild(drugItem);
            });
        } catch (err) {
            console.error('Drugs load error:', err);
            drugsList.innerHTML = '<div class="error-state">Failed to load drugs.</div>';
        }
    }

    // --- Foreign Medicine Alternatives Logic ---
    const alternativeMessages = {
        'en': 'These Korean medicines can be used as alternatives:',
        'ko': '이 약을 대체할 수 있는 한국 약품들입니다:',
        'de': 'Diese koreanischen Medikamente können als Alternativen verwendet werden:',
        'ca': 'Aquests medicaments coreans es poden utilitzar com a alternatives:'
    };

    const backFromAlternatives = document.getElementById('back-from-alternatives');
    if (backFromAlternatives) {
        backFromAlternatives.addEventListener('click', () => {
            showView('upload');
        });
    }

    async function findAlternatives(foreignDrugText) {
        showView('alternatives');
        const alternativesList = document.getElementById('alternatives-list');
        const alternativesMessage = document.getElementById('alternatives-message');
        
        alternativesMessage.textContent = '';
        alternativesList.innerHTML = '<div class="loading-state">🔍 Searching for Korean alternatives...</div>';

        try {
            const response = await fetch('/find-alternatives', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    foreign_drug_text: foreignDrugText,
                    lang: selectedLang || 'en'
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to find alternatives');
            }
            
            if (!data.alternatives || data.alternatives.length === 0) {
                alternativesList.innerHTML = '<div class="empty-state">No alternatives found.</div>';
                return;
            }
            
            // Show translated message
            alternativesMessage.textContent = alternativeMessages[selectedLang] || alternativeMessages['en'];
            
            alternativesList.innerHTML = '';
            data.alternatives.forEach(drug => {
                const altItem = document.createElement('div');
                altItem.className = 'alternative-item';
                altItem.innerHTML = `
                    <span class="alt-icon">💊</span>
                    <div class="alt-info">
                        <span class="alt-name">${drug.name}</span>
                        <span class="alt-manufacturer">${drug.manufacturer}</span>
                    </div>
                    <span class="alt-arrow">›</span>
                `;
                altItem.onclick = () => {
                    // Search for this drug to show details
                    showView('upload');
                    setTimeout(() => {
                        const searchInput = document.getElementById('textSearchInput');
                        if (searchInput) {
                            searchInput.value = drug.name;
                            handleTextSearch();
                        }
                    }, 100);
                };
                alternativesList.appendChild(altItem);
            });
            
        } catch (err) {
            console.error('Alternatives search error:', err);
            alternativesList.innerHTML = `<div class="error-state">${err.message}</div>`;
        }
    }

    // --- Initialization ---
    populateLanguageGrid();
    showView('langSelect');
    startHeaderAnimation();

    // Expose for testing
    window.showView = showView;
    window.updateUIText = updateUIText;
});