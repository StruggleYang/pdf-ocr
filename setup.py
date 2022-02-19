import sys
from setuptools import setup
#from distutils.core import setup
if sys.platform == 'win32':
    import py2exe
else:
    import py2app

"""
 py2app/py2exe build script for main.


 Usage (Mac OS X):
     python setup.py py2app

 Usage (Windows):
     python setup.py py2exe
 """

mainscript = 'main.py'
name="保险单识别系统"
extra_options = dict(
    # Normally unix-like platforms will use "setup.py install"
    # and install the main script as such
    scripts=[mainscript],
)
if sys.platform == 'darwin':
    extra_options = dict(
        setup_requires=['py2app'],
        app=[mainscript],
        # Cross-platform applications generally expect sys.argv to
        # be used for opening files.
        options=dict(py2app=dict(argv_emulation=True,iconfile='source/appicon1.icns')),
    )
elif sys.platform == 'win32':
    extra_options = dict(
        setup_requires=['py2exe'],
        windows =[{ #windows 与 console有区别，console打包后的程序运行有终端控制台窗口弹出
            "dest_base": name, # 打包后的名字
            "script": mainscript,                    ### Main Python script
            "icon_resources": [(1, "source/appicon1.ico")]     ### Icon to embed into the PE file.
        }],
    )


setup(
    name=name,
    **extra_options
)
