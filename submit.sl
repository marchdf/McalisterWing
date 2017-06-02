#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:10:00
#SBATCH -J mcalisterwing
#SBATCH -L SCRATCH
#SBATCH -C haswell

spack load nalu
module list

srun -n 64 naluX --version
