"""
RunPod Serverless Handler for Qwen Image Edit 2511
This handler processes image editing requests using the Qwen-Image-Edit-2511 model.
"""

import runpod
import torch
from PIL import Image
import requests
from io import BytesIO
import base64
import os
import sys

# Debug imports
print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Monkey-patch torch.xpu for older PyTorch versions
# Diffusers requires torch.xpu but PyTorch 2.2.0 doesn't have it
if not hasattr(torch, 'xpu'):
    print("torch.xpu not found, creating mock module for compatibility")
    class MockXPU:
        @staticmethod
        def empty_cache():
            pass  # No-op for non-XPU systems

        @staticmethod
        def is_available():
            return False

    torch.xpu = MockXPU()
    print("Mock torch.xpu module created successfully")

# Import diffusers and check version
try:
    import diffusers
    print(f"Diffusers version: {diffusers.__version__}")

    # Try importing from top-level first
    try:
        from diffusers import QwenImageEditPlusPipeline
        print("Successfully imported QwenImageEditPlusPipeline from top-level")
    except (ImportError, AttributeError) as e1:
        print(f"Top-level import failed: {e1}")
        print("Trying direct submodule import...")
        # Try importing directly from submodule
        from diffusers.pipelines.qwenimage import QwenImageEditPlusPipeline
        print("Successfully imported QwenImageEditPlusPipeline from submodule")

except ImportError as e:
    print(f"ERROR importing diffusers: {e}")
    print("Available diffusers attributes:")
    import diffusers
    print([x for x in dir(diffusers) if 'Qwen' in x or 'Pipeline' in x][:20])
    raise

# Global variables for model caching
pipeline = None

def load_pipeline():
    """Load the Qwen-Image-Edit-2511 pipeline (cached after first call)"""
    global pipeline

    if pipeline is None:
        print("Loading Qwen-Image-Edit-2511 model...")

        # Check CUDA availability
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is required for Qwen-Image-Edit-2511")

        print(f"Using device: cuda")

        # Load the pipeline
        pipeline = QwenImageEditPlusPipeline.from_pretrained(
            "Qwen/Qwen-Image-Edit-2511",
            torch_dtype=torch.bfloat16
        )
        pipeline.to('cuda')

        print("Model loaded successfully!")

    return pipeline


def download_image(image_url):
    """Download image from URL and return PIL Image in RGB mode"""
    try:
        print(f"Downloading image from: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        # Ensure RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        raise Exception(f"Failed to download image: {str(e)}")


def encode_image_to_base64(image):
    """Encode PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def handler(job):
    """
    RunPod handler function

    Expected input format:
    {
        "input": {
            "prompt": "Add sunglasses to the person",
            "image": "https://example.com/image.jpg",
            "model": "qwen-image-edit",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 40
        }
    }
    """
    try:
        job_input = job["input"]

        # Extract parameters
        prompt = job_input.get("prompt")
        image_url = job_input.get("image")
        num_steps = job_input.get("num_inference_steps", 40)
        true_cfg_scale = job_input.get("true_cfg_scale", 4.0)
        guidance_scale = job_input.get("guidance_scale", 1.0)
        seed = job_input.get("seed", 0)

        # Validate required parameters
        if not prompt:
            return {"error": "Missing required parameter: prompt"}

        if not image_url:
            return {"error": "Missing required parameter: image (URL)"}

        print(f"Processing request - Prompt: '{prompt}', Image: {image_url}")
        print(f"Parameters - Steps: {num_steps}, CFG Scale: {true_cfg_scale}, Guidance: {guidance_scale}, Seed: {seed}")

        # Load pipeline
        pipe = load_pipeline()

        # Download the input image
        input_image = download_image(image_url)
        print(f"Input image size: {input_image.size}")

        # Prepare inputs for the pipeline
        inputs = {
            "image": [input_image],  # Must be a list
            "prompt": prompt,
            "generator": torch.manual_seed(seed),
            "true_cfg_scale": true_cfg_scale,
            "negative_prompt": " ",  # Empty negative prompt as per docs
            "num_inference_steps": num_steps,
            "guidance_scale": guidance_scale,
            "num_images_per_prompt": 1,
        }

        # Generate edited image
        print(f"Running Qwen-Image-Edit-2511 inference...")
        with torch.inference_mode():
            output = pipe(**inputs)
            output_image = output.images[0]

        print(f"Generation complete. Output image size: {output_image.size}")

        # Encode output image to base64
        output_image_b64 = encode_image_to_base64(output_image)

        # Return the result in expected format
        return {
            "image_url": f"data:image/png;base64,{output_image_b64}",
            "image": f"data:image/png;base64,{output_image_b64}",
            "prompt": prompt,
            "model": "qwen-image-edit-2511",
            "status": "completed",
            "input_image_size": input_image.size,
            "output_image_size": output_image.size
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in handler: {error_details}")
        return {"error": str(e), "details": error_details}


# Start the RunPod serverless handler
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
