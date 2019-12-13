dl_qorca () {
    wget https://raw.githubusercontent.com/duartegroup/sbmcc/master/qorca -O ~/qorca
    chmod +x ~/qorca
    echo "export PATH=$HOME:$PATH" >> ~/.bash_profile
    source ~/.bash_profile
}

dl_qorca
