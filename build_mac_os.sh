#/bin/bash
source ~/.bash_profile
py2applet --make-setup fileselct.py -y
python setup.py py2app -A
