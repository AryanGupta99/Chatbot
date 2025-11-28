# How to Add OPENAI_MODEL to Render

## Step-by-Step Guide with Screenshots

### Step 1: Go to Render Dashboard
1. Open: https://dashboard.render.com
2. Log in to your account

### Step 2: Select Your Service
1. Click on your service: **acebuddy-api**
2. You should see your service dashboard

### Step 3: Go to Environment Tab
1. Look at the left sidebar
2. Click on **"Environment"** (it's between "Settings" and "Events")

### Step 4: Add New Environment Variable
1. Scroll down to the "Environment Variables" section
2. You should see existing variables like:
   - `OPENAI_API_KEY`
   - `PYTHON_VERSION`
   - `API_SECRET_KEY`
   - etc.

3. Click the **"Add Environment Variable"** button (blue button at the bottom)

### Step 5: Add OPENAI_MODEL
1. In the **Key** field, type: `OPENAI_MODEL`
2. In the **Value** field, type: `gpt-4o-mini`
3. Click **"Save Changes"** button

### Step 6: Render Will Redeploy
1. Render will automatically trigger a new deployment
2. Wait 5-10 minutes for deployment to complete
3. Check the "Events" tab to see deployment progress

---

## Alternative: If Environment Tab Doesn't Exist

If you don't see an "Environment" tab, try this:

### Option A: Use render.yaml (Recommended)
The environment variables are defined in your `render.yaml` file. Let me update it for you.

### Option B: Manual Deploy with Environment Variable
1. Go to your service dashboard
2. Click **"Manual Deploy"** dropdown
3. Select **"Deploy latest commit"**
4. Before deploying, you can add environment variables in the dashboard

---

## Current Environment Variables You Should Have:

```
OPENAI_API_KEY=sk-proj-... (your key)
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
API_HOST=0.0.0.0
API_PORT=8000
PYTHON_VERSION=3.11.9
```

---

## Verification

After deployment, check if the model is being used:
1. Test a query in SalesIQ
2. Check OpenAI usage dashboard
3. You should see `gpt-4o-mini` in the model usage

---

## Cost Comparison

### Before (if using gpt-4-turbo-preview):
- Cost: $10 per 1M input tokens
- 1000 queries ≈ $5

### After (gpt-4o-mini):
- Cost: $0.15 per 1M input tokens
- 1000 queries ≈ $0.08
- **66x cheaper!**

---

## Troubleshooting

### If you can't find Environment tab:
1. Make sure you're looking at the **service** (acebuddy-api), not the dashboard home
2. The tab should be in the left sidebar
3. If still not visible, the variables might be in render.yaml

### If deployment fails:
1. Check the "Logs" tab for errors
2. Make sure `OPENAI_API_KEY` is still set correctly
3. Verify the model name is exactly: `gpt-4o-mini` (no typos)

---

## Need Help?

If you still can't find it, send me a screenshot of your Render dashboard and I'll guide you through it!
