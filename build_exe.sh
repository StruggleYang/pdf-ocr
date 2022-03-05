#/bin/bash
# oonly windows run
#python setup.py py2exe # 这个打包功能不完整,部分文件打包后识别不了，详情见: https://github.com/jsvine/pdfplumber/issues/615
#pyinstaller -F -i source/appicon1.ico  main.py -n 保险单识别系统 --noconsole # 初次运行
pyinstaller 保险单识别系统.spec