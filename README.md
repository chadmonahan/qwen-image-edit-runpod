# RunPod Serverless Setup for Qwen Image Edit

## Overview
This setup deploys the Qwen2-VL-7B-Instruct model as a RunPod serverless endpoint for image editing tasks.

## Files
- `handler.py` - Python handler that processes image editing requests
- `Dockerfile` - Container definition for the serverless worker
- `requirements.txt` - Python dependencies

## Setup Steps

### Option A: Using RunPod's Infrastructure (Recommended - No Local Docker Build Needed)

Since the model is large (~15-20GB), we'll use RunPod's build service to handle everything:

**Step 1: Create a GitHub Repository (or use existing)**
1. Create a new public GitHub repo (e.g., `qwen-image-edit-runpod`)
2. Upload these files:
   - `handler.py`
   - `Dockerfile`
   - `requirements.txt`

**Step 2: Create Network Volume**
1. Go to https://www.runpod.io/console/serverless/user/storage
2. Click "Create Network Volume"
3. Name: `qwen-models`
4. Size: 30GB (to fit the ~15GB model + cache)
5. Region: Choose closest to you (e.g., US-East)
6. Click "Create"

**Step 3: Create Serverless Endpoint with Auto-Build**

1. Go to https://www.runpod.io/console/serverless
2. Click "New Endpoint"
3. Configure the endpoint:

   **Basic Settings:**
   - Name: `Qwen Image Edit`
   - Container Image: `yourusername/qwen-image-edit:latest`

   **GPU Configuration:**
   - Select GPU: A40 (48GB) or A6000 (48GB) recommended
     - Qwen2-VL-7B needs ~16GB VRAM, so A40/A6000 provides headroom
     - Can use RTX 4090 (24GB) if budget-conscious
   - Workers:
     - Min Workers: 0 (auto-scale to zero when idle)
     - Max Workers: 3 (adjust based on expected load)

   **Advanced Settings:**
   - Max Execution Time: 300 seconds (5 minutes)
   - Idle Timeout: 5 seconds
   - Network Volume: Optional (25GB+ for model caching)
     - Recommended: Attach a network volume to persist the model
     - Path: `/runpod-volume`
     - This prevents re-downloading the 15GB model on every cold start

4. Click "Create Endpoint"
5. Copy the Endpoint ID (format: `xxxxxxxxxx`)

### 3. Update Your Configuration

Update your endpoint ID in the application configuration files:

**File: `PersonalMedia.Blazor.Server/appsettings.json`**
```json
"RunPod": {
  "EndpointId": "YOUR_NEW_ENDPOINT_ID_HERE"
}
```

**File: `PersonalMedia.Functions/local.settings.json`**
```json
"RunPod:EndpointId": "YOUR_NEW_ENDPOINT_ID_HERE"
```

### 4. Test the Endpoint

Once deployed, test using the RunPod dashboard or your application:

**Test Request Format:**
```json
{
  "input": {
    "prompt": "Add stylish sunglasses to the person",
    "image": "https://chadmonahan.blob.core.windows.net/personal-media/pose.png",
    "model": "qwen-image-edit",
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 50
  }
}
```

**Expected Response:**
```json
{
  "delayTime": 1234,
  "executionTime": 15678,
  "id": "job-id-here",
  "status": "COMPLETED",
  "output": {
    "image_url": "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "prompt": "Add stylish sunglasses to the person",
    "model": "qwen2-vl-7b-instruct",
    "status": "completed"
  }
}
```

## Alternative: Use Pre-built Template

If you prefer not to build your own container, you can use a community template:

1. Go to RunPod Serverless → Templates
2. Search for "Qwen" or "Vision Language Model"
3. Use a pre-built Qwen2-VL template if available
4. Modify the handler code in the template to match our expected input/output format

## Important Notes

### Model Size & Cold Starts
- Qwen2-VL-7B is ~15GB
- First cold start will take 2-5 minutes to download model
- Use a network volume to persist the model and reduce cold starts to ~30 seconds

### Cost Optimization
- Use Min Workers: 0 to scale to zero when idle
- Choose GPU based on your budget:
  - A40: ~$0.79/hr (~$0.22/hr idle)
  - RTX 4090: ~$0.69/hr (~$0.19/hr idle)
  - A6000: ~$0.89/hr (~$0.24/hr idle)
- Network volume: ~$0.10/GB/month (one-time setup)

### Output Format
Currently the handler returns base64-encoded images. For production, you should:
1. Upload generated images to Azure Blob Storage
2. Return the Azure Storage URL instead of base64
3. This prevents large payloads and provides permanent storage

### Scaling Considerations
- Each worker can handle 1 request at a time
- Adjust Max Workers based on concurrent request expectations
- Monitor metrics in RunPod dashboard: queue time, execution time, cold starts

## Troubleshooting

### Container fails to start
- Check logs in RunPod dashboard
- Verify all dependencies are in requirements.txt
- Ensure Dockerfile base image has CUDA support

### Out of memory errors
- Increase GPU type (e.g., A40 → A6000 → A100)
- Reduce batch size in handler
- Lower `num_inference_steps`

### Slow cold starts
- Attach and configure network volume
- Pre-download model to network volume
- Increase idle timeout to keep workers warm longer

### Model not loading
- Check TRANSFORMERS_CACHE path matches network volume
- Verify HuggingFace model name is correct
- Check internet connectivity from worker

## Next Steps

1. Build and deploy the container
2. Create the serverless endpoint
3. Update endpoint ID in your configs
4. Test with your `/runpod-test` page
5. Monitor performance and adjust GPU/worker settings
6. (Optional) Implement image upload to Azure Storage for production
