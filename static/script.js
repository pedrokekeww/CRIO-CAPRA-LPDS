document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');

    const foldersContainer = document.getElementById('folders-container');
    const addFolderBtnCard = document.getElementById('add-folder-btn-card');

    const analysisFolderSelect = document.getElementById('analysis-folder-select');
    const activeModelSelect = document.getElementById('active-model-select');
    const startAnalysisBtn = document.getElementById('start-analysis-btn');

    // Folder Details Elements
    const fdBackBtn = document.getElementById('fd-back-btn');
    const fdTitleName = document.getElementById('fd-title-name');
    const fdBreadcrumbName = document.getElementById('fd-breadcrumb-name');
    const fdSamplesCount = document.getElementById('fd-samples-count');
    const fdGalleryGrid = document.getElementById('fd-gallery-grid');
    const fdAddSamplesBtn = document.getElementById('fd-add-samples-btn');
    const fdSearchInput = document.getElementById('fd-search-input');
    const btnMultiDelete = document.getElementById('btn-multi-delete');

    const dropArea = document.getElementById('drop-area');
    const imageInput = document.getElementById('image-input');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const fileBadge = document.getElementById('file-badge');
    const removeImageBtn = document.getElementById('remove-image');

    const resultsContainer = document.getElementById('results-container');
    const analysisCard = document.querySelector('.analysis-card');

    const analysisConfigContainer = document.getElementById('analysis-config-container');
    const analysisReadyContainer = document.getElementById('analysis-ready-container');
    const readyBgGrid = document.getElementById('ready-bg-grid');
    const readyViewResultsBtn = document.getElementById('ready-view-results');
    const readyPropName = document.getElementById('ready-prop-name');
    const readyPropFolder = document.getElementById('ready-prop-folder');
    const readyPropModel = document.getElementById('ready-prop-model');
    const readyPropDate = document.getElementById('ready-prop-date');
    const analysisViewTitle = document.getElementById('analysis-view-title');
    const analysisViewDesc = document.getElementById('analysis-view-desc');
    const readyNavCards = document.querySelectorAll('.ready-bottom-nav .nav-card');

    const newFolderModal = document.getElementById('new-folder-modal');
    const openNewFolderModalBtn = document.getElementById('open-new-folder-modal');
    const cancelFolderBtn = document.getElementById('cancel-folder-btn');
    const saveFolderBtn = document.getElementById('save-folder-btn');
    const newFolderNameInput = document.getElementById('new-folder-name');

    const lightboxModal = document.getElementById('lightbox-modal');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxClose = document.querySelector('.lightbox-close');
    const lbCounter = document.getElementById('lb-counter');
    const lbModelName = document.getElementById('lb-model-name');
    const lbConfidence = document.getElementById('lb-confidence');
    const lbTotal = document.getElementById('lb-total');
    const lbClassesList = document.getElementById('lb-classes-list');
    const lbPrev = document.getElementById('lb-prev');
    const lbNext = document.getElementById('lb-next');

    let selectedFiles = [];
    let currentResults = []; // To store batch results for lightbox
    let currentLbIndex = 0;

    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const metricsFolderSelect = document.getElementById('metrics-folder-select');
    const metricsDashboard = document.getElementById('metrics-dashboard');

    // Sidebar Toggle
    const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (isCollapsed) sidebar.classList.add('collapsed');

    sidebarToggle.addEventListener('click', () => {
        const collapsed = sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebar-collapsed', collapsed);
    });

    // --- View Management ---
    function switchView(viewName) {
        views.forEach(v => v.classList.add('hidden'));
        document.getElementById(`view-${viewName}`).classList.remove('hidden');

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === viewName) item.classList.add('active');
        });

        if (viewName === 'analysis') {
            loadFolders(); // For the select
            loadModels();
            const header = document.querySelector('#view-analysis .view-header');
            if (header) header.style.textAlign = 'left';

            // Reset to configuration state
            analysisConfigContainer.classList.remove('hidden');
            analysisReadyContainer.classList.add('hidden');
            analysisViewTitle.textContent = 'Configure a nova análise';
            analysisViewDesc.textContent = 'ajuste os parâmetros abaixo e anexe as amostras para que a I.A. analise e classifique';
        }
        if (viewName === 'metrics') {
            loadFolders();
            metricsDashboard.classList.add('hidden');
            metricsFolderSelect.value = '';
        }
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => switchView(item.dataset.view));
    });

    // --- Folder APIs ---
    async function loadFolders() {
        const res = await fetch('/folders/');
        const folders = await res.json();

        // Update Folder View
        const existingCards = foldersContainer.querySelectorAll('.folder-card');
        existingCards.forEach(c => c.remove());

        folders.forEach(folder => {
            const card = document.createElement('div');
            card.className = 'folder-card';
            card.innerHTML = `
                <button class="btn-edit-folder" title="Renomear Pasta" data-id="${folder.id}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 20h9"></path>
                        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                    </svg>
                </button>
                <button class="btn-delete-folder" title="Excluir Pasta" data-id="${folder.id}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6"/>
                    </svg>
                </button>
                <div class="folder-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                </div>
                <span class="folder-name">${folder.name}</span>
                <div class="folder-footer">
                    <div class="samples-info">
                        <span>Amostras</span>
                        <span class="samples-count">${folder.analysis_count}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${Math.min(folder.analysis_count * 5, 100)}%"></div>
                    </div>
                </div>
                <div class="updated-date">Atualizado: ${new Date(folder.created_at).toLocaleDateString()}</div>
            `;

            // Rename click
            card.querySelector('.btn-edit-folder').addEventListener('click', async (e) => {
                e.stopPropagation();
                const newName = prompt(`Digite o novo nome para a pasta "${folder.name}":`, folder.name);
                if (newName !== null && newName.trim() !== '') {
                    try {
                        const res = await fetch(`/folders/${folder.id}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ name: newName.trim() })
                        });
                        if (res.ok) {
                            loadFolders();
                        } else {
                            alert("Erro ao renomear pasta.");
                        }
                    } catch (err) {
                        console.error("Erro renomeando", err);
                    }
                }
            });

            // Delete click
            card.querySelector('.btn-delete-folder').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteFolder(folder.id, folder.name);
            });

            card.addEventListener('click', () => {
                if(window.openFolderDetails) {
                    window.openFolderDetails(folder.id, folder.name, folder.analysis_count);
                }
            });

            foldersContainer.insertBefore(card, addFolderBtnCard);
        });

        // Update Selects (Analysis and Metrics)
        const currentAnalysisVal = analysisFolderSelect.value;
        const currentMetricsVal = metricsFolderSelect.value;

        const optionsHtml = '<option value="">Selecione uma pasta</option>' +
            folders.map(f => `<option value="${f.id}">${f.name}</option>`).join('');

        analysisFolderSelect.innerHTML = optionsHtml;
        metricsFolderSelect.innerHTML = optionsHtml;

        analysisFolderSelect.value = currentAnalysisVal;
        metricsFolderSelect.value = currentMetricsVal;
    }

    async function createFolder() {
        const name = newFolderNameInput.value.trim();
        if (!name) return;

        const res = await fetch('/folders/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });

        if (res.ok) {
            newFolderNameInput.value = '';
            newFolderModal.classList.add('hidden');
            loadFolders();
        }
    }

    async function deleteFolder(id, name) {
        if (!confirm(`Tem certeza que deseja excluir a pasta "${name}"? Todas as análises dentro dela serão apagadas.`)) {
            return;
        }

        const res = await fetch(`/folders/${id}`, {
            method: 'DELETE'
        });

        if (res.ok) {
            loadFolders();
        } else {
            alert('Erro ao excluir pasta.');
        }
    }

    async function loadModels() {
        const res = await fetch('/models/');
        const models = await res.json();
        const currentVal = activeModelSelect.value;
        activeModelSelect.innerHTML = '<option value="">Selecione um modelo</option>';
        models.forEach(model => {
            const opt = document.createElement('option');
            opt.value = model.id;
            opt.textContent = model.name;
            activeModelSelect.appendChild(opt);
        });
        activeModelSelect.value = currentVal;
    }

    // --- Metrics APIs ---
    async function loadMetrics(folderId) {
        if (!folderId) {
            metricsDashboard.classList.add('hidden');
            return;
        }

        const res = await fetch(`/folders/${folderId}/metrics`);
        const data = await res.json();

        if (res.ok) {
            document.getElementById('m-total-images').textContent = data.total_images;
            document.getElementById('m-total-det').textContent = data.total_detections;
            document.getElementById('m-avg-conf').textContent = `${(data.avg_confidence * 100).toFixed(1)}%`;

            const container = document.getElementById('m-distribution-container');
            container.innerHTML = '';

            Object.entries(data.class_distribution).forEach(([cls, percent]) => {
                const item = document.createElement('div');
                item.className = 'dist-item';
                item.innerHTML = `
                    <div class="dist-header">
                        <span class="dist-name">${cls}</span>
                        <span class="dist-percent">${percent.toFixed(1)}%</span>
                    </div>
                    <div class="dist-bar-bg">
                        <div class="dist-bar-fill" style="width: 0%"></div>
                    </div>
                `;
                container.appendChild(item);

                // Trigger animation
                setTimeout(() => {
                    item.querySelector('.dist-bar-fill').style.width = `${percent}%`;
                }, 100);
            });

            metricsDashboard.classList.remove('hidden');
        }
    }

    metricsFolderSelect.addEventListener('change', (e) => loadMetrics(e.target.value));

    // --- Analysis ---
    async function runAnalysis() {
        const analysisName = document.getElementById('analysis-name').value;
        const folderId = analysisFolderSelect.value || 0; // 0 if none
        const modelId = activeModelSelect.value;

        if (!analysisName || !modelId || selectedFiles.length === 0) {
            return alert('Preencha ao menos o nome e o modelo, e selecione uma imagem!');
        }

        startAnalysisBtn.disabled = true;
        const originalText = startAnalysisBtn.innerHTML;

        resultsContainer.innerHTML = '';
        currentResults = []; // Reset

        for (let i = 0; i < selectedFiles.length; i++) {
            const file = selectedFiles[i];
            const currentTitle = selectedFiles.length > 1 ? `${analysisName} (${i + 1})` : analysisName;

            startAnalysisBtn.textContent = `Processando ${i + 1}/${selectedFiles.length}...`;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('folder_id', folderId);
            formData.append('analysis_name', currentTitle);

            try {
                const res = await fetch(`/analyze/${modelId}`, {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                if (res.ok) {
                    currentResults.push(data);
                    addResultCard(data, currentTitle, i);
                } else {
                    const errorMsg = data.detail || 'Erro desconhecido';
                    console.error(`Erro na imagem ${i + 1}:`, errorMsg);
                    alert(`Falha ao processar "${currentTitle}": ${errorMsg}`);
                }
            } catch (err) {
                console.error(`Falha ao analisar imagem ${i + 1}:`, err);
                alert(`Erro de conexão ao processar "${currentTitle}".`);
            }
        }

        startAnalysisBtn.disabled = false;
        startAnalysisBtn.innerHTML = originalText;

        const totalDet = currentResults.reduce((acc, r) => acc + r.metadata.detections_count, 0);
        const failedCount = selectedFiles.length - currentResults.length;

        if (failedCount > 0) {
            console.warn(`${failedCount} imagens falharam no processamento.`);
        }

        if (folderId > 0) loadFolders();

        // Show Ready View
        showAnalysisReadyView({
            name: analysisName,
            folder: analysisFolderSelect.options[analysisFolderSelect.selectedIndex]?.text || 'Sem Pasta',
            model: activeModelSelect.options[activeModelSelect.selectedIndex]?.text || '-',
            date: new Date().toLocaleDateString(),
            results: currentResults
        });
    }

    function showAnalysisReadyView(data) {
        // Update Text
        const header = document.querySelector('#view-analysis .view-header');
        if (header) header.style.textAlign = 'center';

        analysisViewTitle.textContent = 'Sua análise está pronta!';
        analysisViewDesc.textContent = 'clique em "Ver Resultados" para conferir o que a I.A. preparou para você';

        // Update Properties
        readyPropName.textContent = data.name;
        readyPropFolder.textContent = data.folder;
        readyPropModel.textContent = data.model;
        readyPropDate.textContent = data.date;

        // Update Background Preview
        readyBgGrid.innerHTML = '';
        data.results.slice(0, 3).forEach(res => {
            const img = document.createElement('img');
            img.src = res.image;
            readyBgGrid.appendChild(img);
        });

        // Toggle Container
        analysisConfigContainer.classList.add('hidden');
        analysisReadyContainer.classList.remove('hidden');
    }

    function addResultCard(data, title, index) {
        const card = document.createElement('div');
        card.className = 'results-card';
        card.innerHTML = `
            <h3>${title}</h3>
            <div class="analysis-stats">Detecções: ${data.metadata.detections_count}</div>
            <div class="result-img-wrapper">
                <img src="${data.image}" alt="Resultado">
            </div>
        `;

        card.querySelector('.result-img-wrapper').addEventListener('click', () => {
            openLightbox(index);
        });

        resultsContainer.appendChild(card);
    }

    // --- Lightbox logic ---
    function openLightbox(index) {
        if (!currentResults || currentResults.length === 0) {
            return alert('Nenhum resultado disponível para visualizar.');
        }
        currentLbIndex = index;
        updateLightboxContent();
        lightboxModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    function updateLightboxContent() {
        const result = currentResults[currentLbIndex];
        if (!result) return;

        lightboxImg.src = result.image;
        lbCounter.textContent = `${currentLbIndex + 1} de ${currentResults.length}`;
        lbModelName.textContent = result.metadata.model_name || 'YOLOv8';

        // Stats
        const confs = result.metadata.confidences;
        const avgConf = confs.length ? (confs.reduce((a, b) => a + b, 0) / confs.length * 100).toFixed(1) + '%' : '0%';
        lbConfidence.textContent = avgConf;
        lbTotal.textContent = result.metadata.detections_count;

        // Classes list
        lbClassesList.innerHTML = '';
        const counts = {};
        result.metadata.classes.forEach(c => counts[c] = (counts[c] || 0) + 1);

        Object.keys(counts).forEach(cls => {
            const item = document.createElement('div');
            item.className = 'class-item';
            const pct = ((counts[cls] / result.metadata.detections_count) * 100).toFixed(0);
            item.innerHTML = `
                <span class="class-name">${cls} (${counts[cls]})</span>
                <span class="class-pct">${pct}%</span>
            `;
            lbClassesList.appendChild(item);
        });

        // Nav visibility
        lbPrev.style.visibility = currentLbIndex > 0 ? 'visible' : 'hidden';
        lbNext.style.visibility = currentLbIndex < currentResults.length - 1 ? 'visible' : 'hidden';
    }

    lightboxClose.addEventListener('click', () => {
        lightboxModal.classList.add('hidden');
        document.body.style.overflow = '';
    });

    lbPrev.addEventListener('click', () => {
        if (currentLbIndex > 0) {
            currentLbIndex--;
            updateLightboxContent();
        }
    });

    lbNext.addEventListener('click', () => {
        if (currentLbIndex < currentResults.length - 1) {
            currentLbIndex++;
            updateLightboxContent();
        }
    });

    // Eventos legados removidos para evitar erro de null

    // --- Events ---
    addFolderBtnCard.addEventListener('click', () => newFolderModal.classList.remove('hidden'));
    openNewFolderModalBtn.addEventListener('click', () => newFolderModal.classList.remove('hidden'));
    cancelFolderBtn.addEventListener('click', () => newFolderModal.classList.add('hidden'));
    saveFolderBtn.addEventListener('click', createFolder);

    dropArea.addEventListener('click', () => imageInput.click());

    imageInput.addEventListener('change', (e) => {
        handleFiles(Array.from(e.target.files));
    });

    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('dragover');
    });

    dropArea.addEventListener('dragleave', () => dropArea.classList.remove('dragover'));

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('dragover');
        handleFiles(Array.from(e.dataTransfer.files));
    });

    function handleFiles(files) {
        if (!files.length) return;
        selectedFiles = files;

        const reader = new FileReader();
        reader.onload = (e) => {
            // Fix for TIFF and browsers: If TIFF, browsers might not show it.
            // We can check the data URL header.
            let result = e.target.result;

            // If it's a TIFF, we might need a placeholder or a converter.
            // For now, let's at least ensure we are setting the src.
            imagePreview.src = result;

            uploadPlaceholder.classList.add('hidden');
            previewContainer.classList.remove('hidden');

            if (files.length > 1) {
                fileBadge.textContent = `+${files.length - 1} fotos`;
                fileBadge.classList.remove('hidden');
            } else {
                fileBadge.classList.add('hidden');
            }
        };

        if (files[0].type === 'image/tiff' || files[0].name.toLowerCase().endsWith('.tif') || files[0].name.toLowerCase().endsWith('.tiff')) {
            // TIFF handling
            imagePreview.src = 'data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHN0cm9rZT0iY3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTE0IDJINmEyIDIgMCAwIDAtMiAydjE2YTIgMiAwIDAgMCAyIDJoMTJhMiAyIDAgMCAwIDItMlY4eiIvPjxwb2x5bGluZSBwb2ludHM9IjE0IDIgMTQgOCAyMCA4Ii8+PHRleHQgeD0iNSIgeT0iMTgiIGZvbnQtc2l6ZT0iNSIgZmlsbD0iY3VycmVudENvbG9yIiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiI+VElGRjwvdGV4dD48L3N2Zz4=';

            // Add feedback
            let feedback = document.querySelector('.tiff-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'tiff-feedback';
                feedback.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    <span>Preview não disponível para TIFF</span>
                `;
                previewContainer.appendChild(feedback);
            }

            uploadPlaceholder.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            if (files.length > 1) {
                fileBadge.textContent = `+${files.length - 1} fotos`;
                fileBadge.classList.remove('hidden');
            }
        } else {
            // Remove feedback if present
            const feedback = document.querySelector('.tiff-feedback');
            if (feedback) feedback.remove();
            reader.readAsDataURL(files[0]);
        }
    }

    removeImageBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFiles = [];
        imageInput.value = '';
        uploadPlaceholder.classList.remove('hidden');
        previewContainer.classList.add('hidden');

        // Reset UI
        resultsContainer.classList.add('hidden');

        // Remove TIFF feedback
        const feedback = document.querySelector('.tiff-feedback');
        if (feedback) feedback.remove();
    });

    startAnalysisBtn.addEventListener('click', runAnalysis);
    readyViewResultsBtn.addEventListener('click', () => openLightbox(0));

    readyNavCards.forEach(card => {
        card.addEventListener('click', () => {
            readyNavCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            const view = card.dataset.view;
            switchView(view);
        });
    });

    // --- Folder Details Logic ---
    let currentFolderDetailsId = null;
    let folderAnalyses = [];
    let currentFolderViewAnalyses = [];

    if(fdBackBtn) {
        fdBackBtn.addEventListener('click', () => {
            switchView('folders');
            currentFolderDetailsId = null;
        });
    }

    window.openFolderDetails = async function(folderId, folderName, analysisCount) {
        currentFolderDetailsId = folderId;
        fdTitleName.textContent = folderName;
        fdBreadcrumbName.textContent = folderName;
        fdSamplesCount.textContent = `${analysisCount || 0} AMOSTRAS`;
        
        switchView('folder-details');
        fdGalleryGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 40px;">Carregando imagens...</div>';
        
        try {
            const res = await fetch(`/folders/${folderId}/analyses`);
            if (res.ok) {
                folderAnalyses = await res.json();
                fdSamplesCount.textContent = `${folderAnalyses.length} AMOSTRAS`;
                
                // Reset tabs to default (Amostras)
                const amostrasTab = document.querySelector('.fd-tab[data-tab="amostras"]');
                if(amostrasTab) amostrasTab.click();
                if(fdSearchInput) fdSearchInput.value = '';

                renderFolderGallery(folderAnalyses);
                if(window.renderAmostrasList) window.renderAmostrasList(folderAnalyses);
            } else {
                fdGalleryGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--danger); padding: 40px;">Erro ao carregar imagens.</div>';
            }
        } catch (err) {
            console.error("Erro ao puxar analyses da pasta", err);
            fdGalleryGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--danger); padding: 40px;">Erro de conexão.</div>';
        }
    }

    function renderFolderGallery(analyses) {
        currentFolderViewAnalyses = analyses;
        fdGalleryGrid.innerHTML = '';
        if (analyses.length === 0) {
            fdGalleryGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 40px;">Nenhuma imagem nesta pasta.</div>';
            return;
        }

        analyses.forEach((analysis, index) => {
            const card = document.createElement('div');
            card.className = 'fd-item-card';
            
            card.innerHTML = `
                <img src="${analysis.image_url}" alt="${analysis.name}">
                <div class="fd-item-checkbox">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"></path></svg>
                </div>
                <div class="fd-item-overlay">
                    <div class="fd-item-title">${analysis.name}</div>
                    <div class="fd-item-actions">
                        <button class="fd-item-btn" title="Expandir" onclick="event.stopPropagation(); window.openFolderLightbox(${index})">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="15 3 21 3 21 9"></polyline>
                                <polyline points="9 21 3 21 3 15"></polyline>
                                <line x1="21" y1="3" x2="14" y2="10"></line>
                                <line x1="3" y1="21" x2="10" y2="14"></line>
                            </svg>
                        </button>
                        <button class="fd-item-btn btn-danger" title="Excluir" onclick="event.stopPropagation(); window.deleteAnalysis(${analysis.id})">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6"/>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
            
            if (window.selectedForDelete && window.selectedForDelete.has(analysis.id)) {
                card.classList.add('selected-for-delete');
            }

            card.onclick = (e) => {
                e.stopPropagation();
                if (window.selectedForDelete.has(analysis.id)) {
                    window.selectedForDelete.delete(analysis.id);
                    card.classList.remove('selected-for-delete');
                } else {
                    window.selectedForDelete.add(analysis.id);
                    card.classList.add('selected-for-delete');
                }
                if(window.updateMultiDeleteButtonState) window.updateMultiDeleteButtonState();
            };

            fdGalleryGrid.appendChild(card);
        });
    }

    if(fdSearchInput) {
        fdSearchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = folderAnalyses.filter(a => a.name.toLowerCase().includes(term));
            
            // Re-render whatever view is active
            renderFolderGallery(filtered);
            if(window.renderAmostrasList) window.renderAmostrasList(filtered);
        });
    }
    
    // --- Tabs Logic ---
    const fdTabs = document.querySelectorAll('#fd-tabs .fd-tab');
    const fdAmostrasContainer = document.getElementById('fd-amostras-container');
    const fdGalleryContainer = document.getElementById('fd-gallery-container');

    if(fdTabs.length > 0) {
        fdTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                fdTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                if (tab.dataset.tab === 'amostras') {
                    fdAmostrasContainer.classList.remove('hidden');
                    fdGalleryContainer.classList.add('hidden');
                } else {
                    fdAmostrasContainer.classList.add('hidden');
                    fdGalleryContainer.classList.remove('hidden');
                }
            });
        });
    }

    window.renderAmostrasList = function(analyses) {
        const listContainer = document.getElementById('fd-amostras-list');
        if(!listContainer) return;
        
        listContainer.innerHTML = '';
        
        if (analyses.length === 0) {
            listContainer.innerHTML = '<div style="color: var(--text-dim); padding: 20px 0;">Nenhuma amostra registrada.</div>';
            return;
        }

        const groups = {};
        analyses.forEach(a => {
            // "nome da analise (1)" -> "nome da analise"
            const baseName = a.name.replace(/\s\(\d+\)$/, '').trim();
            if (!groups[baseName]) {
                groups[baseName] = {
                    name: baseName,
                    count: 0,
                    ids: [],
                    date: a.created_at || new Date().toISOString()
                };
            }
            groups[baseName].count++;
            groups[baseName].ids.push(a.id);
        });

        Object.values(groups).forEach(group => {
            const dateObj = new Date(group.date);
            const dateStr = dateObj.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
            
            const row = document.createElement('div');
            row.className = 'fd-amostra-row';
            
            if (group.ids.every(id => window.selectedForDelete && window.selectedForDelete.has(id))) {
                row.classList.add('selected-for-delete');
            }

            row.innerHTML = `
                <div class="fd-amostra-checkbox">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"></path></svg>
                </div>
                <div class="fd-amostra-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M10 2v7.31"></path>
                        <path d="M14 9.3V1.99"></path>
                        <path d="M8.5 2h7"></path>
                        <path d="M14 9.3a6.5 6.5 0 1 1-4 0"></path>
                        <path d="M5.52 16h12.96"></path>
                    </svg>
                </div>
                <div class="fd-amostra-details">
                    <div class="fd-amostra-title">${group.name}</div>
                    <div class="fd-amostra-meta">
                        <div class="fd-meta-item">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                            ${dateStr}
                        </div>
                        <div class="fd-meta-item">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                            ${group.count} imagens anexadas a essa análise
                        </div>
                    </div>
                </div>
            `;
            
            const checkboxDiv = row.querySelector('.fd-amostra-checkbox');
            if (checkboxDiv) {
                checkboxDiv.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const currentlySelected = group.ids.every(id => window.selectedForDelete && window.selectedForDelete.has(id));
                    if (currentlySelected) {
                        group.ids.forEach(id => window.selectedForDelete.delete(id));
                        row.classList.remove('selected-for-delete');
                    } else {
                        group.ids.forEach(id => window.selectedForDelete.add(id));
                        row.classList.add('selected-for-delete');
                    }
                    if(window.updateMultiDeleteButtonState) window.updateMultiDeleteButtonState();
                });
            }

            row.addEventListener('click', () => {
                // Switch to Imagens tab and filter by name
                const imagensTab = document.querySelector('.fd-tab[data-tab="imagens"]');
                if(imagensTab) imagensTab.click();
                
                if(fdSearchInput) {
                    fdSearchInput.value = group.name;
                    fdSearchInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });

            listContainer.appendChild(row);
        });
    }

    if(fdAddSamplesBtn) {
        fdAddSamplesBtn.addEventListener('click', () => {
             switchView('analysis');
             if(analysisFolderSelect && currentFolderDetailsId) {
                 analysisFolderSelect.value = currentFolderDetailsId;
             }
        });
    }

    window.openFolderLightbox = function(index) {
        if (!currentFolderViewAnalyses || currentFolderViewAnalyses.length === 0) return;
        
        currentResults = currentFolderViewAnalyses.map(a => {
            const parsedMeta = a.results_json ? JSON.parse(a.results_json) : {};
            return {
                id: a.id,
                image: a.image_url,
                metadata: {
                    model_name: parsedMeta.model_name || 'Desconhecido',
                    detections_count: a.detections || 0,
                    classes: parsedMeta.classes || [],
                    confidences: parsedMeta.confidences || []
                }
            };
        });
        
        currentLbIndex = index;
        updateLightboxContent();
        lightboxModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    window.deleteAnalysis = async function(id) {
         if(!confirm("Atenção: Ação irreversível!\nTem certeza absoluta que deseja excluir esta análise?")) return;
         
         try {
             const res = await fetch(`/analyses/${id}`, { method: 'DELETE' });
             if (res.ok) {
                 if(currentFolderDetailsId) {
                     // Get current count and subtract 1
                     const currentCount = parseInt(fdSamplesCount.textContent.replace(/\D/g, '')) || 0;
                     const newCount = Math.max(0, currentCount - 1);
                     window.openFolderDetails(currentFolderDetailsId, fdTitleName.textContent, newCount);
                 }
             } else {
                 alert("Erro ao excluir análise do servidor.");
             }
         } catch(e) {
             console.error("Erro deletando análise:", e);
         }
    }

    window.selectedForDelete = new Set();
    
    window.updateMultiDeleteButtonState = function() {
        const btn = document.getElementById('btn-multi-delete');
        if(!btn) return;
        
        if (window.selectedForDelete && window.selectedForDelete.size > 0) {
            btn.classList.add('active-danger');
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        } else {
            btn.classList.remove('active-danger');
            btn.style.opacity = '0.3';
            btn.style.pointerEvents = 'none';
        }
    };

    if(btnMultiDelete) {
        // Initial state
        window.updateMultiDeleteButtonState();
        
        btnMultiDelete.addEventListener('click', async () => {
            if(window.selectedForDelete && window.selectedForDelete.size > 0) {
                if(confirm(`Tem certeza absoluta que deseja excluir as ${window.selectedForDelete.size} imagens selecionadas?\nEsta ação é irreversível.`)) {
                    let deletedCount = 0;
                    for(const id of window.selectedForDelete) {
                        try {
                            const res = await fetch(`/analyses/${id}`, { method: 'DELETE' });
                            if(res.ok) deletedCount++;
                        } catch(e) {
                            console.error("Error deleting", id, e);
                        }
                    }
                    
                    // Reload data
                    if(currentFolderDetailsId) {
                        const currentCount = parseInt(fdSamplesCount.textContent.replace(/\D/g, '')) || 0;
                        const newCount = Math.max(0, currentCount - deletedCount);
                        window.selectedForDelete.clear();
                        window.updateMultiDeleteButtonState();
                        window.openFolderDetails(currentFolderDetailsId, fdTitleName.textContent, newCount);
                    }
                }
            }
        });
    }

    // Initial Load
    switchView('analysis');
});
