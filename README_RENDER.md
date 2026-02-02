# Deploy to Render.com

## Quick Steps:

### 1. Sign up at Render.com
Go to https://render.com and sign up (free tier available)

### 2. Connect GitHub
- Click "New +" → "Web Service"
- Connect your GitHub account
- Select repository: `investment-research-agent`

### 3. Configure (Render will auto-detect render.yaml)
Render will automatically use the `render.yaml` configuration.

**Important: Add Environment Variables**
In the Render dashboard, add these environment variables:

- `GOOGLE_API_KEY` = `AIzaSyCi2leuAQ9pE3Ijbg5FJR4DD3gkbVCbd48`
- `ALPHA_VANTAGE_API_KEY` = `9MUEWOSTIUUG6JEB`
- `GCP_PROJECT_ID` = `gen-lang-client-0942809769`
- `VERTEX_LOCATION` = `us`
- `VERTEX_DATA_STORE_ID` = `jz-invest_1769987456711`

### 4. Deploy
Click "Create Web Service" and Render will:
- Install dependencies
- Start your agent
- Give you a public URL (e.g., https://investment-research-agent.onrender.com)

## Free Tier Notes:
- Your service will spin down after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds to wake up
- Perfect for personal use and demos

## Advantages:
✅ Simple GitHub integration
✅ Automatic deployments on git push
✅ Free tier (750 hours/month)
✅ Easy environment variable management
✅ No compatibility issues
