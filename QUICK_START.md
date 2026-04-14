# Voter Data Management System - Quick Reference

## System Overview

This is a web application for managing voter data in Veerapandi Constituency (No. 91), Salem.

## Quick Start (30 seconds)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 in your browser.

## Features at a Glance

| Feature | Description |
|---------|-------------|
| **PDF Upload** | Upload voter lists and auto-extract data |
| **Booth Management** | Organize voters by booth numbers |
| **Search** | Find voters by name or ID (EPIC) |
| **Updates** | Mark visitors, add notes, verify info |
| **Statistics** | Track visited vs. unvisited voters |
| **Database** | SQLite for persistent storage |

## File Structure

```
.
├── backend/
│   ├── app.py              # Flask API server
│   ├── database.py         # Database layer
│   ├── pdf_parser.py       # PDF extraction
│   └── requirements.txt    # Python packages
├── frontend/
│   ├── templates/
│   │   └── index.html      # Dashboard
│   └── static/
│       ├── style.css       # Styling
│       └── script.js       # JavaScript
├── uploads/                # Temp file storage
├── README.md               # Full documentation
├── SETUP.md                # Installation guide
└── .github/
    └── copilot-instructions.md  # Dev guide
```

## API Endpoints

**Booths**
- GET `/api/booths` → List all booths

**Voters**
- GET `/api/booth/<id>/voters` → Get voters in booth
- GET `/api/search?q=<term>` → Search voters
- PUT `/api/voter/<id>` → Update voter

**Files**
- POST `/api/upload-pdf` → Upload & parse
- POST `/api/clear-data` → Reset all data

**Stats**
- GET `/api/stats` → Get statistics

## PDF Requirements

✓ Contains voter information
✓ Has booth numbers (numeric)
✓ Has voter IDs in EPIC format: `KKDDSSSSSS` (e.g., KA01A123456)
✓ Has voter names
✓ Max 50MB file size

## Status Codes

- ✅ **visited**: Voter has been visited
- ⏳ **not_visited**: Not yet visited (default)
- ❌ **not_available**: Voter not at location
- 🚫 **no_entry**: Restricted access
- ✓ **verified**: Information verified

## Keyboard Shortcuts

- **Enter** in search field → Perform search
- **Ctrl+R** → Refresh page/reload data

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | `python app.py --port 5001` |
| No voters found | Check PDF format & EPIC ID format |
| CORS error | Ensure backend at http://localhost:5000 |
| Database error | Delete `voters.db` and restart |

## Technology Stack

- Backend: Flask (Python web framework)
- Frontend: Bootstrap 5 (responsive UI)
- Database: SQLite3 (file-based DB)
- PDF: pdfplumber (extraction library)

## Important Notes

⚠️ **Development Only**: No authentication, debug mode on, HTTP only

🔒 **For Production**: Enable authentication, HTTPS, rate limiting, remove debug mode

## Performance

- Indexed searches on: name, voter_id, booth_id
- Handles 100,000+ voters efficiently
- 50MB file upload limit
- Typical booth size: 1,000-5,000 voters

## Contact

For documentation: See README.md
For development: See .github/copilot-instructions.md
For setup: See SETUP.md

---

**Version**: 1.0 | **Updated**: April 2026
