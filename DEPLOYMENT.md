# Deployment Guide

## Free Deployment Setup (Netlify + Render)

### Architecture
- **Frontend**: Deployed to Netlify (static React app)
- **Backend**: Deployed to Render (Flask API with free tier)

---

## Backend Deployment (Render - Free Tier)

### Step 1: Prepare Your Model
⚠️ **Important**: The `.pkl` model file is NOT in git (excluded by `.gitignore`). You have two options:

**Option A: Upload model manually to Render**
1. After deploying to Render, use their Shell feature or SFTP to upload `random_forest_regressor_model.pkl` to the `backend/` directory

**Option B: Use Git LFS (recommended for team projects)**
```bash
git lfs install
git lfs track "*.pkl"
git add .gitattributes
git add backend/random_forest_regressor_model.pkl
git commit -m "Add model via Git LFS"
git push
```

### Step 2: Deploy Backend to Render

1. **Create Render Account**: Go to https://render.com and sign up (free)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `prediksi-lama-rawat-api` (or your choice)
     - **Region**: Singapore or closest to you
     - **Branch**: `main`
     - **Root Directory**: Leave empty (or set to `backend` if needed)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r backend/requirements.txt`
     - **Start Command**: `gunicorn backend.app_flask:app --bind 0.0.0.0:$PORT --workers 2`
     - **Plan**: Free

3. **Environment Variables** (if needed):
   - You can add `PORT` but Render sets it automatically
   - No other env vars needed for basic setup

4. **Deploy**: Click "Create Web Service"
   - Render will build and deploy (takes 2-5 minutes)
   - You'll get a URL like: `https://prediksi-lama-rawat-api.onrender.com`

5. **Test Backend**:
   ```bash
   curl https://your-backend.onrender.com/schema
   ```

⚠️ **Free Tier Limitations**:
- Backend sleeps after 15 minutes of inactivity (first request after sleep takes ~30 seconds)
- 750 hours/month free (more than enough for personal projects)

---

## Frontend Deployment (Netlify)

### Step 1: Update Backend URL

Before deploying, you'll set an environment variable in Netlify UI (Step 3 below)

### Step 2: Deploy to Netlify

**Option A: Netlify UI (Easiest)**

1. **Create Netlify Account**: Go to https://netlify.com and sign up (free)

2. **Import Project**:
   - Click "Add new site" → "Import an existing project"
   - Choose "Deploy with GitHub"
   - Authorize and select your `Prediksi_Lama_Rawat` repository

3. **Configure Build Settings**:
   - **Base directory**: Leave empty (netlify.toml handles it)
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Publish directory**: `frontend/dist`
   - Click "Show advanced" → "New variable"
     - **Key**: `VITE_API_BASE`
     - **Value**: `https://your-backend.onrender.com` (use your actual Render URL)

4. **Deploy**: Click "Deploy site"
   - Netlify builds and deploys (takes 1-2 minutes)
   - You'll get a URL like: `https://random-name-123.netlify.app`

5. **Custom Domain (Optional)**:
   - Go to "Domain settings" → Add custom domain
   - Or change the Netlify subdomain to something like `prediksi-lama-rawat.netlify.app`

**Option B: Netlify CLI**

```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy (from project root)
netlify deploy --prod

# Follow prompts:
# - Create & configure new site
# - Set build command: cd frontend && npm install && npm run build
# - Set publish directory: frontend/dist
```

Then set environment variable in Netlify UI:
- Go to Site settings → Environment variables
- Add `VITE_API_BASE` = `https://your-backend.onrender.com`
- Trigger a redeploy

### Step 3: Test Full Stack

1. Visit your Netlify URL
2. Fill in the form and click "Predict"
3. You should see the prediction result (the first request to Render may take ~30 seconds if the backend was asleep)

---

## CORS Configuration

The backend is already configured to allow all origins (`CORS(app)` with default settings). For production, you can restrict this:

In `backend/app_flask.py`:
```python
CORS(app, origins=['https://your-netlify-url.netlify.app'])
```

---

## Local Development (After Deployment)

```bash
# Backend (in one terminal)
.\.venv\Scripts\Activate.ps1
python backend/app_flask.py

# Frontend (in another terminal)
cd frontend
npm run dev
```

Frontend will use `http://localhost:8000` by default (from `.env` or hardcoded fallback).

---

## Troubleshooting

### Backend Issues

**"Model not loaded" error**:
- Check that `random_forest_regressor_model.pkl` exists in `backend/` directory on Render
- Use Render Shell to verify: `ls backend/`

**Backend is slow on first request**:
- This is normal for free tier (cold start after sleep)
- Consider upgrading to paid tier or pinging your backend periodically to keep it warm

**Build fails on Render**:
- Check Render logs for missing dependencies
- Ensure `requirements.txt` has all packages

### Frontend Issues

**"Network Error" or CORS**:
- Verify `VITE_API_BASE` environment variable in Netlify is correct (no trailing slash)
- Check Render backend logs for CORS errors
- Ensure backend is running and accessible

**Frontend shows old version**:
- Trigger a new deploy in Netlify UI
- Clear Netlify cache: Site settings → Build & deploy → Clear cache and retry deploy

**API calls fail**:
- Open browser DevTools → Network tab
- Check if requests are going to the correct backend URL
- Verify backend is responding: `curl https://your-backend.onrender.com/schema`

---

## Cost Summary

- **Netlify**: Free tier (100GB bandwidth, unlimited personal projects)
- **Render**: Free tier (750 hours/month, sleeps after inactivity)
- **Total**: $0/month for personal projects

---

## Next Steps

1. Deploy backend to Render (5 minutes)
2. Get backend URL
3. Deploy frontend to Netlify with `VITE_API_BASE` set (3 minutes)
4. Test end-to-end
5. (Optional) Add custom domain
6. (Optional) Set up monitoring (UptimeRobot to ping backend every 5 minutes to prevent sleep)

---

## Alternative Free Hosting Options

**Backend alternatives to Render**:
- Railway (free tier: 500 hours/month)
- Fly.io (free tier: 3 shared VMs)
- Google Cloud Run (free tier: 2 million requests/month)
- PythonAnywhere (free tier with limitations)

**Frontend alternatives to Netlify**:
- Vercel (similar to Netlify)
- GitHub Pages (static only, no build env vars)
- Cloudflare Pages (generous free tier)

All follow similar deployment patterns.
