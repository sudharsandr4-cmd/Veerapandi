# Voter Management Enhancements TODO

## Approved Plan Steps (Breakdown)

### Step 1: Update requirements.txt (add pandas, openpyxl)
- [x] Edit requirements.txt

### Step 2: Database Schema Migration
- [x] Edit backend/database.py (add phone_number to CREATE TABLE)
- [x] Add phone_number to SELECT queries in search_voters, get_voters_by_booth
- [ ] Manual DB migration: cd backend && sqlite3 voters.db \"ALTER TABLE voters ADD COLUMN phone_number TEXT;\"

### Step 3: Backend Updates
- [x] Edit backend/app.py:
  * Update update_voter endpoint to handle phone_number
  * Add /api/export endpoint (CSV/Excel with filters: all/visited/remaining)
  * Modify upload_pdf to accept/use manual filename from form
- [x] Edit backend/database.py: 
  * Add phone_number to update_voter
  * Extend search_voters to LIKE on phone_number
  * Update get_voter_stats if needed

### Step 4: Frontend UI Updates\n- [x] Edit frontend/templates/index.html:\n  * Add filename input to upload section\n  * Add phone_number input to update modal\n  * Add export buttons (CSV/Excel dropdown for all/visited/remaining)\n- [x] Edit frontend/static/script.js:\n  * Include filename in upload FormData\n  * Add phone_number to update payload & voter display\n  * Add export button handlers (fetch Blob download)\n- [x] Edit frontend/static/style.css: Style new elements (phone input, export btns)

### Step 5: Testing & Followup
- [ ] Install deps: pip install -r requirements.txt
- [ ] Run migration command
- [ ] Test full flow: upload (manual name), search (name/phone), update phone/status, export CSV/Excel
- [ ] Restart server

**Progress: Backend complete (Step 3 done). Current Step: 4/5**

**Backend ready. Run migration, install deps, test backend endpoints, then proceed to frontend.**

