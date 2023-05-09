# output_dir = "/mnt/d/sandra/sample/"
# is mounted to docker cv_container /home/data => choose empty folder
output_dir = "/mnt/c/Users/SH1389/Documents/docker_files/container1/"
#training_data_directory = "/mnt/d/sandra/sample/"
training_data_directory = "/mnt/c/Users/SH1389/Documents/data/training_data/resampled/"
#input_file = "/mnt/d/sandra/sample/images/aCT1.nrrd"
input_file = "/mnt/c/Users/SH1389/Documents/data/training_data/resampled/images/rct42.nrrd"
container_name = 'cv_container1'

# component can be "aorta"; "lv"
component = "aorta"

# verbose is useful for debugging purpose
verbose = True

# True when GPU is available
GPU = True
