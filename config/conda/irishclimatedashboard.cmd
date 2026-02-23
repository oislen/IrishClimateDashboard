:: create and activate new environment
call conda deactivate
call conda env remove --name irishclimatedashboard
call conda create --name irishclimatedashboard python=3 --yes
call conda activate irishclimatedashboard

:: update conda version
call conda update -n base conda --yes

:: install relevant libraries
call pip install -r ..\..\requirements.txt

:: export environment to .yml file
call conda env export > irishclimatedashboard.yml
