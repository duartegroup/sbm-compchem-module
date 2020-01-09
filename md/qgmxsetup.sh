dl_qgmx () {
    curl https://raw.githubusercontent.com/duartegroup/sbmcc/master/md/qgmx_fn.sh >> ~/.bash_profile
    source ~/.bash_profile
    module load gromacs/2018.6__single
}

dl_qgmx
