// ==================== GLOBAL STATE ====================
let currentVoterId = null;
let allBooths = [];
let toastInstance = null;

// ==================== API ENDPOINTS ====================
const API_BASE = `${window.location.origin}/api`;

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadBooths();
    loadStats();
    setupUploadArea();
});

// ==================== EVENT LISTENERS ====================
function initializeEventListeners() {
    // Upload
    document.getElementById('uploadArea').addEventListener('click', () => {
        document.getElementById('pdfInput').click();
    });

    document.getElementById('uploadArea').addEventListener('dragover', (e) => {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('active');
    });

    document.getElementById('uploadArea').addEventListener('dragleave', () => {
        document.getElementById('uploadArea').classList.remove('active');
    });

    document.getElementById('uploadArea').addEventListener('drop', (e) => {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('active');
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    document.getElementById('pdfInput').addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Search
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    document.getElementById('clearSearchBtn').addEventListener('click', clearSearch);

    // Booth selection
    document.getElementById('boothSelect').addEventListener('change', onBoothChange);

    // Clear data
    document.getElementById('clearDataBtn').addEventListener('click', confirmClearData);

    // Update modal
    document.getElementById('saveUpdateBtn').addEventListener('click', saveVoterUpdate);
}

function setupUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const pdfInput = document.getElementById('pdfInput');

    uploadArea.addEventListener('click', () => pdfInput.click());
}

// ==================== FILE UPLOAD ====================
function handleFileSelect(file) {
    if (file.type !== 'application/pdf') {
        showToast('Error', 'Please select a PDF file', 'danger');
        return;
    }

    if (file.size > 50 * 1024 * 1024) {
        showToast('Error', 'File size exceeds 50MB limit', 'danger');
        return;
    }

    uploadPDF(file);
}

document.getElementById('exportBtn').addEventListener('click', exportData);


function exportData() {\n    const filter = document.getElementById('exportFilter').value;\n    const type = document.getElementById('exportType').value;\n    const url = `${API_BASE}/export?type=${type}&filter=${filter}`;\n    \n    const a = document.createElement('a');\n    a.href = url;\n    a.target = '_blank';\n    a.download = '';\n    document.body.appendChild(a);\n    a.click();\n    document.body.removeChild(a);\n    showToast('Download', `Exporting ${filter} voters as ${type.toUpperCase()}`, 'info');\n}


function uploadPDF(file) {
    const formData = new FormData();
    formData.append('pdf_file', file);
    const customFilename = document.getElementById('customFilename') ? document.getElementById('customFilename').value.trim() : '';
    if (customFilename) {
        formData.append('custom_filename', customFilename);
    }

    document.getElementById('uploadProgress').style.display = 'block';
    document.getElementById('uploadResult').style.display = 'none';
    document.getElementById('progressBar').style.width = '0%';

    fetch(`${API_BASE}/upload-pdf`, {
        method: 'POST',
        body: formData
    })
        .then(async response => {
            updateProgress(100);

            const contentType = response.headers.get('content-type') || '';
            const isJson = contentType.includes('application/json');
            const data = isJson
                ? await response.json()
                : { status: 'error', message: `Upload failed with HTTP ${response.status}` };

            if (!response.ok) {
                throw new Error(data.message || `Upload failed with HTTP ${response.status}`);
            }

            return data;
        })
        .then(data => {
            document.getElementById('uploadProgress').style.display = 'none';

            if (data.status === 'success') {
                showUploadResult(true, `Successfully uploaded!
                Added: ${data.added_voters} voters
                Booths: ${data.total_booths}
                Skipped: ${data.skipped_voters}`);
                showToast('Success', data.message, 'success');

                setTimeout(() => {
                    loadBooths();
                    loadStats();
                }, 500);
            } else {
                showUploadResult(false, `Upload failed: ${data.message}`);
                showToast('Error', data.message, 'danger');
            }
        })
        .catch(error => {
            document.getElementById('uploadProgress').style.display = 'none';

            const message = error.message === 'Failed to fetch'
                ? 'Network error while uploading. Check the deployed backend logs for the request failure.'
                : error.message;

            showUploadResult(false, `Upload error: ${message}`);
            showToast('Error', message, 'danger');
        });
}

function updateProgress(percent) {
    document.getElementById('progressBar').style.width = percent + '%';
    document.getElementById('uploadStatus').textContent = percent + '% uploaded...';
}

function showUploadResult(success, message) {
    const resultDiv = document.getElementById('uploadResult');
    resultDiv.className = 'alert ' + (success ? 'alert-success' : 'alert-danger');
    resultDiv.innerHTML = message;
    resultDiv.style.display = 'block';
}

// ==================== BOOTH MANAGEMENT ====================
function loadBooths() {
    fetch(`${API_BASE}/booths`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                allBooths = data.booths;
                populateBoothSelect();
            }
        })
        .catch(error => console.error('Error loading booths:', error));
}

