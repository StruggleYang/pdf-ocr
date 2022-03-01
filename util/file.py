#!/usr/bin/env python
# coding:utf-8
# -*- coding: UTF-8 -*-
import os
import subprocess
import sys


def os_open_file(file_path):
    """
    使用操作系统的默认程序打开文件
    """
    if sys.platform == 'darwin':  # mac os
        subprocess.call(["open", file_path])
    elif sys.platform == 'win32':  # windows
        os.startfile(file_path)
    else:  # linux
        subprocess.call(["xdg-open", file_path])
