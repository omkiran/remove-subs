# 🔧 Unified LaMa + ZITS Video Subtitle Inpainting Pipeline

A unified, production-ready pipeline for removing burnt-in subtitles from videos using AI inpainting with **LaMa** (Large Mask Inpainting) and **ZITS++** (video-aware temporal consistency).

## ✨ Features

- 🚀 **Auto GPU/CPU Detection** - Automatically configures for available hardware
- 🐳 **Docker Containerization** - Complete isolated environment setup
- ☁️ **AWS S3 Integration** - Direct processing from S3 buckets
- 🔄 **Flexible Deployment** - Local, cloud, or containerized execution
- 📦 **All-in-One Setup** - Single command to run the entire pipeline
- 🎯 **Production Ready** - Robust error handling and logging
- 📊 **Progress Monitoring** - Real-time status updates and visualization
- 🎬 **MP4 H.264 Support** - Optimized for standard video formats

## 🏗️ Architecture

The pipeline combines two state-of-the-art AI models:

1. **LaMa** - Performs initial frame-by-frame subtitle inpainting
2. **ZITS++** - Ensures temporal consistency across video frames

```
Input Video → Frame Extraction → Mask Generation → LaMa Inpainting → ZITS++ Refinement → Final Video
```

## 🚀 Quick Start

### Option 1: AWS with S3 (Production)

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Process video from S3
cd lama_zits_unified_pipeline
./test_pipeline.sh aws gpu s3://bucket/video.mp4 s3://bucket/output/

# Use synthetic data for testing
./test_pipeline.sh aws gpu
```

### Option 2: Docker/Podman (Local/Development)

```bash
# Clone and navigate to the unified pipeline
cd lama_zits_unified_pipeline

# Using Docker (traditional)
./test_pipeline.sh docker

# Using Podman (rootless alternative)
./test_pipeline.sh podman

# Force GPU mode
./test_pipeline.sh docker gpu
./test_pipeline.sh podman gpu

# Force CPU mode  
./test_pipeline.sh docker cpu
./test_pipeline.sh podman cpu
```

### Option 3: Local Development

```bash
# Generate test data
./test_pipeline.sh local

# Follow the displayed instructions for manual setup
```

## 📋 Requirements

### System Requirements
- **Docker** or **Podman** (recommended) or Python 3.8+
- **NVIDIA GPU** (optional, but significantly faster)
- **CUDA 11.3+** (for GPU acceleration)
- **FFmpeg** (for video processing)
- **AWS CLI** (for S3 integration)

### Container Runtime Notes
- **Docker**: Standard container runtime, requires Docker Desktop on macOS/Windows
- **Podman**: Rootless alternative to Docker, better security model
- **GPU Support**: 
  - Docker: Uses `--gpus` flag with nvidia-docker2
  - Podman: Uses `--device nvidia.com/gpu=all` with CDI

### Python Dependencies
- PyTorch
- OpenCV
- NumPy
- Matplotlib
- Boto3 (for AWS S3)

## 🔧 Usage

### 1. AWS Production with S3

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Process MP4 video from S3
./test_pipeline.sh aws gpu s3://my-bucket/input-video.mp4 s3://my-bucket/output/

# Use CPU mode
./test_pipeline.sh aws cpu s3://my-bucket/input-video.mp4 s3://my-bucket/output/
```

### 2. Local Processing with Docker/Podman

```bash
# Using Docker (traditional)
./test_pipeline.sh docker

# Using Podman (rootless, more secure)
./test_pipeline.sh podman

# Process your own MP4 video with Podman
# 1. Place your video.mp4 in the project directory
# 2. Extract frames
ffmpeg -i video.mp4 input_video/frame_%05d.png
# 3. Create subtitle masks (manual or automated)
# 4. Run pipeline
./test_pipeline.sh podman gpu
```

### 3. Advanced AWS Configuration

Set environment variables for custom S3 paths:

```bash
export S3_INPUT_VIDEO=s3://my-bucket/videos/input.mp4
export S3_OUTPUT_LOCATION=s3://my-bucket/results/
export USE_SYNTHETIC_DATA=false

./test_pipeline.sh aws gpu
```

## 📁 Directory Structure

```
lama_zits_unified_pipeline/
├── docker/
│   ├── Dockerfile              # Unified container definition
│   ├── entrypoint.sh           # Auto GPU/CPU pipeline script
│   ├── gpu_detector.py         # Hardware detection utility
│   ├── s3_handler.py           # AWS S3 integration
│   ├── video_processor.py      # MP4 processing utilities
│   └── lama_zits_pipeline.py   # Synthetic data generator
├── notebook/
│   ├── lama_zits_pipeline.ipynb # Interactive Jupyter notebook
│   └── lama_zits_pipeline.py   # Standalone Python script
├── scripts/                    # Additional utility scripts
├── test_pipeline.sh            # Main execution script
├── docker-compose.yml          # Container orchestration
├── AWS_DEPLOYMENT.md           # AWS deployment guide
└── README.md                   # This file
```

## 🔍 Environment Detection

The pipeline automatically detects:

- **GPU Availability** - CUDA-capable devices
- **Docker Environment** - Container vs local execution  
- **Hardware Capabilities** - Memory, compute capability
- **Platform** - Google Colab, local machine, cloud instance

## 🎛️ Configuration Options

