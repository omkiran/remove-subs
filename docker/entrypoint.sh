#!/bin/bash
set -e

echo "🚀 Starting Unified LaMa + ZITS Pipeline (AWS Enhanced)"
echo "======================================================="

# Run GPU detection
python /workspace/gpu_detector.py
GPU_DETECTED=$?

# Source environment variables set by gpu_detector.py
DEVICE=${PIPELINE_DEVICE:-cpu}
GPU_AVAILABLE=${PIPELINE_GPU_AVAILABLE:-false}
DOWNLOAD_WEIGHTS=${PIPELINE_DOWNLOAD_WEIGHTS:-false}

# AWS and S3 configuration
S3_INPUT_VIDEO=${S3_INPUT_VIDEO:-""}
S3_OUTPUT_LOCATION=${S3_OUTPUT_LOCATION:-""}
USE_SYNTHETIC_DATA=${USE_SYNTHETIC_DATA:-true}

# Input args with defaults
INPUT_VIDEO_DIR=${INPUT_VIDEO_DIR:-/data/input_video}
MASKS_DIR=${MASKS_DIR:-/data/masks}
LAMA_OUT_DIR=${LAMA_OUT_DIR:-/data/lama_output}
ZITS_OUT_DIR=${ZITS_OUT_DIR:-/data/zits_output}
MODEL_PATH=${MODEL_PATH:-/workspace/lama/big-lama}

echo "📁 Configuration:"
echo "   Video frames: $INPUT_VIDEO_DIR"
echo "   Masks: $MASKS_DIR"
echo "   LaMa output: $LAMA_OUT_DIR"
echo "   ZITS output: $ZITS_OUT_DIR"
echo "   S3 input: ${S3_INPUT_VIDEO:-'Not specified'}"
echo "   S3 output: ${S3_OUTPUT_LOCATION:-'Not specified'}"
echo "   Use synthetic: $USE_SYNTHETIC_DATA"
echo

# Create output directories
mkdir -p "$LAMA_OUT_DIR" "$ZITS_OUT_DIR"

# Handle input data (S3 or synthetic)
if [ -n "$S3_INPUT_VIDEO" ]; then
    echo "📥 Processing S3 input video: $S3_INPUT_VIDEO"
    
    # Download video from S3
    TEMP_VIDEO="/tmp/input_video.mp4"
    python -c "
from s3_handler import S3Handler
from video_processor import VideoProcessor
import sys

handler = S3Handler()
processor = VideoProcessor()

# Download video from S3
if handler.download_file('$S3_INPUT_VIDEO', '$TEMP_VIDEO'):
    # Extract frames
    if processor.extract_frames('$TEMP_VIDEO', '$INPUT_VIDEO_DIR'):
        # Generate subtitle masks
        processor.generate_subtitle_masks('$INPUT_VIDEO_DIR', '$MASKS_DIR')
        print('✅ Video processing completed')
    else:
        print('❌ Frame extraction failed')
        sys.exit(1)
else:
    print('❌ S3 download failed')
    sys.exit(1)
"
    
elif [ "$USE_SYNTHETIC_DATA" = "true" ]; then
    echo "🎨 Generating synthetic test data..."
    python /workspace/lama_zits_pipeline.py
else
    echo "⚠️  No input specified. Looking for existing data..."
fi

# Download LaMa weights if needed and GPU is available
if [ "$DOWNLOAD_WEIGHTS" = "true" ] && [ ! -f "$MODEL_PATH/config.yaml" ]; then
    echo "📥 Downloading LaMa pretrained weights..."
    cd /workspace/lama
    wget -q https://github.com/advimman/lama/releases/download/0.1.1/big-lama.zip -O big-lama.zip
    unzip -q big-lama.zip -d big-lama
    rm big-lama.zip
    echo "✅ Weights downloaded successfully"
else
    echo "⚠️  Using existing weights or manual setup required"
fi

