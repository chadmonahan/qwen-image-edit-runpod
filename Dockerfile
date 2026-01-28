# RunPod Serverless Dockerfile for Qwen Image Edit 2511
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install diffusers from source (required for QwenImageEditPlusPipeline)
RUN pip install --no-cache-dir git+https://github.com/huggingface/diffusers

# Install other Python dependencies
RUN pip install --no-cache-dir \
    runpod>=1.5.0 \
    torch>=2.1.0 \
    torchvision>=0.16.0 \
    transformers>=4.37.0 \
    accelerate>=0.25.0 \
    Pillow>=10.0.0 \
    requests>=2.31.0

# Copy handler code
COPY handler.py /app/handler.py

# Set environment variables for model caching
ENV TRANSFORMERS_CACHE=/runpod-volume/huggingface-cache
ENV HF_HOME=/runpod-volume/huggingface-cache
ENV HF_HUB_CACHE=/runpod-volume/huggingface-cache

# Run the handler
CMD ["python", "-u", "handler.py"]