### Docker Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_VIDEO_DIR` | `/data/input_video` | Input video frames directory |
| `MASKS_DIR` | `/data/masks` | Subtitle mask files directory |
| `LAMA_OUT_DIR` | `/data/lama_output` | LaMa inpainting output |
| `ZITS_OUT_DIR` | `/data/zits_output` | Final ZITS++ output |
| `MODEL_PATH` | `/workspace/lama/big-lama` | LaMa model weights path |
| `S3_INPUT_VIDEO` | `""` | S3 URL for input MP4 video |
| `S3_OUTPUT_LOCATION` | `""` | S3 URL for output location |
| `USE_SYNTHETIC_DATA` | `true` | Generate synthetic test data |

### Pipeline Modes

| Mode | Description | Command |
|------|-------------|---------|
| `local` | Generate test data only | `./test_pipeline.sh local` |
| `aws` | AWS with S3 integration | `./test_pipeline.sh aws gpu s3://bucket/video.mp4` |
| `docker` | Local containerized pipeline with Docker | `./test_pipeline.sh docker` |
| `podman` | Local containerized pipeline with Podman | `./test_pipeline.sh podman` |

### AWS Instance Recommendations

| Use Case | Instance Type | GPU | Performance |
|----------|---------------|-----|-------------|
| Development | `g4dn.xlarge` | T4 | Good |
| Production | `g4dn.2xlarge` | T4 | Better |
| Large Videos | `p3.2xlarge` | V100 | Best |
| CPU Fallback | `c5.4xlarge` | None | Acceptable |

## � Podman Setup (Alternative to Docker)

### Why Podman?
- **Rootless**: More secure, runs without root privileges
- **Daemonless**: No background daemon required
- **Docker Compatible**: Drop-in replacement for most Docker commands
- **Systemd Integration**: Better integration with Linux systems

### Podman Installation

**macOS:**
```bash
brew install podman
podman machine init
podman machine start
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install podman
```

**RHEL/CentOS/Fedora:**
```bash
sudo dnf install podman
```

### GPU Support with Podman

Podman uses Container Device Interface (CDI) for GPU access:

```bash
# Install nvidia-container-toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install nvidia-container-toolkit

# Generate CDI specification
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# Test GPU access
podman run --rm --device nvidia.com/gpu=all nvidia/cuda:11.3-base-ubuntu20.04 nvidia-smi
```

### Rootless Configuration

```bash
# Set up subuid/subgid for your user
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid

# Migrate existing containers
podman system migrate

# Enable lingering (optional, for systemd services)
sudo loginctl enable-linger $USER
```

## �🚀 Performance

### GPU vs CPU Performance

| Hardware | Frame Processing | Total Time (10 frames) |
|----------|------------------|------------------------|
| NVIDIA RTX 3080 | ~2-3 sec/frame | ~30-45 seconds |
| NVIDIA GTX 1660 | ~5-8 sec/frame | ~60-90 seconds |
| CPU (8-core) | ~30-60 sec/frame | ~10-15 minutes |
| CPU (4-core) | ~60-120 sec/frame | ~20-30 minutes |

### Memory Requirements

- **GPU**: 4GB+ VRAM recommended (8GB+ for high resolution)
- **CPU**: 8GB+ RAM minimum (16GB+ recommended)
- **Storage**: 2GB+ free space for models and temporary files

## 🐛 Troubleshooting

### Common Issues

**Docker GPU not detected:**
```bash
# Verify NVIDIA Docker support
docker run --rm --gpus all nvidia/cuda:11.3-base-ubuntu20.04 nvidia-smi
```

**Podman GPU not detected:**
```bash
# Verify Podman GPU support (requires nvidia-container-toolkit)
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
podman run --rm --device nvidia.com/gpu=all nvidia/cuda:11.3-base-ubuntu20.04 nvidia-smi
```

**Permission denied:**
```bash
chmod +x test_pipeline.sh
chmod +x docker/entrypoint.sh
```

**Out of memory:**
```bash
# Use CPU mode for large videos
./test_pipeline.sh docker cpu
./test_pipeline.sh podman cpu
```

**Missing dependencies:**
```bash
# Rebuild Docker image
docker build --no-cache -t lama-zits:unified docker/

# Rebuild Podman image
podman build --no-cache -t lama-zits:unified docker/
```

### Debug Mode

Enable verbose logging:
```bash
export DEBUG=1
./test_pipeline.sh docker
```

## 🔬 Technical Details

### LaMa Model
- **Architecture**: Fast Fourier Convolution (FFC) based
- **Training**: Large-scale image inpainting dataset
- **Strengths**: High-quality static inpainting, handles large missing regions

### ZITS++ Model  
- **Architecture**: Transformer-based with temporal attention
- **Training**: Video inpainting with temporal consistency
- **Strengths**: Temporal coherence, reduces flickering artifacts

### Pipeline Optimizations
- **Automatic weight downloading** for GPU setups
- **Memory-efficient processing** for large videos
- **Batch processing** for multiple frames
- **Error recovery** and graceful degradation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LaMa**: [Resolution-robust Large Mask Inpainting with Fourier Convolutions](https://github.com/advimman/lama)
- **ZITS++**: [ZITS++: Image Inpainting by Improving the Incremental Transformer on Structural Prior](https://github.com/DQiaole/ZITS_plus_plus)
- **PyTorch**: Deep learning framework
- **OpenCV**: Computer vision library

## 📞 Support

- 🐛 **Bug Reports**: Open an issue with detailed reproduction steps
- 💡 **Feature Requests**: Describe your use case and proposed solution  
- 📧 **Contact**: Create a discussion for general questions

---

**Made with ❤️ for the video processing community**
