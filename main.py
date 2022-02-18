#!/usr/bin/env python
# coding:utf-8
"""
  Created: 2014/8/26
"""
import sys
import wx
from util.statistics import analyse_and_export
from util.logging import logger


###############################################################################


class DirDialog(wx.Frame):
    files_names = None
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        f = wx.Frame.__init__(self, None, -1, u"❤️保险单识别统计程序-YM专用❤️",
                              size=wx.Size(800, 500))
        if sys.platform == "win32":
            import win32api
            # set window icon,窗口左上角图标
            exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
            icon = wx.Icon(exeName, wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
        b = wx.Button(self, -1, u"选择需要解析的文件夹",
                      style=wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)

        # put some text with a larger bold font on it
        self.files_names = wx.StaticText(
            self, label="暂未选择文件！！！", pos=(10, 40), style=wx.ALIGN_LEFT)
        self.Center()

    # ----------------------------------------------------------------------
    def OnButton(self, event):
        """"""
        dlg = wx.DirDialog(self, u"选择需要解析的文件夹", style=wx.DD_DEFAULT_STYLE)
        self.files_names.SetLabel('正在解析...(请勿关闭程序)')
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetPath():
                logger.info('已选文件夹:%s' % dlg.GetPath())
                self.files_names.SetLabel('已选解析文件目录:%s' % dlg.GetPath())
                self.files_names.LabelText = analyse_and_export(
                    dlg.GetPath(), self.files_names.LabelText)
        elif dlg.ShowModal() == wx.ID_CANCEL:
            self.files_names.LabelText = '已取消选择，请重新选择解析目录'
        dlg.Destroy()


###############################################################################
if __name__ == '__main__':
    frame = wx.App()
    app = DirDialog()
    app.Show()
    frame.MainLoop()
