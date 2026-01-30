"""
Test if diffusers can be imported without torch.xpu errors
This simulates what happens in the handler
"""

import sys

print("=" * 80)
print("Testing Diffusers Import (simulating RunPod environment)")
print("=" * 80)

try:
    print("\n1. Checking if torch is available...")
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        print("✗ PyTorch not installed locally - but that's OK for import testing")
        print("Creating mock torch module for testing...")

        # Create a minimal mock torch for testing
        class MockTorch:
            __version__ = "2.2.0"
            class cuda:
                @staticmethod
                def is_available():
                    return True

        sys.modules['torch'] = MockTorch()
        import torch

    print("\n2. Creating torch.xpu mock (if needed)...")
    if not hasattr(torch, 'xpu'):
        print("torch.xpu not found, creating mock module")

        class MockXPU:
            @staticmethod
            def empty_cache():
                pass
            @staticmethod
            def is_available():
                return False
            @staticmethod
            def device_count():
                return 0
            @staticmethod
            def manual_seed(seed):
                pass
            @staticmethod
            def reset_peak_memory_stats(device=None):
                pass
            @staticmethod
            def max_memory_allocated(device=None):
                return 0
            @staticmethod
            def synchronize(device=None):
                pass

        torch.xpu = MockXPU()
        print("✓ Mock torch.xpu created")
    else:
        print("✓ torch.xpu already exists")

    print("\n3. Attempting to import diffusers...")
    import diffusers
    print(f"✓ Diffusers version: {diffusers.__version__}")

    print("\n4. Attempting to import QwenImageEditPlusPipeline...")
    try:
        from diffusers import QwenImageEditPlusPipeline
        print("✓ Successfully imported QwenImageEditPlusPipeline from top-level")
    except (ImportError, AttributeError) as e1:
        print(f"Top-level import failed: {e1}")
        print("Trying direct submodule import...")
        from diffusers.pipelines.qwenimage import QwenImageEditPlusPipeline
        print("✓ Successfully imported QwenImageEditPlusPipeline from submodule")

    print("\n" + "=" * 80)
    print("✓ ALL IMPORTS SUCCESSFUL!")
    print("=" * 80)

except Exception as e:
    print(f"\n✗ Error occurred: {e}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())
    sys.exit(1)
