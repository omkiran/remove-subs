#!/usr/bin/env python3
"""
Unified LaMa + ZITS Video Subtitle Inpainting Pipeline
Python script version for direct execution
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path

def generate_test_data():
    """Generate synthetic test frames and masks."""
    
    # Configuration
    config = {
        'input_dir': '../input_video',
        'mask_dir': '../masks',
        'lama_output_dir': '../lama_output',
        'zits_output_dir': '../zits_output',
        'frame_count': 10,
        'frame_size': (256, 256),
        'subtitle_region': (30, 220, 230, 250)  # x1, y1, x2, y2
    }
    
    # Create directories
    for dir_path in [config['input_dir'], config['mask_dir'], config['lama_output_dir'], config['zits_output_dir']]:
        os.makedirs(dir_path, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")
    
    print(f"\n🎬 Generating {config['frame_count']} test frames...")
    
    # Generate synthetic frames with subtitles
    for i in range(config['frame_count']):
        # Create frame with gradient background
        img = np.full((*config['frame_size'], 3), 255, dtype=np.uint8)
        
        # Add gradient effect
        for y in range(config['frame_size'][0]):
            img[y, :] = [255 - y//3, 200 + y//8, 180 + y//4]
        
        # Add main content text
        cv2.putText(img, f"Video Frame {i+1}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(img, "Sample Content", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 1)
        
        # Add subtitle (to be removed)
        cv2.putText(img, f"Subtitle text {i+1}", (40, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Save frame
        cv2.imwrite(f"{config['input_dir']}/frame_{i:03d}.png", img)

        # Create corresponding mask for subtitle area
        mask = np.zeros(config['frame_size'], dtype=np.uint8)
        x1, y1, x2, y2 = config['subtitle_region']
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        
        # Save mask
        cv2.imwrite(f"{config['mask_dir']}/mask_{i:03d}.png", mask)

    print(f"✅ Generated {config['frame_count']} frames and masks")
    print(f"   📁 Frames: {config['input_dir']}")
    print(f"   🎭 Masks: {config['mask_dir']}")
    
    return config

def check_environment():
    """Check the runtime environment."""
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        device = 'cuda' if gpu_available else 'cpu'
    except ImportError:
        gpu_available = False
        device = 'cpu'
    
    in_docker = os.path.exists('/.dockerenv')
    
    print("🔍 Environment Detection:")
    print(f"   GPU Available: {gpu_available}")
    print(f"   Device: {device}")
    print(f"   Docker: {in_docker}")
    
    if gpu_available:
        print("   🚀 GPU acceleration available")
    else:
        print("   💻 Running in CPU mode")
    
    return {
        'gpu_available': gpu_available,
        'device': device,
        'in_docker': in_docker
    }

def main():
    """Main execution function."""
    print("🔧 Unified LaMa + ZITS Video Subtitle Inpainting Pipeline")
    print("=" * 60)
    
    # Check environment
    env_config = check_environment()
    print()
    
    # Generate test data
    config = generate_test_data()
    print()
    
    # Provide instructions
    print("🚀 Next Steps:")
    print("=" * 30)
    
    if env_config['in_docker']:
        print("🐳 Running in Docker - Pipeline will continue automatically!")
    else:
        print("💻 Local execution - Choose your method:")
        print("   🐳 Docker: cd .. && ./test_pipeline.sh docker")
        print("   🔧 Manual: Follow the pipeline instructions")
    
    print()
    print("📋 Manual Pipeline Commands:")
    print()
    print("🎨 LaMa Inpainting:")
    print("   git clone https://github.com/advimman/lama.git")
    print("   cd lama && pip install -r requirements.txt")
    print(f"   python bin/predict.py model.path=big-lama \\")
    print(f"       indir={config['input_dir']} \\")
    print(f"       maskdir={config['mask_dir']} \\")
    print(f"       outdir={config['lama_output_dir']}")
    print()
    print("🎬 ZITS++ Temporal Refinement:")
    print("   git clone https://github.com/DQiaole/ZITS_plus_plus.git")
    print("   cd ZITS_plus_plus && pip install -r requirements.txt")
    print(f"   python test_video.py \\")
    print(f"       --video_root {config['input_dir']} \\")
    print(f"       --mask_root {config['mask_dir']} \\")
    print(f"       --inpainted_root {config['lama_output_dir']} \\")
    print(f"       --output_root {config['zits_output_dir']}")
    print()
    print("🎞️ Final Video Assembly:")
    print(f"   ffmpeg -framerate 10 -i {config['zits_output_dir']}/frame_%03d.png \\")
    print("       -c:v libx264 -pix_fmt yuv420p output_clean.mp4")
    
    print()
    print("✅ Test data generation completed!")

if __name__ == "__main__":
    main()
