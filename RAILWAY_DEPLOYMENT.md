# 🚀 Railway Deployment Guide

## Fixed Issues ✅

The following has been configured for Railway deployment:

1. ✅ **Procfile** - Tells Railway how to start the app
2. ✅ **runtime.txt** - Specifies Python 3.11
3. ✅ **railway.json** - Railway configuration
4. ✅ **app.py updated** - Uses PORT from environment
5. ✅ **database.py updated** - Uses absolute paths
6. ✅ **UPLOAD_FOLDER** - Fixed path handling

---

## 🔧 How to Deploy on Railway

### Step 1: Ensure Changes Are Pushed to GitHub

```bash
cd "c:\Users\NAVEEN\Desktop\Naveen\New folder (5)"
git add Procfile runtime.txt railway.json backend/
git commit -m "Configure app for Railway deployment"
git push origin main
```

### Step 2: Go to Railway Dashboard

1. Visit: https://railway.app
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**

### Step 3: Select Your Repository

1. Search for: **Veerapandi**
2. Click to select the repository
3. Railway will auto-detect the Python project

### Step 4: Wait for Build

Railway will:
1. ✅ Install Python 3.11
2. ✅ Install packages from requirements.txt
3. ✅ Run Procfile command
4. ✅ Start your Flask app

**Build time: 2-5 minutes**

### Step 5: Get Your URL

Once deployed, you'll see a URL like:
```
https://veerapandi-prod-abc123.railway.app
```

### Step 6: Update Frontend

Edit `frontend/static/script.js` line 6:

Change from:
```javascript
const API_BASE = 'http://localhost:5000/api';
```

To:
```javascript
const API_BASE = 'https://veerapandi-prod-abc123.railway.app/api';
```

### Step 7: Commit Frontend Changes

```bash
git add frontend/static/script.js
git commit -m "Update API URL to Railway backend"
git push origin main
```

### Step 8: Redeploy Netlify

Your Netlify site will auto-redeploy. Done! ✅

---

## 📊 Expected Deployment Timeline

| Step | Time |
|------|------|
| Build Docker image | 30-60 sec |
| Install dependencies | 1-2 min |
| Start Flask app | 10-20 sec |
| **Total** | **2-4 min** |

---

## 🔍 Check Deployment Status

In Railway dashboard:
- ✅ Green = Running
- 🟡 Yellow = Building
- 🔴 Red = Failed

Click on the project to see logs.

---

## 🐛 If Build Fails

### Check the logs:
1. Click your project in Railway
2. Go to **"Deployments"** tab
3. Click the failed deployment
4. View logs to see error

### Common errors:
- **"No module named 'flask'"** - Dependencies not installing
  - Solution: Check `backend/requirements.txt` format
  
- **"Port 5000 in use"** - Environment not setting PORT
  - Solution: Already fixed in app.py

- **"Database error"** - Path issues
  - Solution: Already fixed with absolute paths

---

## ✅ Verify Deployment Works

Once deployed, test:

```bash
# Replace with your Railway URL
curl https://your-railway-url.railway.app/
# Should return HTML dashboard

curl https://your-railway-url.railway.app/api/booths
# Should return {"status": "success", "booths": [], ...}

curl https://your-railway-url.railway.app/api/stats
# Should return statistics
```

---

## 💾 Database Persistence

⚠️ **Important**: Railway's free tier uses ephemeral storage
- Database resets when the app restarts
- Consider upgrading to PostgreSQL for persistent storage
- Or use Railway's paid tier with persistent volumes

For now, SQLite works fine for testing.

---

## 🔄 Updates

After making code changes:
1. Commit and push to GitHub
2. Railway auto-redeploys (usually within 1-2 minutes)
3. No manual action needed

---

## 🎯 Your Deployment Setup

```
GitHub (Repository)
   ↓
Railway (detects Procfile)
   ↓
Installs dependencies from requirements.txt
   ↓
Runs: cd backend && python app.py
   ↓
Flask app running at https://your-url.railway.app
   ↓
Netlify frontend calls API endpoints
   ↓
✅ Full stack working!
```

---

## 📞 If Issues Persist

1. Check Railway build logs
2. Verify `Procfile` syntax (no extra whitespace)
3. Verify `requirements.txt` has all packages
4. Ensure `backend/app.py` exists
5. Check Flask is using the right PORT

---

**Ready to deploy?** Push your changes and Railway will build automatically! 🚀

---

**Last Updated**: April 14, 2026
