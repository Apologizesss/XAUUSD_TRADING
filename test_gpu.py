"""Test GPU availability"""

import torch

print("=" * 60)
print("PyTorch GPU Test")
print("=" * 60)

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(
        f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
    )
    print("\n✅ GPU is ready to use!")
else:
    print("\n⚠️ GPU not available - using CPU")
