dl_qorca () {
    curl https://raw.githubusercontent.com/yongrenjie/qcnmr-tools/master/arcus-b/qorca > ~/qorca
    chmod +x ~/qorca
    echo "export PATH=$HOME:$PATH" >> ~/.bash_profile
    source ~/.bash_profile
}

dl_qorca