function populateBoothSelect() {
    const select = document.getElementById('boothSelect');
    const currentValue = select.value;

    while (select.options.length > 1) {
        select.remove(1);
    }

    allBooths.forEach(booth => {
        const option = document.createElement('option');
        option.value = booth.id;
        option.textContent = `Booth ${booth.booth_number} - ${booth.booth_name}`;
        select.appendChild(option);
    });

    if (currentValue && select.querySelector(`option[value="${currentValue}"]`)) {
        select.value = currentValue;
    }
}

function onBoothChange() {
    clearSearch();
}

// ==================== SEARCH ====================
function performSearch() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    const boothId = document.getElementById('boothSelect').value;

    if (searchTerm.length < 2) {
        showToast('Warning', 'Search term must be at least 2 characters', 'warning');
        return;
    }

    let url = `${API_BASE}/search?q=${encodeURIComponent(searchTerm)}`;
    if (boothId) {
        url += `&booth_id=${boothId}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displaySearchResults(data.voters);
                document.getElementById('resultsInfo').style.display = 'block';
                document.getElementById('resultsCount').textContent = data.count;
            } else {
                showToast('Error', data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error searching:', error);
            showToast('Error', 'Search failed', 'danger');
        });
}

function displaySearchResults(voters) {
    const container = document.getElementById('votersContainer');
    container.innerHTML = '';

    if (voters.length === 0) {
        container.innerHTML = '<div class="p-3 text-center text-muted">No voters found</div>';
        document.getElementById('votersCard').style.display = 'block';
        document.getElementById('noDataAlert').style.display = 'none';
        return;
    }

    voters.forEach(voter => {
        const voterDiv = createVoterElement(voter);
        container.appendChild(voterDiv);
    });

    document.getElementById('votersCard').style.display = 'block';
    document.getElementById('noDataAlert').style.display = 'none';
}

function createVoterElement(voter) {\n    const div = document.createElement('div');\n    div.className = 'voter-item';\n\n    const statusBadge = voter.status || 'not_visited';\n    const statusDisplay = statusBadge.replace('_', ' ').charAt(0).toUpperCase() +\n        statusBadge.replace('_', ' ').slice(1);\n\n    const phoneDisplay = voter.phone_number ? `<div class="voter-phone"><strong>Phone:</strong> ${voter.phone_number}</div>` : '';\n\n    div.innerHTML = `\n        <div class="voter-name">${voter.voter_name}</div>\n        <div class="voter-id"><strong>ID:</strong> ${voter.voter_id}</div>\n        <div class="voter-booth"><strong>Booth:</strong> ${voter.booth_number}</div>\n        ${phoneDisplay}\n        <span class="voter-status ${statusBadge}">${statusDisplay}</span>\n        ${voter.custom_notes ? `<div class="voter-notes"><strong>Notes:</strong> ${voter.custom_notes}</div>` : ''}\n        <div class="voter-actions">\n            <button class="btn btn-sm btn-outline-primary" onclick="openUpdateModal(${voter.id}, '${voter.voter_name}', '${voter.voter_id}', '${voter.phone_number || ''}')">\n                <i class="bi bi-pencil"></i> Update\n            </button>\n            <button class="btn btn-sm btn-outline-success" onclick="markAsVisited(${voter.id})">\n                <i class="bi bi-check-circle"></i> Mark Visited\n            </button>\n        </div>\n    `;\n\n    return div;\n}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('votersContainer').innerHTML = '';
    document.getElementById('votersCard').style.display = 'none';
    document.getElementById('resultsInfo').style.display = 'none';
    document.getElementById('noDataAlert').style.display = 'block';
}

// ==================== VOTER UPDATES ====================
function openUpdateModal(voterId, voterName, voterId_epic, phoneNumber = '') {
    currentVoterId = voterId;
    document.getElementById('voterNameDisplay').value = voterName;
    document.getElementById('voterIdDisplay').value = voterId_epic;
    document.getElementById('phoneInput').value = phoneNumber;
    document.getElementById('statusSelect').value = 'not_visited';
    document.getElementById('notesInput').value = '';

    const modal = new bootstrap.Modal(document.getElementById('updateModal'));
    modal.show();
}

function saveVoterUpdate() {
    const phone = document.getElementById('phoneInput').value.trim();
    const status = document.getElementById('statusSelect').value;
    const notes = document.getElementById('notesInput').value.trim();

    if (!status && !phone && !notes) {
        showToast('Warning', 'Please provide at least one field to update', 'warning');
        return;
    }

    const payload = {};
    if (phone) payload.phone_number = phone;
    if (status) payload.status = status;
    if (notes) payload.custom_notes = notes;

    fetch(`${API_BASE}/voter/${currentVoterId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Success', 'Voter updated successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('updateModal')).hide();

                performSearch();
                loadStats();
            } else {
                showToast('Error', data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error updating voter:', error);
            showToast('Error', 'Failed to update voter', 'danger');
        });
}

