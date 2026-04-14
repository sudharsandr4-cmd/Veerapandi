# Voter Data Management System
## Veerapandi Constituency (No. 91), Salem

A web-based application for managing voter data by uploading official voter list PDFs and creating a searchable, updateable database.

---

## Features

✅ **PDF Data Extraction** - Automatically extract voter information from PDF files using pdfplumber
✅ **Booth-Level Organization** - Automatically categorize voters by booth number
✅ **Search Functionality** - Search voters by name or Voter ID (EPIC)
✅ **Voter Updates** - Mark voters as visited, add custom notes, verify information
✅ **SQLite Database** - Persistent data storage
✅ **Responsive Dashboard** - Bootstrap-based mobile-friendly interface
✅ **Real-time Statistics** - Track visited/unvisited voters

---

## Technical Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **PDF Parsing**: pdfplumber
- **Database**: SQLite3
- **API**: RESTful API with CORS support

---

## Project Structure

```
voter-management-system/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── database.py            # Database models and operations
│   ├── pdf_parser.py          # PDF extraction logic
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── templates/
│   │   └── index.html         # Main dashboard HTML
│   └── static/
│       ├── style.css          # Dashboard styling
│       └── script.js          # Frontend logic
├── uploads/                   # Temporary PDF storage
└── voters.db                  # SQLite database (auto-created)
```

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Initialize Database (Automatic)

The database is created automatically on first run of the Flask app.

### Step 3: Run the Application

```bash
cd backend
python app.py
```

The application will start at: **http://localhost:5000**

---

## Usage Guide

### 1. Upload Voter List PDF

1. Go to **Upload Voter List** section
2. Click on the upload area or drag-and-drop a PDF file
3. The system will automatically extract:
   - Voter Name
   - Voter ID (EPIC Number)
   - Booth Number

### 2. View Voters by Booth

1. Select a booth from the **Booth Selection** dropdown
2. All voters in that booth will be displayed
3. View statistics for each booth

### 3. Search for Voters

1. Enter voter name or EPIC ID in the search box (minimum 2 characters)
2. Optionally select a specific booth to narrow results
3. Click **Search** button or press Enter

### 4. Update Voter Information

1. Click the **Update** button next to each voter
2. Choose a status:
   - **Not Visited** - Default status
   - **Visited** - Mark as contacted
   - **Not Available** - Voter not at location
   - **No Entry** - Restricted access
   - **Verified** - Information verified
3. Add optional custom notes
4. Click **Save Changes**

### 5. Mark Voters as Visited

- Click **Mark Visited** button for quick status update
- Use the **Update** button for more detailed information

---

## PDF Format Requirements

The PDF should contain voter information in one of these formats:

### Table Format (Recommended)
| Booth | Voter ID (EPIC) | Voter Name |
|-------|-----------------|-----------|
| 01 | KA01A1234567 | John Doe |
| 01 | KA01A1234568 | Jane Smith |

### Text Format
```
Booth: 01
Voter ID: KA01A1234567, Voter Name: John Doe
Voter ID: KA01A1234568, Voter Name: Jane Smith
```

**Expected Voter ID Format**: Starts with 2-letter state code (e.g., KA, TN), followed by district and numeric identifier

---

## Database Schema

### Booths Table
```sql
CREATE TABLE booths (
    id INTEGER PRIMARY KEY,
    booth_number TEXT UNIQUE,
    booth_name TEXT,
    created_at TIMESTAMP
);
```

### Voters Table
```sql
CREATE TABLE voters (
    id INTEGER PRIMARY KEY,
    voter_id TEXT UNIQUE,           -- EPIC Number
    voter_name TEXT,
    booth_id INTEGER,
    booth_number TEXT,
    status TEXT,                     -- visited, not_visited, etc.
    custom_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (booth_id) REFERENCES booths(id)
);
```

---

## API Endpoints

### Booths
- `GET /api/booths` - Get all booths with voter count

### Voters
- `GET /api/booth/<id>/voters` - Get voters in a booth
- `GET /api/search?q=<term>&booth_id=<id>` - Search voters
- `PUT /api/voter/<id>` - Update voter information

### File Upload
- `POST /api/upload-pdf` - Upload and parse voter list PDF

### Statistics
- `GET /api/stats` - Get overall statistics
- `POST /api/clear-data` - Clear all data (reset)

---

## Configuration

### File Size Limit
- Maximum PDF file size: **50MB**
- Configured in `backend/app.py`

### Search Parameters
- Minimum search term length: **2 characters**
- Case-insensitive search

### Database
- Database file: `voters.db` (in backend directory root)
- Automatically created on first run

---

## Troubleshooting

### Issue: "ModuleNotFoundError" when running app.py
**Solution**: Make sure you've installed dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Issue: PDF parsing extracts no data
**Solution**: 
- Ensure PDF contains structured voter information
- Check that voter IDs follow EPIC format (e.g., KA01A1234567)
- PDF should have clear columns or marked sections for voter data

### Issue: Database locked error
**Solution**: 
- Make sure only one instance of the app is running
- Delete `voters.db` and restart the app to reset database

### Issue: "CORS error" in browser console
**Solution**: Ensure backend is running at `http://localhost:5000`

---

## Performance Notes

- Searches are indexed on voter name, voter ID, and booth ID for fast queries
- Database automatically creates indexes on startup
- Suitable for up to 100,000+ voters per database

---

## Security Considerations

⚠️ **For Production Use**:
1. Disable Flask debug mode: `debug=False`
2. Use environment variables for configuration
3. Implement user authentication
4. Add data validation and sanitization
5. Use HTTPS for data transmission
6. Implement rate limiting on API endpoints
7. Regular database backups

---

## Future Enhancements

- 🔐 User authentication & role-based access
- 📊 Advanced reporting and analytics
- 🔄 Data import/export (CSV, Excel)
- 📱 Mobile app
- 🗺️ Booth location mapping
- 📧 Bulk communication features
- 🎯 Campaign tracking

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation
3. Check Flask and pdfplumber documentation

---

## License

This project is for electoral management purposes in Veerapandi Constituency.

---

**Last Updated**: April 2026
**Version**: 1.0
