# 🐍 Python Installation Guide - Windows

Your Voter Data Management System is ready, but **Python 3.8+ needs to be installed** to run it.

## ⚡ Quick Install Steps

### Step 1: Download Python
Visit: **https://www.python.org/downloads/**

Click the yellow **"Download Python 3.11"** button

### Step 2: Run Installer
1. Open the downloaded installer
2. ✅ **Check "Add Python to PATH"** (IMPORTANT!)
3. Click **"Disable path length limit"** (at the bottom)
4. Click **"Install Now"**
5. Wait for installation to complete

### Step 3: Verify Installation
Open PowerShell and run:
```powershell
python --version
```

Should show: `Python 3.11.x` or similar

### Step 4: Install Dependencies
```powershell
cd "c:\Users\NAVEEN\Desktop\Naveen\New folder (5)\backend"
python -m pip install -r requirements.txt
```

### Step 5: Run Application
```powershell
cd backend
python app.py
```

You should see:
```
Running on http://127.0.0.1:5000
```

### Step 6: Open in Browser
Visit: **http://localhost:5000**

---

## ✅ Verification Checklist

After installation, verify in PowerShell:

```powershell
python --version          # Should show Python 3.8+
python -m pip --version   # Should show pip version
```

---

## 🔧 Troubleshooting

### "Python is not recognized"
- Python may not be in PATH
- Restart PowerShell/Command Prompt
- Or reinstall with "Add Python to PATH" checked

### Still not working?
- Add Python to PATH manually:
  1. Settings > "Edit the system environment variables"
  2. Click "Environment Variables"
  3. Click "New" under "User variables"
  4. Variable name: `PYTHON_PATH`
  5. Variable value: `C:\Users\NAVEEN\AppData\Local\Programs\Python\Python311` (adjust version)
  6. Click OK and restart PowerShell

---

## 📋 Alternative: Portable Python

If you don't want to modify system settings:
- Download portable Python from: https://www.python-portable.org/
- Extract it anywhere
- Use full path when running: `C:\path\to\portable\python.exe app.py`

---

## ⏱️ After Installing Python

```powershell
# Navigate to project
cd "c:\Users\NAVEEN\Desktop\Naveen\New folder (5)"

# Install dependencies
python -m pip install -r backend/requirements.txt

# Run the application
cd backend
python app.py

# Open browser to http://localhost:5000
```

---

**Once Python is installed, come back and run the application!** 🚀
