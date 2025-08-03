FROM nvidia/cuda:11.6.2-cudnn8-runtime-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

# Basic system deps
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3-pip \
    git \
    ffmpeg \
    libgl1-mesa-glx \
    wget \
    unzip \
    curl \
    awscli \
    build-essential \
    libgomp1 \
    libatlas-base-dev \
    liblapack-dev \
    gfortran \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Set python3.8 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    python -m pip install --upgrade pip


# -------- INSTALL PYTORCH WITH CUDA 11.6 --------
RUN pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 \
    -f https://download.pytorch.org/whl/torch_stable.html --root-user-action=ignore


# Install compatible Python packages
RUN pip install numpy==1.23.0 \
    opencv-python-headless==4.6.0.66 \
    matplotlib \
    boto3 \
    botocore \
    scikit-image==0.19.3 \
    cython==0.29.33 \
    "setuptools<60" \
    --root-user-action=ignore

# Clone LaMa and patch requirements
RUN git clone https://github.com/advimman/lama.git /workspace/lama
WORKDIR /workspace/lama
RUN echo 'pyyaml \n\
tqdm \n\
numpy==1.23.0 \n\
easydict==1.9.0 \n\
scikit-image==0.17.2 \n\
scikit-learn==1.0.2 \n\
opencv-python==4.6.0.66 \n\
tensorflow==2.10.0 \n\
joblib \n\
matplotlib \n\
pandas \n\
albumentations==0.5.2 \n\
hydra-core==1.1.0 \n\
pytorch-lightning==1.2.9 \n\
tabulate \n\
kornia==0.5.0 \n\
webdataset \n\
packaging \n\
wldhx.yadisk-direct' > requirements.txt
RUN pip install -r requirements.txt --root-user-action=ignore

# -------- PREVENT PyYAML uninstall error --------
RUN pip install --ignore-installed PyYAML==6.0 --root-user-action=ignore


# Clone ZITS++ and patch requirements
WORKDIR /workspace
RUN git clone https://github.com/ewrfcas/ZITS-PlusPlus.git
WORKDIR /workspace/ZITS-PlusPlus
RUN cat requirements.txt
# Remove torch/vision and broken sync_batchnorm lines
RUN sed -i '/torch==/d' requirements.txt && \
    sed -i '/torchvision==/d' requirements.txt && \
    sed -i '/sync_batchnorm==/d' requirements.txt && \
    sed -i 's/numpy==1.20.1/numpy==1.23.0/' requirements.txt && \
    sed -i 's/scikit_image==0.15.0/scikit-image==0.17.2/' requirements.txt && \
    sed -i 's/opencv_python==4.5.5.62/opencv-python==4.6.0.66/' requirements.txt

RUN cat requirements.txt
RUN pip install -r requirements.txt --root-user-action=ignore

# Copy your scripts
COPY entrypoint.sh /entrypoint.sh
COPY gpu_detector.py /workspace/gpu_detector.py
COPY s3_handler.py /workspace/s3_handler.py
COPY video_processor.py /workspace/video_processor.py
RUN chmod +x /entrypoint.sh

# Model dir
RUN mkdir -p /workspace/lama/big-lama

WORKDIR /workspace
ENTRYPOINT ["/entrypoint.sh"]

