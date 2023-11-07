# Setup ubuntu with Nvidia cuda support
FROM nvidia/cuda:12.2.2-base-ubuntu20.04

# Install base utilities
RUN apt update && \
    apt install -y build-essential  && \
    apt install -y wget && \
    apt install -y vim && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Installing conda toolkit to enable GPU
RUN apt -y update
RUN DEBIAN_FRONTEND=noninteractive apt -yq install git nano libtiff-dev cuda-toolkit-11-4

# settings
ENV AM_I_IN_A_DOCKER_CONTAINER Yes

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

# preparing the working directory
WORKDIR /home/app

# copying project code to the container
COPY /. .

RUN sed -e "s/\r//g" scripts/cardiovision.sh && \
    chmod u+x scripts/cardiovision.sh && \
    sed -e "s/\r//g" bash_script.sh && \
    chmod u+x bash_script.sh && \
    ./bash_script.sh

RUN mkdir /home/data
