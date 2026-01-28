# RunPod Serverless Dockerfile for Qwen Image Edit 2511
# Using PyTorch 2.2.0 with Python 3.10 and CUDA 12.1.1 (has torch.xpu support)
FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel setuptools

# Install diffusers from source (required for QwenImageEditPlusPipeline)
# PyTorch 2.2.0 is already in the base image and supports torch.xpu
RUN pip install --no-cache-dir git+https://github.com/huggingface/diffusers

# Install other Python dependencies
RUN pip install --no-cache-dir \
    runpod>=1.5.0 \
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
