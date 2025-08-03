#!/bin/bash
set -e

echo "🔧 Unified LaMa + ZITS Video Subtitle Inpainting Pipeline (AWS Enhanced)"
echo "========================================================================"

# Container runtime detection
detect_container_runtime() {
    local runtime="$1"
    
    if [[ "$runtime" == "podman" ]]; then
        if command -v podman &> /dev/null; then
            echo "podman"
            return 0
        else
            echo "❌ Podman not found. Please install Podman first."
            echo "   macOS: brew install podman"
            echo "   Ubuntu: sudo apt install podman"
            echo "   RHEL/CentOS: sudo dnf install podman"
            exit 1
        fi
    elif [[ "$runtime" == "docker" ]]; then
        if command -v docker &> /dev/null; then
            echo "docker"
            return 0
        else
            echo "❌ Docker not found. Please install Docker first."
            exit 1
        fi
    else
        # Auto-detect
        if command -v podman &> /dev/null; then
            echo "podman"
        elif command -v docker &> /dev/null; then
            echo "docker"
        else
            echo "❌ Neither Docker nor Podman found. Please install one."
            exit 1
        fi
    fi
}

# GPU flags for different runtimes
get_gpu_flags() {
    local runtime="$1"
    local force_gpu="$2"
    
    if [[ "$force_gpu" == "cpu" ]]; then
        echo ""
        return
    fi
    
    if [[ "$runtime" == "docker" ]]; then
        if command -v nvidia-smi &>/dev/null && [[ "$force_gpu" != "cpu" ]]; then
            echo "--gpus all"
        fi
    elif [[ "$runtime" == "podman" ]]; then
        # Check if nvidia-container-toolkit is configured
        if [[ -f /etc/cdi/nvidia.yaml ]] && command -v nvidia-smi &>/dev/null && [[ "$force_gpu" != "cpu" ]]; then
            echo "--device nvidia.com/gpu=all"
        elif command -v nvidia-smi &>/dev/null && [[ "$force_gpu" != "cpu" ]]; then
            echo "⚠️  GPU detected but CDI not configured for Podman"
            echo "   Run: sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml"
            echo "   Falling back to CPU mode..."
            echo ""
        fi
    fi
}

# Default mode
MODE=${1:-local}
GPU_MODE=${2:-auto}
S3_INPUT=${3:-""}
S3_OUTPUT=${4:-""}

