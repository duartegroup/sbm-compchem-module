
qgmx () {
    echo '#!/bin/bash' > qgmx.sh
    echo '#SBATCH --ntasks-per-node=16' >> qgmx.sh
    echo '#SBATCH --time=48:00:00' >> qgmx.sh
    echo '#SBATCH --job-name=gmx_mpi' >> qgmx.sh
    echo module load gromacs/2018.6__single >> qgmx.sh
    echo gmx_mpi mdrun -deffnm ${1%.tpr} >> qgmx.sh
    sbatch qgmx.sh
	rm qgmx.sh
}

