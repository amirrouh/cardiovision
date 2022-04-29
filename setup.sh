# Create the required environments
conda create --name cardiovision python=3.8 -y
conda create --name cnn python=3.6 -y
conda create --name landmark python=3.8 -y
conda create --name valve python=3.7 -y
conda create --name calcification python=3.8 -y

conda activate cardiovision
codna install tqdm

# Setting up cnn environment
conda activate cnn
conda install tensorflow-gpu=1.14 -y
conda install keras -y
conda install -c simpleitk simpleitk -y




