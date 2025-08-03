#!/usr/bin/env python3
"""
Standalone script for generating synthetic test data
Used by the Docker container when USE_SYNTHETIC_DATA=true
"""

import cv2
import numpy as np
import os
import sys

def generate_synthetic_data():
    """Generate synthetic test frames and masks."""
    
    # Configuration
    config = {
        'input_dir': '/data/input_video',
        'mask_dir': '/data/masks',
        'frame_count': 30,  # More frames for better testing
        'frame_size': (256, 256),
        'subtitle_region': (0, 205, 256, 256)  # Bottom portion for subtitles
    }
    
    # Create directories
    for dir_path in [config['input_dir'], config['mask_dir']]:
        os.makedirs(dir_path, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")
    
    print(f"\n🎬 Generating {config['frame_count']} synthetic test frames...")
    
    # Generate synthetic frames with subtitles
    for i in range(config['frame_count']):
        # Create frame with animated background
        img = np.full((*config['frame_size'], 3), 255, dtype=np.uint8)
        
        # Add animated gradient effect
        phase = i / config['frame_count'] * 2 * np.pi
        for y in range(config['frame_size'][0]):
            for x in range(config['frame_size'][1]):
                # Create moving gradient
                r = int(128 + 127 * np.sin(phase + x/30))
                g = int(128 + 127 * np.sin(phase + y/30 + np.pi/3))
                b = int(128 + 127 * np.sin(phase + (x+y)/40 + 2*np.pi/3))
                img[y, x] = [min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]
        
        # Add main content text
        cv2.putText(img, f"Test Video Frame {i+1:02d}", (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f"Sample Content", (20, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Add moving object for realistic content
        center_x = int(128 + 50 * np.sin(i/5))
        center_y = int(120 + 30 * np.cos(i/3))
        cv2.circle(img, (center_x, center_y), 15, (0, 255, 255), -1)
        
        # Add subtitle (to be removed) with variation
        subtitle_texts = [
            "This is a sample subtitle",
            "Subtitle text to remove",
            "Burnt-in subtitle example",
            f"Frame {i+1} subtitle",
            "AI will remove this text"
        ]
        subtitle = subtitle_texts[i % len(subtitle_texts)]
        
        # Add subtitle background box
        text_size = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.rectangle(img, (10, 215), (text_size[0] + 20, 245), (0, 0, 0), -1)
        
        # Add subtitle text
        cv2.putText(img, subtitle, (15, 235), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Save frame
        cv2.imwrite(f"{config['input_dir']}/frame_{i+1:05d}.png", img)

        # Create corresponding mask for subtitle area
        mask = np.zeros(config['frame_size'], dtype=np.uint8)
        x1, y1, x2, y2 = config['subtitle_region']
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        
        # Save mask
        cv2.imwrite(f"{config['mask_dir']}/mask_{i+1:05d}.png", mask)

    print(f"✅ Generated {config['frame_count']} synthetic frames and masks")
    print(f"   📁 Frames: {config['input_dir']}")
    print(f"   🎭 Masks: {config['mask_dir']}")
    
    return config

def main():
    """Main execution function."""
    print("🎨 Synthetic Data Generator for LaMa + ZITS Pipeline")
    print("=" * 55)
    
    try:
        config = generate_synthetic_data()
        print("\n✅ Synthetic data generation completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Error generating synthetic data: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
