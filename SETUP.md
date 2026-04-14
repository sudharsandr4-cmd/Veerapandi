# Voter Data Management System - Setup Instructions

This file contains detailed setup instructions for the Voter Data Management System.

## Prerequisites

- Python 3.8 or higher installed
- Windows/Mac/Linux OS
- ~50MB disk space (including uploads)

## Installation Steps

### Windows

1. Open Command Prompt (Win + R, type `cmd`)
2. Navigate to the backend folder:
   ```
   cd path\to\backend
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start the application:
   ```
   python app.py
   ```

### macOS / Linux

1. Open Terminal
2. Navigate to the backend folder:
   ```
   cd path/to/backend
   ```
3. Create virtual environment (optional but recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Start the application:
   ```
   python app.py
   ```

## Running the Application

Once installed, the application will be available at:
**http://localhost:5000**

### Accessing the Dashboard

1. Open your web browser
2. Go to: `http://localhost:5000`
3. You should see the Voter Management System dashboard

## Creating a Test PDF

To test the system, you need a voter list PDF. Here's what the PDF should contain:

### Option 1: Table Format (Recommended)

Create a PDF with a table containing:

| Booth Number | Voter ID (EPIC) | Voter Name     |
|--------------|-----------------|----------------|
| 001          | KA01A0001234    | JOHN SMITH     |
| 001          | KA01A0001235    | JANE ELIZABETH |
| 002          | KA01A0002234    | ROBERT JOHNSON |

### Option 2: Text Format

```
Booth: 001
Voter ID: KA01A0001234, Name: JOHN SMITH
Voter ID: KA01A0001235, Name: JANE ELIZABETH

Booth: 002
Voter ID: KA01A0002234, Name: ROBERT JOHNSON
```

### Voter ID Format

Voter IDs should follow the EPIC (Electoral Photo Identity Card) format:
- Format: `KKDDSSSSSS` (Example: `KA01A0001234`)
  - KK = State code (2 letters, e.g., KA for Karnataka, TN for Tamil Nadu)
  - DD = District code (2 digits)
  - A = Additional digit
  - SSSSSS = Serial number (6 digits or alphanumeric)

## Workflow

### 1. First Time Setup
- [ ] Install Python dependencies
- [ ] Run the application
- [ ] Verify it opens at http://localhost:5000

### 2. Upload Sample Data
- [ ] Create a test PDF with voter information
- [ ] Go to "Upload Voter List" section
- [ ] Upload the PDF
- [ ] Verify data appears in the system

### 3. Test Features
- [ ] Select a booth from dropdown
- [ ] Search for voters by name
- [ ] Search for voters by Voter ID
- [ ] Click "Update" button on a voter
- [ ] Update status and notes
- [ ] Mark voter as visited
- [ ] Check statistics

## Database Reset

To start fresh and clear all data:

1. In the application, click "Clear All Data" button in the Actions section
2. Or delete the `voters.db` file and restart the application

## Stopping the Application

To stop the Flask server:
- Press `Ctrl + C` in the terminal/command prompt where it's running

## Common Issues

### "Address already in use"
- Another application is using port 5000
- Stop the other application or modify the port in `app.py`

### "Module not found" error
- Python dependencies not installed
- Run: `pip install -r requirements.txt`

### PDF won't upload
- File is too large (>50MB)
- File is not a PDF
- PDF doesn't contain structured voter data

### No data extracted from PDF
- PDF format not recognized
- Voter IDs don't match EPIC format
- Table structure not detected
- Try a different PDF or ensure clear columns

## Next Steps

1. Upload a voter list PDF
2. Browse voters by booth
3. Search for specific voters
4. Update voter information as needed
5. Track visited/unvisited counts

## Documentation

- See `README.md` for full feature documentation
- See `.github/copilot-instructions.md` for development guide

## Support

For more detailed information:
- Check README.md
- Review the API endpoints in app.py
- Ensure PDF format matches examples above

---

**Setup Guide Version**: 1.0
**Last Updated**: April 2026
