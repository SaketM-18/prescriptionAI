# Deployment Guide

## Quick Start

### Local Development

1. **Get Google API Key:**
   - Visit: https://aistudio.google.com/
   - Create API key

2. **Create key.json:**
```bash
echo '{"api_key": "your-api-key-here"}' > key.json
```

3. **Install & Run:**
```bash
pip install -r requirements.txt
python app.py
```

4. **Visit:** http://localhost:5000

---

## Production Deployment (Render)

### First Time Setup

1. **Create Render Account:**
   - Visit: https://render.com/
   - Sign up with GitHub

2. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure Service:**
   - **Name:** prescription-ai (or your choice)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. **Add Environment Variable:**
   - Go to "Environment" tab
   - Add variable:
     - **Key:** `GOOGLE_API_KEY`
     - **Value:** your-google-api-key
   - Click "Save Changes"

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - Visit your app URL

---

## Updating the App

### After Making Changes

1. **Commit changes:**
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

2. **Render auto-deploys:**
   - Detects push automatically
   - Rebuilds and redeploys
   - Takes 2-3 minutes

3. **Check deployment:**
   - Go to Render Dashboard
   - Check "Events" tab
   - Wait for "Deploy succeeded"

---

## Environment Variables

### Required:
- `GOOGLE_API_KEY` - Your Google Gemini API key

### Optional:
- `PORT` - Server port (Render sets this automatically)

---

## Troubleshooting

### Issue: "API key not found"
**Solution:** 
- Check Render Dashboard → Environment
- Verify `GOOGLE_API_KEY` is set
- Redeploy if needed

### Issue: "All models failed"
**Solution:**
- Check API quota at https://aistudio.google.com/
- Wait for quota reset (1 hour)
- Or upgrade quota

### Issue: App not loading
**Solution:**
- Check Render logs for errors
- Verify all dependencies in requirements.txt
- Check if build succeeded

---

## Monitoring

### Check Logs:
1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. View real-time logs

### Check Metrics:
1. Go to Render Dashboard
2. Select your service
3. Click "Metrics" tab
4. View CPU, memory, requests

---

## Security Checklist

Before deploying:
- [ ] `key.json` is in `.gitignore`
- [ ] No API keys in code
- [ ] Environment variable set in Render
- [ ] API key restrictions configured (optional)
- [ ] HTTPS enabled (automatic on Render)

---

## Cost

### Render:
- Free tier: 750 hours/month
- Sleeps after 15 min inactivity
- Wakes up on request (cold start)

### Google AI:
- Free tier: 15 requests/min, 1500/day
- Pay-as-you-go: ~$0.00025 per image
- Very affordable for production

---

## Custom Domain (Optional)

1. Go to Render Dashboard
2. Select your service
3. Click "Settings" → "Custom Domain"
4. Add your domain
5. Update DNS records as shown
6. Wait for SSL certificate (automatic)

---

## Backup & Recovery

### Backup:
- Code: Already in GitHub
- Data: Stored in browser localStorage
- No database needed

### Recovery:
- Redeploy from GitHub
- Users' data persists in their browsers

---

## Performance Tips

1. **Enable caching** (already configured)
2. **Optimize images** before upload
3. **Use CDN** for static files (optional)
4. **Monitor API usage** regularly

---

## Support

- **Render Docs:** https://render.com/docs
- **Google AI Studio:** https://aistudio.google.com/
- **Flask Docs:** https://flask.palletsprojects.com/

---

**Last Updated:** 2026-02-21