case $MODE in
    "local")
        echo "🏠 Running in LOCAL mode"
        echo "📝 Generating synthetic test data..."
        
        # Create output directories
        mkdir -p input_video masks lama_output zits_output aws_output
        
        # Run the notebook to generate test data
        if command -v python3 &> /dev/null; then
            echo "🐍 Executing pipeline notebook..."
            cd notebook
            python3 lama_zits_pipeline.py
            cd ..
        else
            echo "❌ Python3 not found. Please install Python to run locally."
            exit 1
        fi
        
        echo "✅ Test data generation completed"
        echo
        echo "📋 Next steps:"
        echo "   1. For AWS GPU: ./test_pipeline.sh aws gpu s3://bucket/video.mp4 s3://bucket/output/"
        echo "   2. For AWS CPU: ./test_pipeline.sh aws cpu"
        echo "   3. For local Docker: ./test_pipeline.sh docker"
        echo "   4. For local Podman: ./test_pipeline.sh podman"
        echo
        echo "🔧 Manual setup instructions are in the README.md"
        ;;
        
    "aws")
        echo "☁️  Running in AWS mode"
        
        # Check AWS credentials
        if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
            echo "⚠️  AWS credentials not found in environment variables"
            echo "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
            echo "Or use IAM roles if running on EC2"
            echo
        fi
        
        # GPU detection and setup
        if [ "$GPU_MODE" = "auto" ]; then
            if command -v nvidia-smi &> /dev/null; then
                echo "🚀 NVIDIA GPU detected - enabling GPU support"
                DOCKER_PROFILE="aws-gpu"
                IMAGE_TAG="aws-gpu"
            else
                echo "💻 No GPU detected - running in CPU mode"
                DOCKER_PROFILE="aws-cpu"
                IMAGE_TAG="aws-cpu"
            fi
        elif [ "$GPU_MODE" = "gpu" ]; then
            echo "🚀 Forcing GPU mode"
            DOCKER_PROFILE="aws-gpu"
            IMAGE_TAG="aws-gpu"
        else
            echo "💻 Forcing CPU mode"
            DOCKER_PROFILE="aws-cpu"
            IMAGE_TAG="aws-cpu"
        fi
        
        # Set S3 configuration
        export S3_INPUT_VIDEO="$S3_INPUT"
        export S3_OUTPUT_LOCATION="$S3_OUTPUT"
        export USE_SYNTHETIC_DATA=${USE_SYNTHETIC_DATA:-false}
        
        if [ -n "$S3_INPUT" ]; then
            echo "� S3 Input: $S3_INPUT"
            export USE_SYNTHETIC_DATA=false
        else
            echo "🎨 Using synthetic data (no S3 input specified)"
            export USE_SYNTHETIC_DATA=true
        fi
        
        if [ -n "$S3_OUTPUT" ]; then
            echo "📤 S3 Output: $S3_OUTPUT"
        else
            echo "💾 Local output only"
        fi
        
        # Create local directories
        mkdir -p input_video masks lama_output zits_output aws_output
        
        # Build and run with Docker Compose
        echo "🔨 Building Docker image..."
        docker-compose build
        
        echo "🚀 Starting AWS-enabled container..."
        docker-compose --profile $DOCKER_PROFILE up --remove-orphans
        ;;
        
    "docker"|"podman")
        RUNTIME=$(detect_container_runtime "$MODE")
        echo "🐳 Running with $RUNTIME in $([[ "$GPU_MODE" == "gpu" ]] && echo "GPU" || [[ "$GPU_MODE" == "cpu" ]] && echo "CPU" || echo "auto-detect") mode"
        
        # Build image if needed
        IMAGE_NAME="lama-zits:unified"
        if ! $RUNTIME images | grep -q "$IMAGE_NAME"; then
            echo "� Building $RUNTIME image..."
            $RUNTIME build -t "$IMAGE_NAME" docker/
        fi
        
        # Get GPU flags
        GPU_FLAGS=$(get_gpu_flags "$RUNTIME" "$GPU_MODE")
        
        # Check if test data exists
        if [ ! -d "input_video" ] || [ -z "$(ls -A input_video 2>/dev/null)" ]; then
            echo "� No test data found. Generating..."
            ./test_pipeline.sh local
        fi
        
        # Set environment variables
        ENV_VARS="-e USE_SYNTHETIC_DATA=true"
        if [[ -n "$S3_INPUT_VIDEO" ]]; then
            ENV_VARS="$ENV_VARS -e S3_INPUT_VIDEO=$S3_INPUT_VIDEO"
        fi
        if [[ -n "$S3_OUTPUT_LOCATION" ]]; then
            ENV_VARS="$ENV_VARS -e S3_OUTPUT_LOCATION=$S3_OUTPUT_LOCATION"
        fi
        if [[ -n "$AWS_ACCESS_KEY_ID" ]]; then
            ENV_VARS="$ENV_VARS -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
        fi
        if [[ -n "$AWS_SECRET_ACCESS_KEY" ]]; then
            ENV_VARS="$ENV_VARS -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
        fi
        
        # Run container
        echo "🚀 Starting $RUNTIME container..."
        $RUNTIME run --rm \
            $GPU_FLAGS \
            $ENV_VARS \
            -v "$(pwd)/input_video:/data/input_video" \
            -v "$(pwd)/masks:/data/masks" \
            -v "$(pwd)/lama_output:/data/lama_output" \
            -v "$(pwd)/zits_output:/data/zits_output" \
            "$IMAGE_NAME"
        ;;
        
    "help"|"--help"|"-h")
        echo "Usage: $0 [MODE] [GPU_MODE] [S3_INPUT] [S3_OUTPUT]"
        echo
        echo "Modes:"
        echo "  local    - Generate test data and show setup instructions"
        echo "  aws      - Run full pipeline with AWS/S3 support"
        echo "  docker   - Run pipeline in Docker container (local)"
        echo "  podman   - Run pipeline in Podman container (rootless)"
        echo "  help     - Show this help message"
        echo
        echo "GPU Modes (for aws/docker/podman):"
        echo "  auto     - Auto-detect GPU availability (default)"
        echo "  gpu      - Force GPU mode"
        echo "  cpu      - Force CPU mode"
        echo
        echo "S3 Parameters (for aws mode):"
        echo "  S3_INPUT  - S3 URL for input video (e.g., s3://bucket/video.mp4)"
        echo "  S3_OUTPUT - S3 URL for output location (e.g., s3://bucket/output/)"
        echo
        echo "Examples:"
        echo "  $0 local                                    # Generate test data"
        echo "  $0 docker                                   # Auto-detect and run with Docker"
        echo "  $0 podman gpu                               # Force GPU mode with Podman"
        echo "  $0 aws gpu                                  # AWS with GPU, synthetic data"
        echo "  $0 aws auto s3://bucket/video.mp4           # AWS with S3 input"
        echo "  $0 aws cpu \"\" s3://bucket/output/          # AWS CPU with S3 output"
        echo
        echo "Container Runtimes:"
        echo "  🐳 Docker  - Standard container runtime"
        echo "  🦭 Podman  - Rootless, daemonless alternative"
        echo
        echo "GPU Support:"
        echo "  Docker: Uses --gpus flag (requires nvidia-docker2)"
        echo "  Podman: Uses --device flag (requires nvidia-container-toolkit + CDI)"
        echo
        echo "AWS Configuration:"
        echo "  Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
        echo "  Or use IAM roles when running on EC2 instances"
        ;;
        
    *)
        echo "❌ Unknown mode: $MODE"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
