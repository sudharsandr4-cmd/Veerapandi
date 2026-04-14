# Voter Data Management System - Development Instructions

## ✅ Workspace Setup Complete

### Project Status
- [x] Project structure created
- [x] All source files generated
- [x] Documentation complete
- [x] Configuration files ready
- [ ] Python dependencies (manual setup required)
- [ ] Application tested

### Quick Start

#### Prerequisites
Ensure Python 3.8+ is installed on your system:
```bash
python --version
# Should show: Python 3.8.x or higher
```

#### Installation (First Time Only)
```bash
# Install Python dependencies
cd backend
python -m pip install -r requirements.txt
# Or
pip install -r requirements.txt
```

#### Running the Application
```bash
# Start Flask backend (from backend directory)
cd backend
python app.py
```

The application will be available at: **http://localhost:5000**

## Project Overview

**Purpose**: Web application for managing voter data in Veerapandi Constituency (No. 91), Salem

**Key Features**:
- PDF voter list upload and parsing
- Booth-level voter organization
- Search by name or voter ID (EPIC)
- Voter record updates and notes
- SQLite database persistence
- Bootstrap responsive dashboard

## Architecture

```
Frontend (Bootstrap 5)
    ↓
API (Flask REST)
    ↓
Database (SQLite)
    ↓
PDF Parser (pdfplumber)
```

## Development Workflow

1. **Backend**: Modify Python files in `backend/` directory
2. **Frontend**: Modify HTML/CSS/JS in `frontend/` directory
3. **Database**: Schema defined in `backend/database.py`
4. **PDF Parsing**: Logic in `backend/pdf_parser.py`

## Key Technologies

- **Backend**: Python Flask (RESTful API)
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Database**: SQLite3
- **PDF Processing**: pdfplumber
- **API Communication**: Fetch API (JSON)

## Important Files

| File | Purpose |
|------|---------|
| `backend/app.py` | Main Flask application & API routes |
| `backend/database.py` | Database models and operations |
| `backend/pdf_parser.py` | PDF extraction & parsing logic |
| `frontend/templates/index.html` | Main dashboard HTML |
| `frontend/static/style.css` | Dashboard styling |
| `frontend/static/script.js` | Frontend JavaScript logic |

## Common Development Tasks

### Adding a New API Endpoint
1. Define the route in `backend/app.py`
2. Add database function in `backend/database.py` if needed
3. Call from `frontend/static/script.js`

### Modifying Database Schema
1. Update `database.py` init_db() function
2. Create migration or clear `voters.db` to recreate
3. Restart application

### Styling Changes
- Edit `frontend/static/style.css`
- Changes reflect immediately in browser (refresh page)

### Frontend Logic Changes
- Edit `frontend/static/script.js`
- Changes reflect after page refresh

## Testing

### Manual Testing Checklist
- [ ] Upload PDF and verify voter extraction
- [ ] Search by voter name
- [ ] Search by voter ID (EPIC)
- [ ] Update voter information
- [ ] Mark voter as visited
- [ ] View booth-level statistics
- [ ] Test on mobile screen sizes
- [ ] Verify CORS functionality

### Test PDF Format
Ensure test PDFs contain:
- Voter ID in EPIC format (e.g., KA01A1234567)
- Voter names (text)
- Booth numbers (numeric)

## Debugging

### Enable Flask Debug Mode
Already enabled in `app.py`:
```python
app.run(debug=True)
```

### Check Browser Console
Open DevTools (F12) → Console tab for JavaScript errors

### Database Inspection
```bash
sqlite3 voters.db
sqlite> SELECT * FROM voters LIMIT 5;
```

## Performance Tips

- Searches use indexed columns (name, voter_id, booth_id)
- Database queries optimized with WHERE clauses
- Frontend pagination not needed for typical booth sizes
- File uploads limited to 50MB max

## Security Reminders

⚠️ Current implementation is for development/local use:
- ❌ No authentication
- ❌ Debug mode enabled
- ❌ No HTTPS
- ❌ No rate limiting

For production deployment, implement:
- User authentication
- HTTPS encryption
- Rate limiting
- Input validation
- Environment-based config

## Troubleshooting

**Port already in use**: Flask uses port 5000. Kill process or use `app.run(port=5001)`

**PDF not parsing**: Verify PDF has structured data with voter IDs in EPIC format

**Database errors**: Delete `voters.db` and restart app to reset

**CORS errors**: Ensure backend runs at `http://localhost:5000`

## Dependencies

See `backend/requirements.txt` for complete list:
- Flask 2.3.3
- pdfplumber 0.10.3
- Flask-CORS 4.0.0

## File Locations

- Backend code: `backend/`
- Frontend code: `frontend/`
- Database file: `voters.db` (created at runtime)
- Uploads: `uploads/` (temporary storage)

## Contact & Support

For questions about implementation:
1. Check README.md for feature documentation
2. Review API endpoint documentation
3. Check pdfplumber docs for PDF parsing issues

---

**Development Version**: 1.0
**Last Updated**: April 2026
