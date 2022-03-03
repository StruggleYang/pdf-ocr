#/bin/bash
system=$(uname -s)

if (($system == "Darwin")); then
    if [ ! -f "setup.py" ]; then
        source ~/.bash_profile
        py2applet --make-setup main.py
    fi
    # 打包
    python setup.py py2app -A
fi