function markAsVisited(voterId) {
    fetch(`${API_BASE}/voter/${voterId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: 'visited'
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Success', 'Marked as visited', 'success');
                performSearch();
                loadStats();
            }
        })
        .catch(error => console.error('Error:', error));
}

// ==================== STATISTICS ====================
function loadStats() {
    fetch(`${API_BASE}/stats`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('totalVoters').textContent = data.total_voters || 0;
                document.getElementById('visitedVoters').textContent = data.visited_voters || 0;
                document.getElementById('remainingVoters').textContent =
                    (data.total_voters || 0) - (data.visited_voters || 0);
                document.getElementById('totalBooths').textContent = data.total_booths || 0;

                if (data.total_voters === 0) {
                    document.getElementById('noDataAlert').style.display = 'block';
                }
            }
        })
        .catch(error => console.error('Error loading stats:', error));
}

// ==================== DATA MANAGEMENT ====================
function confirmClearData() {
    if (confirm('Are you sure you want to delete ALL voter data? This action cannot be undone.')) {
        clearAllData();
    }
}

function clearAllData() {
    fetch(`${API_BASE}/clear-data`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Success', 'All data cleared', 'success');
                document.getElementById('votersContainer').innerHTML = '';
                document.getElementById('votersCard').style.display = 'none';
                clearSearch();
                loadBooths();
                loadStats();
            }
        })
        .catch(error => {
            console.error('Error clearing data:', error);
            showToast('Error', 'Failed to clear data', 'danger');
        });
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(title, message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');

    toastTitle.textContent = title;
    toastBody.textContent = message;

    toast.className = 'toast';
    if (type === 'success') {
        toast.style.backgroundColor = '#d1e7dd';
        toast.style.color = '#0f5132';
    } else if (type === 'danger') {
        toast.style.backgroundColor = '#f8d7da';
        toast.style.color = '#842029';
    } else if (type === 'warning') {
        toast.style.backgroundColor = '#fff3cd';
        toast.style.color = '#664d03';
    } else {
        toast.style.backgroundColor = '#cfe2ff';
        toast.style.color = '#055160';
    }

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}
