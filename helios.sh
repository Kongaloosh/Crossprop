#!/bin/bash
#PBS -A pau-670-aa
#PBS -l walltime=12:00:00
#PBS -l nodes=1:gpus=4
#PBS -r n

module load compilers/gcc/4.8.5 cuda/7.5 libs/cuDNN/5
module load apps/python/2.7.10
virtualenv ~/venv
source ~/venv/bin/activate
pip install numpy
pip install /software-gpu/apps/python/wheelhouse/tensorflow-0.12.1+helios-cp27-none-linux_x86_64.whl
pip install matplotlib

cd ~/Crossprop
export PYTHONPATH=$PWD
echo "Current working directory is `pwd`"

echo "Starting run at: `date`"
python tfTrainGEOFF.py
echo "Job finished with exit code $? at: `date`"