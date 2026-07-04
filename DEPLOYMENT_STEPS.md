# 🚀 Deployment Steps for Leave Management Agent

## Error You're Seeing:
"You do not have access to this app or it does not exist"

This means the app needs to be created first on Streamlit Cloud.

---

## ✅ Solution - Follow These Steps:

### Step 1: Push Code to GitHub

Open **Command Prompt** or **Git Bash** and run:

```bash
cd "C:\Users\siban\OneDrive\Desktop\Leave management Agent"
git status
git push origin main
```

**If push fails**, try:
```bash
git push -u origin main --force
```

---

### Step 2: Deploy on Streamlit Cloud

1. **Go to:** https://share.streamlit.io

2. **Sign in** with your GitHub account (nishanth895)

3. Click the **"Create app"** or **"New app"** button

4. **Fill in the form:**
   - **Repository:** Select `nishanth895/leave-management-agent`
   - **Branch:** `main`
   - **Main file path:** `app.py`

5. Click **"Advanced settings"** (optional)
   - Add secrets if needed:
     ```
     GEMINI_API_KEY = "your-api-key-here"
     ```
   - Get key from: https://aistudio.google.com/app/apikey

6. Click **"Deploy"** button

7. Wait 2-3 minutes for deployment

---

### Step 3: Access Your App

After deployment completes, you'll get a URL like:
```
https://leave-management-agent.streamlit.app
```

Or:
```
https://nishanth895-leave-management-agent-app-xxxxx.streamlit.app
```

---

## 🔐 Default Login Credentials:

**Admin:**
- Email: `admin@example.com`
- Password: `admin123`

**Employee:**
- Email: `alice@example.com`
- Password: `password123`

---

## ❓ Common Issues & Fixes:

### Issue 1: "Repository not found"
- Make sure you're signed in with the correct GitHub account
- Check if repository is public (not private)

### Issue 2: "App keeps crashing"
- Check the logs in Streamlit Cloud
- Make sure all files are pushed to GitHub
- Verify `requirements.txt` is present

### Issue 3: "Can't push to GitHub"
- Check if remote URL is correct: `git remote -v`
- Try: `git push -u origin main --force`

---

## 📝 Checklist Before Deployment:

- [x] All code is committed
- [x] `requirements.txt` exists
- [x] `app.py` is the main file
- [x] `.streamlit/config.toml` is configured
- [ ] Code is pushed to GitHub
- [ ] App is created on Streamlit Cloud

---

## 🆘 Still Having Issues?

1. Check GitHub repository: https://github.com/nishanth895/leave-management-agent
2. Verify all files are there
3. Try redeploying from Streamlit Cloud dashboard
4. Check Streamlit Cloud logs for errors

---

**Good luck! 🎉**
