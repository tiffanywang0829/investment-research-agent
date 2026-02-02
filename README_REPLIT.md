# Deploy to Replit

## Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Replit configuration"
git push
```

## Step 2: Import to Replit

1. Go to https://replit.com
2. Click "Create Repl"
3. Select "Import from GitHub"
4. Paste your GitHub repository URL
5. Click "Import from GitHub"

## Step 3: Set Environment Variables

In Replit, go to the "Secrets" tab (lock icon) and add:

- `GOOGLE_API_KEY` = `AIzaSyCi2leuAQ9pE3Ijbg5FJR4DD3gkbVCbd48`
- `ALPHA_VANTAGE_API_KEY` = `9MUEWOSTIUUG6JEB`
- `GCP_PROJECT_ID` = `gen-lang-client-0942809769`
- `VERTEX_LOCATION` = `us`
- `VERTEX_DATA_STORE_ID` = `jz-invest_1769987456711`

## Step 4: Run

Click the "Run" button in Replit. The agent will start at:
- Development: Your Replit URL (e.g., https://your-repl.username.repl.co)

## Step 5: Access Your Agent

Once running, you can access:
- Web UI: Click the webview in Replit or visit your Repl URL
- API: Use the URL provided in the Replit console

## Notes

- Replit will keep your agent running as long as you have the tab open
- For always-on deployment, you'll need a Replit paid plan ($7/month)
- The agent will auto-restart if it crashes
