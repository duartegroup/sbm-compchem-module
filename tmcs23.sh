dl_qorca () {
    wget https://raw.githubusercontent.com/duartegroup/sbm-compchem-module/master/qorcaCoulson.py -O ~/qorca
    chmod +x ~/qorca
    echo "export PATH=\$HOME:\$PATH" >> ~/.bash_profile
    source ~/.bash_profile
}

dl_qorca
