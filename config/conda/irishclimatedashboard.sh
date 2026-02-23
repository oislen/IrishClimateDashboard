# create and activate new environment
conda deactivate
conda env remove --name irishclimatedashboard
conda create --name irishclimatedashboard python=3 --yes
conda activate irishclimatedashboard

# update conda version
conda update -n base conda --yes

# install relevant libraries
pip install -r ../../requirements.txt

# export environment to .yml file
conda env export > irishclimatedashboard.yml
