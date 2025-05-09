dl_qorca () {
    mkdir -p ~/scripts/
    wget https://raw.githubusercontent.com/duartegroup/sbm-compchem-module/master/qorcaCoulson.py -O ~/scripts/qorca
    chmod +x ~/scripts/qorca
    echo "export PATH=\$HOME/scripts:\$PATH" >> ~/.bash_profile
    source ~/.bash_profile
}

dl_qpython_autode () {
    wget https://raw.githubusercontent.com/duartegroup/sbm-compchem-module/master/qpythonAutodE.py -O ~/scripts/qpython
    chmod +x ~/scripts/qpython
    source /usr/local/conda/autode/install
}

dl_qorca
dl_qpython_autode
