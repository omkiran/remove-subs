#!/usr/bin/env python3
"""
GPU Detection and Configuration Script
Detects GPU availability and configures the environment accordingly.
"""

import torch
import os
import sys

def detect_gpu():
    """Detect GPU availability and return configuration."""
    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if gpu_available else 0
    
    config = {
        'gpu_available': gpu_available,
        'gpu_count': gpu_count,
        'device': 'cuda' if gpu_available else 'cpu',
        'download_weights': gpu_available  # Only auto-download for GPU setups
    }
    
    if gpu_available:
        config['gpu_name'] = torch.cuda.get_device_name(0)
        config['gpu_memory'] = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
    
    return config

def print_config(config):
    """Print the detected configuration."""
    print("🔍 GPU Detection Results:")
    print(f"   GPU Available: {config['gpu_available']}")
    print(f"   Device: {config['device']}")
    print(f"   GPU Count: {config['gpu_count']}")
    
    if config['gpu_available']:
        print(f"   GPU Name: {config['gpu_name']}")
        print(f"   GPU Memory: {config['gpu_memory']:.1f} GB")
        print("   🚀 Running in GPU-accelerated mode")
    else:
        print("   💻 Running in CPU-only mode")
    
    print(f"   Auto-download weights: {config['download_weights']}")
    print()

def main():
    """Main function to detect and configure GPU settings."""
    config = detect_gpu()
    print_config(config)
    
    # Set environment variables for the pipeline
    os.environ['PIPELINE_DEVICE'] = config['device']
    os.environ['PIPELINE_GPU_AVAILABLE'] = str(config['gpu_available']).lower()
    os.environ['PIPELINE_DOWNLOAD_WEIGHTS'] = str(config['download_weights']).lower()
    
    # Return exit code for shell scripts
    return 0 if config['gpu_available'] else 1

if __name__ == "__main__":
    sys.exit(main())
