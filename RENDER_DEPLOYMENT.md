# Deploy to Render

## Quick Deployment Steps

### 1. Push to GitHub
All code is already on GitHub: https://github.com/nishanth895/leave-management-agent

### 2. Sign Up / Login to Render
- Go to: https://render.com/
- Sign up or login with your GitHub account

### 3. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select repository: **nishanth895/leave-management-agent**
4. Render will auto-detect the `render.yaml` file

### 4. Configure Settings (if manual setup needed)
- **Name:** leave-management-agent
- **Environment:** Python
- **Region:** Singapore (or closest to you)
- **Branch:** main
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
- **Instance Type:** Free

### 5. Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add this variable:
```
Key: GEMINI_API_KEY
Value: your_actual_gemini_api_key_here
```

### 6. Deploy
Click **"Create Web Service"**

Render will:
- Clone your repository
- Install dependencies
- Start your Streamlit app
- Give you a live URL like: `https://leave-management-agent.onrender.com`

### 7. Access Your App
Once deployed (takes 3-5 minutes), you'll get a URL.

**Login Credentials:**
- **Admin:** admin@example.com / admin123
- **Employee:** alice@example.com / password123

---

## Troubleshooting

### If build fails:
1. Check the logs in Render dashboard
2. Verify GEMINI_API_KEY is set correctly
3. Make sure all files are pushed to GitHub

### Database:
- SQLite database will be created automatically on first run
- Data persists on Render's persistent disk

### Free Tier Limitations:
- App sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds to wake up
- 750 hours/month free
- For production, upgrade to paid plan

---

## Features Deployed:
✅ Premium Admin Dashboard with glassmorphism UI
✅ AI Leave Recommendations (Google Gemini)
✅ Employee Self-Service Portal
✅ Leave Analytics & Reports
✅ PDF Export
✅ Real-time Status Updates
✅ Secure Authentication

---

**Deployed App URL:** Will be available after deployment
**Repository:** https://github.com/nishanth895/leave-management-agent
