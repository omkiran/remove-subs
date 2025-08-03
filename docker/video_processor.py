#!/usr/bin/env python3
"""
Video Processor for LaMa + ZITS Pipeline
Handles MP4 to frame extraction and frame to MP4 conversion
"""

import cv2
import numpy as np
import os
import subprocess
import sys
from pathlib import Path

class VideoProcessor:
    def __init__(self):
        """Initialize video processor."""
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv']
    
    def extract_frames(self, video_path, output_dir, target_fps=None):
        """Extract frames from MP4 video using FFmpeg."""
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Get video info
            video_info = self.get_video_info(video_path)
            if not video_info:
                return False
            
            print(f"🎬 Extracting frames from: {video_path}")
            print(f"   Resolution: {video_info['width']}x{video_info['height']}")
            print(f"   FPS: {video_info['fps']}")
            print(f"   Duration: {video_info['duration']:.1f}s")
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', 'scale=256:256',  # Resize for processing
                '-q:v', '2',  # High quality
                f'{output_dir}/frame_%05d.png'
            ]
            
            # Add FPS filter if specified
            if target_fps:
                cmd.insert(-2, '-r')
                cmd.insert(-1, str(target_fps))
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Count extracted frames
                frame_count = len([f for f in os.listdir(output_dir) if f.endswith('.png')])
                print(f"✅ Extracted {frame_count} frames successfully")
                return True
            else:
                print(f"❌ Frame extraction failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Frame extraction error: {str(e)}")
            return False
    
    def create_video(self, frames_dir, output_path, fps=30, codec='libx264'):
        """Create MP4 video from frames using FFmpeg."""
        try:
            # Check if frames exist
            frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
            if not frame_files:
                print(f"❌ No frames found in {frames_dir}")
                return False
            
            print(f"🎞️  Creating video from {len(frame_files)} frames...")
            print(f"   Output: {output_path}")
            print(f"   FPS: {fps}")
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-y',  # Overwrite output file
                '-framerate', str(fps),
                '-i', f'{frames_dir}/frame_%05d.png',
                '-c:v', codec,
                '-pix_fmt', 'yuv420p',
                '-crf', '18',  # High quality
                output_path
            ]
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check output file
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"✅ Video created successfully ({file_size / 1024 / 1024:.1f} MB)")
                    return True
                else:
                    print("❌ Video creation failed - output file not found")
                    return False
            else:
                print(f"❌ Video creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Video creation error: {str(e)}")
            return False
    
    def get_video_info(self, video_path):
        """Get video information using FFprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                # Find video stream
                video_stream = None
                for stream in data['streams']:
                    if stream['codec_type'] == 'video':
                        video_stream = stream
                        break
                
                if video_stream:
                    return {
                        'width': int(video_stream['width']),
                        'height': int(video_stream['height']),
                        'fps': eval(video_stream['r_frame_rate']),  # Evaluate fraction
                        'duration': float(data['format']['duration'])
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting video info: {str(e)}")
            return None
    
    def generate_subtitle_masks(self, frames_dir, masks_dir, subtitle_region=None):
        """Generate subtitle masks for frames (for demo/testing)."""
        try:
            if subtitle_region is None:
                # Default subtitle region (bottom 20% of frame)
                subtitle_region = (0, 205, 256, 256)  # x1, y1, x2, y2
            
            frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
            if not frame_files:
                print(f"❌ No frames found in {frames_dir}")
                return False
            
            os.makedirs(masks_dir, exist_ok=True)
            
            print(f"🎭 Generating subtitle masks for {len(frame_files)} frames...")
            
            for i, frame_file in enumerate(frame_files):
                # Create mask
                mask = np.zeros((256, 256), dtype=np.uint8)
                x1, y1, x2, y2 = subtitle_region
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
                
                # Save mask with same numbering as frame
                mask_file = frame_file.replace('frame_', 'mask_')
                cv2.imwrite(f"{masks_dir}/{mask_file}", mask)
            
            print(f"✅ Generated {len(frame_files)} subtitle masks")
            return True
            
        except Exception as e:
            print(f"❌ Mask generation error: {str(e)}")
            return False

def main():
    """Test video processing functionality."""
    processor = VideoProcessor()
    
    if len(sys.argv) > 2:
        command = sys.argv[1]
        
        if command == "extract":
            video_path = sys.argv[2]
            output_dir = sys.argv[3] if len(sys.argv) > 3 else "extracted_frames"
            processor.extract_frames(video_path, output_dir)
            
        elif command == "create":
            frames_dir = sys.argv[2]
            output_path = sys.argv[3] if len(sys.argv) > 3 else "output.mp4"
            processor.create_video(frames_dir, output_path)
            
        elif command == "info":
            video_path = sys.argv[2]
            info = processor.get_video_info(video_path)
            print(f"Video info: {info}")
    else:
        print("Usage:")
        print("  python video_processor.py extract <video_path> [output_dir]")
        print("  python video_processor.py create <frames_dir> [output_path]")
        print("  python video_processor.py info <video_path>")

if __name__ == "__main__":
    main()
