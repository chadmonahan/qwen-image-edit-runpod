"""
Local test script for the RunPod handler
Run this to test the handler locally and see any errors
"""

import sys
import os

# Add the current directory to path so we can import handler
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("Testing RunPod Handler Locally")
print("=" * 80)

# Try to import and test the handler
try:
    print("\n1. Attempting to import handler module...")
    import handler
    print("✓ Handler module imported successfully!")

    print("\n2. Testing handler function with mock input...")
    test_input = {
        "input": {
            "prompt": "Add sunglasses to the person",
            "image": "https://picsum.photos/512/512",
            "num_inference_steps": 20,
            "true_cfg_scale": 4.0,
            "guidance_scale": 1.0,
            "seed": 0
        }
    }

    print(f"Test input: {test_input}")
    print("\n3. Calling handler function...")

    # Note: This will try to actually run the model, which will take time
    # and download the model if not cached
    result = handler.handler(test_input)

    print("\n4. Handler result:")
    print(result)

    print("\n✓ Handler test completed successfully!")

except Exception as e:
    print(f"\n✗ Error occurred: {e}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())
    sys.exit(1)
