dl_nics () {
    wget https://raw.githubusercontent.com/yongrenjie/sbmcc/master/carbene/nics1.py -O ~/nics1.py
    wget https://raw.githubusercontent.com/yongrenjie/sbmcc/master/carbene/nics2.py -O ~/nics2.py
    if [[ ":$PATH" != *":$HOME:"* ]]; then
        echo 'export PATH=$HOME:$PATH' >> ~/.bash_profile
        source ~/.bash_profile
    fi
}

dl_nics
