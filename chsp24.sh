dl_qorca () {
    mkdir -p ~/bin/
    wget https://raw.githubusercontent.com/duartegroup/sbm-compchem-module/master/qorcaARC.py -O ~/bin/qorca
    chmod +x ~/bin/qorca
}

dl_qpython_autode () {
    wget https://raw.githubusercontent.com/duartegroup/sbm-compchem-module/master/qpythonARC.py -O ~/bin/qpython
    chmod +x ~/bin/qpython
    if ! command -v conda &> /dev/null; then
        echo "Installing conda..."
        wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -q -O miniconda.sh
        # The installer prints loads to the terminal, so redirect it (so it doesn't appear)
        eval "bash miniconda.sh -b -p \"$HOME/miniconda\"" > /dev/null
        rm miniconda.sh
        eval "$("$HOME"/miniconda/bin/conda shell.bash hook)" > /dev/null
        eval "conda init bash" > /dev/null
        echo "done\n"
        echo "Installed miniconda to $HOME/miniconda with\n"
        python --version
    fi
}

dl_qorca
dl_qpython_autode
