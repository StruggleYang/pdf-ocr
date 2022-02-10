#!/usr/bin/env python
# coding:utf-8
"""
  Created: 2014/8/26
"""

import os
import wx
import pdfplumber


###############################################################################
class DirDialog(wx.Frame):
    files_names = None
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, -1, u"选择需要解析的文件夹")
        b = wx.Button(self, -1, u"选择需要解析的文件夹",
                      style=wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)

        # put some text with a larger bold font on it
        self.files_names = wx.StaticText(
            self, label="暂未选择文件！！！", pos=(10, 40))
        self.Center()

    # ----------------------------------------------------------------------
    def OnButton(self, event):
        """"""
        dlg = wx.DirDialog(self, u"选择需要解析的文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetPath():
                self.files_names.LabelText = '已选解析文件目录:%s' % dlg.GetPath()
                files = os.listdir(dlg.GetPath())
                for file in files:
                    if file.endswith('.pdf'):
                        file_path = '%s/%s' % (dlg.GetPath(), file)
                        print(file_path)
                        self.readPdf(file_path)

        dlg.Destroy()

    def readPdf(self, file):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                print('页数', page.page_number)
                all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
                tables = page.extract_table()
                if tables:
                    for item in tables:
                        print(item)


###############################################################################
if __name__ == '__main__':
    frame = wx.PySimpleApp()
    app = DirDialog()
    app.Show()
    frame.MainLoop()
