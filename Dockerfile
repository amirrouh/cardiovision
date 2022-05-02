FROM frolvlad/alpine-miniconda3

WORKDIR /home/tmp

# COPY bash_script.sh .

# RUN chmod +x ${project}.sh

# RUN sh ./${project}.sh

WORKDIR /home/app

COPY * .

# Activate anaconda
CMD ["eval", "$(conda shell.bash hook)"]