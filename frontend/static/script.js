// ==================== GLOBAL STATE ====================
let currentVoterId = null;
let allBooths = [];
let toastInstance = null;

// ==================== API ENDPOINTS ====================
const API_BASE = `${window.location.origin}/api`;

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    // First, check if we are authenticated by trying to load stats.
    // If it fails with 401, we will be redirected to login.
    loadInitialData();
});

function loadInitialData() {
    fetch(`${API_BASE}/stats`)
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login'; // Redirect to login
                return null;
            }
            return response.json();
        })
        .then(data => {
            if (data) { // Only proceed if we are authenticated
                initializeEventListeners();
                populateStats(data); // Use initial stats load
                loadBooths();
            }
        })
        .catch(error => {
            console.error('Initial data load failed:', error);
            // Potentially show an error message that the backend is down
        });
}

// ==================== EVENT LISTENERS ====================
function initializeEventListeners() {
    // Upload
    document.getElementById('uploadArea').addEventListener('click', () => {
        document.getElementById('fileInput').click();
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

    document.getElementById('fileInput').addEventListener('change', (e) => {
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

    // Export buttons
    document.getElementById('exportCsvBtn').addEventListener('click', () => exportData('csv'));
    document.getElementById('exportXlsxBtn').addEventListener('click', () => exportData('excel'));
}

// ==================== FILE UPLOAD ====================
function handleFileSelect(file) {
    const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'];
    const isAllowed = allowedTypes.includes(file.type) || file.name.endsWith('.csv') || file.name.endsWith('.xlsx');
    
    if (!isAllowed) {
        showToast('Error', 'Please select an Excel (.xlsx) or CSV (.csv) file.', 'danger');
        return;
    }

    if (file.size > 50 * 1024 * 1024) {
        showToast('Error', 'File size exceeds 50MB limit', 'danger');
        return;
    }

    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    document.getElementById('uploadProgress').style.display = 'block';
    document.getElementById('uploadResult').style.display = 'none';
    document.getElementById('progressBar').style.width = '0%';

    fetch(`${API_BASE}/upload-file`, {
        method: 'POST',
        body: formData
    })
        .then(async response => {
            updateProgress(100);
            if (response.status === 401) {
                window.location.href = '/login';
                return null;
            }
            const contentType = response.headers.get('content-type') || '';
            const isJson = contentType.includes('application/json');
            const data = isJson ? await response.json() : { status: 'error', message: `Upload failed with HTTP ${response.status}` };

            if (!response.ok) {
                throw new Error(data.message || `Upload failed with HTTP ${response.status}`);
            }

            return data;
        })
        .then(data => {
            if (!data) return;

            document.getElementById('uploadProgress').style.display = 'none';

            if (data.status === 'success') {
                showUploadResult(true, `Successfully processed!
                Added: ${data.added_voters}
                Updated: ${data.updated_voters}`);
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
        .then(response => {
            if (response.status === 401) { window.location.href = '/login'; return null; }
            return response.json();
        })
        .then(data => {
            if (data && data.status === 'success') {
                allBooths = data.booths;
                populateBoothSelect();
            }
        })
        .catch(error => {
            console.error('Error loading booths:', error)
            showToast('Error', 'Could not load booth data.', 'danger');
        });
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
        .then(response => {
            if (response.status === 401) { window.location.href = '/login'; return null; }
            return response.json();
        })
        .then(data => {
            if (data && data.status === 'success') {
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

function createVoterElement(voter) {
    const div = document.createElement('div');
    div.className = 'voter-item';

    // Format the status for display
    const statusBadge = voter.status || 'not_visited';
    const statusDisplay = statusBadge.replace('_', ' ').charAt(0).toUpperCase() +
                         statusBadge.replace('_', ' ').slice(1);

    const houseNumberDisplay = voter.house_number ?
        `<div class="voter-house"><strong>House No:</strong> ${voter.house_number}</div>` : '';
    const phoneDisplay = voter.phone_number ?
        `<div class="voter-phone"><strong>Phone:</strong> ${voter.phone_number}</div>` : '';
    
    const notesDisplay = voter.custom_notes ? 
        `<div class="voter-notes"><strong>Notes:</strong> ${voter.custom_notes}</div>` : '';

    div.innerHTML = `
        <div class="voter-name">${voter.voter_name}</div>
        <div class="voter-id"><strong>ID:</strong> ${voter.voter_id}</div>
        ${houseNumberDisplay}
        <div class="voter-booth"><strong>Booth:</strong> ${voter.booth_number}</div>
        ${phoneDisplay}
        <span class="voter-status ${statusBadge}">${statusDisplay}</span>
        ${notesDisplay}
        <div class="voter-actions">
            <button class="btn btn-sm btn-outline-primary" onclick="openUpdateModal(${voter.id}, '${voter.voter_name.replace(/'/g, "\\'")}', '${voter.voter_id}', '${voter.phone_number || ''}', '${voter.house_number || ''}')">
                <i class="bi bi-pencil"></i> Update
            </button>
            <button class="btn btn-sm btn-outline-success" onclick="markAsVisited(${voter.id})">
                <i class="bi bi-check-circle"></i> Mark Visited
            </button>
        </div>`;

    return div;
}
function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('votersContainer').innerHTML = '';
    document.getElementById('votersCard').style.display = 'none';
    document.getElementById('resultsInfo').style.display = 'none';
    document.getElementById('noDataAlert').style.display = 'block';
}

// ==================== VOTER UPDATES ====================
function openUpdateModal(voterId, voterName, voterId_epic, phoneNumber = '', houseNumber = '') {
    currentVoterId = voterId;
    document.getElementById('voterNameDisplay').value = voterName;
    document.getElementById('voterIdDisplay').value = voterId_epic;
    document.getElementById('phoneInput').value = phoneNumber;
    document.getElementById('houseNumberInput').value = houseNumber;
    document.getElementById('statusSelect').value = 'not_visited';
    document.getElementById('notesInput').value = '';

    const modal = new bootstrap.Modal(document.getElementById('updateModal'));
    modal.show();
}

function saveVoterUpdate() {
    const phone = document.getElementById('phoneInput').value.trim();
    const status = document.getElementById('statusSelect').value;
    const notes = document.getElementById('notesInput').value.trim();
    const houseNumber = document.getElementById('houseNumberInput').value.trim();

    if (!status && !phone && !notes && !houseNumber) {
        showToast('Warning', 'Please provide at least one field to update', 'warning');
        return;
    }

    const payload = {};
    if (phone) payload.phone_number = phone;
    if (houseNumber) payload.house_number = houseNumber;
    if (status) payload.status = status;
    if (notes) payload.custom_notes = notes;

    fetch(`${API_BASE}/voter/${currentVoterId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(response => {
            if (response.status === 401) { window.location.href = '/login'; return null; }
            return response.json();
        })
        .then(data => {
            if (data && data.status === 'success') {
                showToast('Success', 'Voter updated successfully', 'success');
                bootstrap.Modal.getInstance(document.getElementById('updateModal')).hide();

                // Re-run the current search to refresh the list
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
        .then(response => {
            if (response.status === 401) { window.location.href = '/login'; return null; }
            return response.json();
        })
        .then(data => {
            if (data && data.status === 'success') {
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
        .then(response => {
            if (response.status === 401) { window.location.href = '/login'; return null; }
            return response.json();
        })
        .then(data => {
            if (data) populateStats(data);
        })
        .catch(error => console.error('Error loading stats:', error));
}

function populateStats(data) {
    if (data.status === 'success') {
        document.getElementById('totalVoters').textContent = data.total_voters || 0;
        document.getElementById('visitedVoters').textContent = data.visited_voters || 0;
        document.getElementById('totalBooths').textContent = data.total_booths || 0;

        if (data.total_voters === 0) {
            document.getElementById('noDataAlert').style.display = 'block';
        } else {
            document.getElementById('noDataAlert').style.display = 'none';
        }
    }
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
        .then(response => {
            if (response.status === 401) { window.location.href = '/login'; return null; }
            return response.json();
        })
        .then(data => {
            if (data && data.status === 'success') {
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

// ==================== DATA EXPORT ====================
function exportData(type) {
    const url = `${API_BASE}/export?type=${type}`;
    
    // Open in a new tab to handle download
    window.open(url, '_blank');

    showToast('Download', `Exporting all voters as ${type.toUpperCase()}`, 'info');
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
