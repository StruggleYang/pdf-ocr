#/bin/bash
source ~/.bash_profile
py2applet --make-setup statistics.py -y
python setup.py py2app -A
