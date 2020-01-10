dl_nics () {
    mkdir -p ~/nicspy
    wget https://raw.githubusercontent.com/duartegroup/sbmcc/master/carbene/nics1.py -O ~/nicspy/nics1.py
    wget https://raw.githubusercontent.com/duartegroup/sbmcc/master/carbene/nics2.py -O ~/nicspy/nics2.py
    wget https://raw.githubusercontent.com/duartegroup/sbmcc/master/carbene/nics1 -O ~/nicspy/nics1
    wget https://raw.githubusercontent.com/duartegroup/sbmcc/master/carbene/nics2 -O ~/nicspy/nics2
    chmod +x ~/nicspy/nics1
    chmod +x ~/nicspy/nics2
    echo "export PATH=\$HOME/nicspy:\$PATH" >> ~/.bash_profile
    source ~/.bash_profile
}

dl_nics