# Check if input data exists
if [ ! -d "$INPUT_VIDEO_DIR" ] || [ -z "$(ls -A "$INPUT_VIDEO_DIR" 2>/dev/null)" ]; then
    echo "❌ Error: No input video frames found in $INPUT_VIDEO_DIR"
    echo "Please mount your input data or run the notebook to generate test data."
    exit 1
fi

if [ ! -d "$MASKS_DIR" ] || [ -z "$(ls -A "$MASKS_DIR" 2>/dev/null)" ]; then
    echo "❌ Error: No mask files found in $MASKS_DIR"
    echo "Please ensure masks are available for processing."
    exit 1
fi

echo "🎯 Starting LaMa inpainting..."
echo "Running on device: $DEVICE"

# Run LaMa
cd /workspace/lama
if [ -f "$MODEL_PATH/config.yaml" ]; then
    python bin/predict.py model.path="$MODEL_PATH" indir="$INPUT_VIDEO_DIR" maskdir="$MASKS_DIR" outdir="$LAMA_OUT_DIR"
    echo "✅ LaMa inpainting completed"
else
    echo "⚠️  LaMa weights not found. Please ensure model weights are available at $MODEL_PATH"
    echo "You can download them manually or set DOWNLOAD_WEIGHTS=true for GPU setups"
fi

# Check if LaMa output exists before proceeding
if [ -d "$LAMA_OUT_DIR" ] && [ "$(ls -A "$LAMA_OUT_DIR" 2>/dev/null)" ]; then
    echo "🎬 Starting ZITS++ temporal refinement..."
    
    # Run ZITS++
    cd /workspace/ZITS_plus_plus
    python test_video.py \
        --video_root "$INPUT_VIDEO_DIR" \
        --mask_root "$MASKS_DIR" \
        --inpainted_root "$LAMA_OUT_DIR" \
        --output_root "$ZITS_OUT_DIR"
    
    echo "✅ ZITS++ processing completed"
else
    echo "⚠️  Skipping ZITS++ due to missing LaMa output"
fi

echo "🎉 Pipeline execution completed!"
echo "================================================"
echo "📊 Summary:"
echo "   Device used: $DEVICE"
echo "   GPU available: $GPU_AVAILABLE"
echo "   Final output: $ZITS_OUT_DIR"

if [ -d "$ZITS_OUT_DIR" ] && [ "$(ls -A "$ZITS_OUT_DIR" 2>/dev/null)" ]; then
    echo "   Status: ✅ Success - Check output directory for results"
    
    # Create final video
    echo "🎞️  Creating final output video..."
    python -c "
from video_processor import VideoProcessor
processor = VideoProcessor()
if processor.create_video('$ZITS_OUT_DIR', '/tmp/output_clean.mp4', fps=30):
    print('✅ Final video created: /tmp/output_clean.mp4')
else:
    print('⚠️  Video creation failed, frames available in $ZITS_OUT_DIR')
"
    
    # Upload to S3 if specified
    if [ -n "$S3_OUTPUT_LOCATION" ]; then
        echo "📤 Uploading results to S3..."
        python -c "
from s3_handler import S3Handler
import os

handler = S3Handler()

# Upload final video if it exists
if os.path.exists('/tmp/output_clean.mp4'):
    video_url = '$S3_OUTPUT_LOCATION/output_clean.mp4'
    handler.upload_file('/tmp/output_clean.mp4', video_url)

# Upload processed frames directory
frames_url = '$S3_OUTPUT_LOCATION/processed_frames'
handler.upload_directory('$ZITS_OUT_DIR', frames_url)

print('✅ S3 upload completed')
"
    fi
    
    echo
    echo "💡 Results:"
    if [ -f "/tmp/output_clean.mp4" ]; then
        echo "   🎬 Final video: /tmp/output_clean.mp4"
    fi
    echo "   📁 Processed frames: $ZITS_OUT_DIR"
    if [ -n "$S3_OUTPUT_LOCATION" ]; then
        echo "   ☁️  S3 location: $S3_OUTPUT_LOCATION"
    fi
else
    echo "   Status: ⚠️  Partial completion - Check logs for issues"
fi

echo "================================================"
