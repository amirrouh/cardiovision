# Setup ubuntu with Nvidia cuda support
FROM nvidia/cuda:11.4.2-base-ubuntu20.04
RUN apt -y update
RUN DEBIAN_FRONTEND=noninteractive apt -yq install git nano libtiff-dev cuda-toolkit-11-4

# settings
ENV AM_I_IN_A_DOCKER_CONTAINER Yes

# Install miniconda
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 

# Setting up the environments
COPY bash_script.sh .
RUN chmod +x bash_script.sh
RUN sh ./bash_script.sh

# preparing the working directory
WORKDIR /home/app

# copying project code to the container
COPY /. .