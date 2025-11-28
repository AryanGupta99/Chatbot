# Deployment Instructions - KB Updates

## What Was Pushed

### Knowledge Base Updates
1. **SelfCare Portal Password Reset Guide** (`data/kb/01_password_reset.md`)
   - Official SelfCare Portal workflow
   - Google Authenticator enrollment
   - Portal URL: https://Selfcare.acecloudhosting.com

2. **Disk Storage Guide** (`data/kb/02_disk_storage_upgrade.md`)
   - Cleanup steps (temp files, cache, etc.)
   - Storage upgrade pricing ($28-$120/month)
   - Ticket creation workflow with ETA

### Deployment Configuration
- Updated `render.yaml` to automatically build KB on deployment
- Created `build_kb_for_deploy.py` for non-interactive KB building
- Render will rebuild the vector store with new content

## Render Deployment Status

Render should automatically deploy when it detects the GitHub push.

### Check Deployment Status:
1. Go to https://dashboard.render.com
2. Find your service: `acebuddy-api`
3. Check the "Events" tab for deployment progress

### Expected Build Process:
```
1. Install dependencies (pip install -r requirements.txt)
2. Build KB chunks from updated guides
3. Rebuild vector store with new embeddings
4. Start API server
```

Build time: ~5-10 minutes (due to vector store rebuild)

## Testing on SalesIQ

Once deployed, test these queries in your SalesIQ chat widget:

### Test 1: Password Reset
**Query:** "I forgot my password"

**Expected Response Should Include:**
- SelfCare Portal mention
- https://Selfcare.acecloudhosting.com URL
- Google Authenticator enrollment steps
- Security question setup

### Test 2: Disk Storage
**Query:** "My C drive is showing red" or "My disk is full"

**Expected Response Should Include:**
- Cleanup steps first (temp files, cache, disk cleanup tool)
- Instructions to check disk space
- Storage upgrade pricing if needed
- Ticket creation offer

### Test 3: Storage Pricing
**Query:** "How much does storage upgrade cost?"

**Expected Response Should Include:**
- 200GB – $120/Month
- 100GB – $60/Month
- 80GB – $50/Month
- 60GB – $40/Month
- 40GB – $28/Month

## Troubleshooting

### If Deployment Fails:
1. Check Render logs for errors
2. Most likely issue: OpenAI API key not set
3. Verify environment variable `OPENAI_API_KEY` is set in Render dashboard

### If Responses Are Still Old:
1. Render might be using cached data
2. Manually trigger a rebuild in Render dashboard
3. Or clear the deployment cache

### If Build Takes Too Long:
- Vector store rebuild requires generating embeddings for 797 chunks
- This can take 5-10 minutes on Render's free tier
- Be patient, it's a one-time process per deployment

## Manual Deployment Trigger

If auto-deployment doesn't start:
1. Go to Render dashboard
2. Click on your service
3. Click "Manual Deploy" → "Deploy latest commit"

## Verification

After deployment completes:
1. Check API health: `https://your-render-url.onrender.com/health`
2. Test a query: `POST https://your-render-url.onrender.com/chat`
3. Test via SalesIQ widget with the queries above

## Next Steps

1. Monitor first few real user interactions
2. Collect feedback on response accuracy
3. Iterate on KB content if needed
4. Consider adding more specific guides based on common queries
