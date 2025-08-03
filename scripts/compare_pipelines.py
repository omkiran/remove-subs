#!/usr/bin/env python3
"""
Pipeline Comparison and Migration Guide
Shows differences between old and new unified pipeline
"""

import os
from pathlib import Path

def compare_pipelines():
    """Compare the different pipeline versions."""
    
    print("📊 Pipeline Version Comparison")
    print("=" * 50)
    
    pipelines = {
        "Basic (full)": "../lama_zits_video_pipeline_full",
        "GPU-Ready": "../lama_zits_video_pipeline_gpu_ready", 
        "Unified": "."
    }
    
    features = {
        "Auto GPU Detection": [False, False, True],
        "Weight Auto-Download": [False, True, True],
        "CPU/GPU Flexibility": [False, False, True],
        "Docker Compose": [False, False, True],
        "Environment Detection": [False, False, True],
        "Progress Monitoring": [False, False, True],
        "Error Handling": ["Basic", "Basic", "Advanced"],
        "Jupyter Notebook": [True, True, True],
        "Production Ready": [False, True, True]
    }
    
    print(f"{'Feature':<25} {'Basic':<10} {'GPU-Ready':<12} {'Unified':<10}")
    print("-" * 60)
    
    for feature, values in features.items():
        basic, gpu_ready, unified = values
        basic_str = "✅" if basic is True else "❌" if basic is False else str(basic)
        gpu_str = "✅" if gpu_ready is True else "❌" if gpu_ready is False else str(gpu_ready)
        unified_str = "✅" if unified is True else "❌" if unified is False else str(unified)
        
        print(f"{feature:<25} {basic_str:<10} {gpu_str:<12} {unified_str:<10}")
    
    print("\n🚀 Migration Benefits:")
    print("   ✅ Single codebase for all scenarios")
    print("   ✅ Automatic hardware optimization") 
    print("   ✅ Better error handling and logging")
    print("   ✅ Docker Compose support")
    print("   ✅ Production-ready configuration")
    print("   ✅ Comprehensive documentation")
    
    print("\n📋 Migration Steps:")
    print("   1. Test unified pipeline: ./test_pipeline.sh local")
    print("   2. Run with Docker: ./test_pipeline.sh docker")
    print("   3. Migrate your data to new directory structure")
    print("   4. Update any custom scripts to use new paths")
    
    print("\n🔧 Backward Compatibility:")
    print("   - Same LaMa and ZITS++ models")
    print("   - Same input/output formats")
    print("   - Same Docker base image")
    print("   - Enhanced with auto-detection")

def check_old_pipelines():
    """Check if old pipeline directories exist."""
    
    old_dirs = [
        "../lama_zits_video_pipeline_full",
        "../lama_zits_video_pipeline_gpu_ready"
    ]
    
    print("\n🔍 Existing Pipeline Detection:")
    
    for old_dir in old_dirs:
        if os.path.exists(old_dir):
            print(f"   ✅ Found: {old_dir}")
            
            # Check for data
            input_dir = os.path.join(old_dir, "input_video")
            if os.path.exists(input_dir) and os.listdir(input_dir):
                print(f"      📁 Has data: {len(os.listdir(input_dir))} files")
        else:
            print(f"   ❌ Not found: {old_dir}")

def main():
    """Main comparison function."""
    compare_pipelines()
    check_old_pipelines()
    
    print("\n💡 Recommendation:")
    print("   Use the unified pipeline for all new projects!")
    print("   It combines the best features of both previous versions.")

if __name__ == "__main__":
    main()
