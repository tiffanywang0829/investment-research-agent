# Setup Google Cloud Authentication for Render

To enable Vertex AI Search in production, you need to provide Google Cloud credentials.

## Step 1: Create Service Account

1. Go to https://console.cloud.google.com/iam-admin/serviceaccounts
2. Select project: ``
3. Click "Create Service Account"
4. Name: ``
5. Click "Create and Continue"

## Step 2: Grant Permissions

Add these roles:

- `Discovery Engine Viewer` (for Vertex AI Search)
- `Discovery Engine User` (for querying data stores)

Click "Continue" → "Done"

## Step 3: Create JSON Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON"
5. Download the JSON file

## Step 4: Add to Render

1. Go to your Render dashboard
2. Select your service
3. Go to "Environment" tab
4. Add new environment variable:
   - **Key**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - **Value**: Paste the ENTIRE contents of the JSON file

## Step 5: Update Agent Code

The agent needs to be updated to use the JSON credentials from the environment variable instead of relying on local gcloud auth.

## Step 6: Redeploy

After adding the credentials, trigger a manual deploy in Render.
