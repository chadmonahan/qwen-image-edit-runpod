# Quick Setup Guide - Qwen Image Edit 2511 on RunPod

## Overview
This guide sets up Qwen-Image-Edit-2511 on RunPod without needing to download/upload the massive model files locally.

## Prerequisites
- RunPod account with credits
- GitHub account (for code hosting)

---

## Step 1: Create Network Volume (for Model Storage)

1. Go to: https://www.runpod.io/console/serverless/user/storage
2. Click **"+ Network Volume"**
3. Configure:
   - **Name**: `qwen-models`
   - **Size**: 30 GB
   - **Region**: US-East (or your preferred region)
4. Click **"Create"**
5. Wait for it to provision (~1 minute)

**Why?** The model is ~15-20GB. The network volume stores it persistently so it doesn't re-download on every cold start.

---

## Step 2: Upload Code to GitHub

### Option A: Create New Repository
1. Go to https://github.com/new
2. Repository name: `qwen-image-edit-runpod`
3. Set to **Public**
4. Click "Create repository"
5. Upload these files from `/Users/chadmonahan/GitHub/PersonalMedia/runpod-setup/`:
   - `handler.py`
   - `Dockerfile`
   - `requirements.txt`

### Option B: Use Command Line
```bash
cd /Users/chadmonahan/GitHub/PersonalMedia/runpod-setup
git init
git add handler.py Dockerfile requirements.txt
git commit -m "Initial Qwen Image Edit 2511 setup"
gh repo create qwen-image-edit-runpod --public --source=. --push
```

**Copy your GitHub repo URL** (e.g., `https://github.com/yourusername/qwen-image-edit-runpod`)

---

## Step 3: Create RunPod Serverless Endpoint

1. Go to: https://www.runpod.io/console/serverless
2. Click **"+ New Endpoint"**

### Basic Configuration

**Container Configuration:**
- **Container Image**: Leave blank for now, we'll use GitHub
- **Docker Build**: Enable this option
- **GitHub Repository URL**: Paste your repo URL from Step 2
- **GitHub Branch**: `main`
- **Dockerfile Path**: `Dockerfile` (default)

**Endpoint Settings:**
- **Endpoint Name**: `Qwen Image Edit 2511`
- **GPU Type**: Select **RTX A5000 (24GB)** or **A40 (48GB)**
  - A5000: Cheaper (~$0.50/hr)
  - A40: More headroom (~$0.79/hr)

**Workers:**
- **Min Workers**: 0 (scales to zero when idle - saves money!)
- **Max Workers**: 2 (adjust based on your needs)
- **GPUs per Worker**: 1
- **Idle Timeout**: 5 seconds
- **Max Job Duration**: 600 seconds (10 minutes)

**Advanced Settings:**
- **Network Volume**: Select `qwen-models` (the volume you created)
- **Volume Mount Path**: `/runpod-volume`

### Build Process
3. Click **"Deploy"**
4. RunPod will:
   - Clone your GitHub repo
   - Build the Docker image (takes ~5-10 minutes)
   - Deploy the endpoint

5. Monitor build progress in the "Builds" tab
6. Once build completes, endpoint status will show "Ready"

---

## Step 4: Get Your Endpoint ID

1. After deployment, go to your endpoint details
2. Find the **Endpoint ID** (format: `xxxxxxxxxx`)
3. Copy it - you'll need this for your application

Example endpoint URL format:
```
https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync
```

---

## Step 5: Update Application Configuration

Update your endpoint ID in two places:

### File 1: `PersonalMedia.Blazor.Server/appsettings.json`
```json
"RunPod": {
  "EndpointId": "YOUR_ENDPOINT_ID_HERE",
  "ApiKey": "YOUR_API_KEY_HERE",
  "ModelParameters": {
    "model": "qwen-image-edit",
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 40
  }
}
```

### File 2: `PersonalMedia.Functions/local.settings.json`
```json
"RunPod:EndpointId": "YOUR_ENDPOINT_ID_HERE",
"RunPod:ApiKey": "YOUR_API_KEY_HERE"
```

**Get your API Key:**
1. Go to https://www.runpod.io/console/serverless/user/settings
2. Copy your API Key
3. Add it to the config files above

---

## Step 6: Test the Endpoint

### Test in RunPod Dashboard (Recommended First)

1. Go to your endpoint in RunPod console
2. Click **"Test"** or **"Requests"** tab
3. Send a test request:

```json
{
  "input": {
    "prompt": "Add stylish sunglasses to the person",
    "image": "https://chadmonahan.blob.core.windows.net/personal-media/pose.png",
    "num_inference_steps": 40,
    "true_cfg_scale": 4.0,
    "guidance_scale": 1.0,
    "seed": 0
  }
}
```

4. Wait for response (~15-60 seconds)
   - **First run (cold start)**: 30-60 seconds (downloads model to volume)
   - **Subsequent runs (warm)**: 10-20 seconds

Expected response:
```json
{
  "delayTime": 1234,
  "executionTime": 15678,
  "id": "job-id-here",
  "status": "COMPLETED",
  "output": {
    "image_url": "data:image/png;base64,iVBORw0KGg...",
    "image": "data:image/png;base64,iVBORw0KGg...",
    "prompt": "Add stylish sunglasses to the person",
    "model": "qwen-image-edit-2511",
    "status": "completed"
  }
}
```

### Test from Your Application

Once the RunPod test works:
1. Update your config files with the endpoint ID and API key
2. Run your Blazor app
3. Navigate to `/runpod-test`
4. Select "Pose Test Image"
5. Enter a prompt
6. Click "Run Test"

---

## Troubleshooting

### Build Fails
- Check GitHub repo is public
- Verify all files (handler.py, Dockerfile, requirements.txt) are in repo root
- Check build logs in RunPod dashboard for specific errors

### Cold Start Takes Too Long
- Verify network volume is attached
- Check volume has enough space (30GB)
- First cold start will download ~15GB model (can take 5-10 minutes)
- Subsequent cold starts should be ~30 seconds

### Out of Memory Errors
- Upgrade GPU to A40 (48GB) or A100 (80GB)
- The model needs ~16GB VRAM minimum

### Request Timeouts
- Increase "Max Job Duration" in endpoint settings
- Check RunPod logs for specific errors
- Verify image URL is accessible

### Model Not Found
- Wait for first cold start to complete (can take 10 minutes)
- Check network volume has enough space
- Verify TRANSFORMERS_CACHE path is `/runpod-volume/huggingface-cache`

---

## Cost Estimation

**Network Volume:**
- 30GB × $0.10/GB/month = **$3/month** (one-time setup)

**Compute (when running):**
- RTX A5000: ~$0.50/hr active, ~$0.14/hr idle
- A40: ~$0.79/hr active, ~$0.22/hr idle

**Example monthly cost (light usage):**
- 100 requests × 20 seconds each = ~33 minutes runtime
- 33 min × $0.50/hr = **$0.28**
- Network volume = **$3.00**
- **Total: ~$3.28/month**

With Min Workers = 0, you only pay when processing requests!

---

## Next Steps

1. ✅ Complete Steps 1-6 above
2. Test with different prompts
3. Monitor performance in RunPod dashboard
4. Adjust GPU type/workers based on your usage
5. (Optional) Implement image upload to Azure Storage for production

## Support

- **RunPod Docs**: https://docs.runpod.io/
- **Qwen Docs**: https://github.com/QwenLM/Qwen-Image
- **Issues**: Check RunPod logs and build output for errors
