#!/usr/bin/env python
# coding:utf-8
"""
GUI窗口页面
"""
import sys
import wx
from util.statistics import analyse_and_export
from util.log import logger
from util.file import os_open_file


###############################################################################


class DirDialog(wx.Frame):
    files_names = None
    open_result = True
    selected = False
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.fm = wx.Frame.__init__(self, None, -1, u"❤️保险单识别统计程序-YM专用❤️",
                                    size=wx.Size(800, 500))
        # 初始化滚动条
        self.scrollWin = wx.ScrolledWindow(self, -1, size=wx.Size(800, 500))
        # 设置windows 的窗口小图标和应用icon一致
        if sys.platform == "win32":
            import win32api
            # set window icon,窗口左上角图标
            exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
            icon = wx.Icon(exeName, wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
        # 文件夹选择按钮
        b = wx.Button(self.scrollWin, -1, u"选择需要解析的文件夹",
                      style=wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)
        # 是否自动开的复选框
        self.cb1 = wx.CheckBox(self.scrollWin, label='自动打开解析结果excel', pos=(180, 5))
        self.cb1.SetValue(self.open_result)
        self.Bind(wx.EVT_CHECKBOX, self.onChecked)

        # 提示文本
        self.files_names = wx.StaticText(
            self.scrollWin, label="暂未选择文件！！！", pos=(10, 40), style=wx.ALIGN_LEFT)
        # 窗口居中
        self.Center()

    def onChecked(self, e):
        """
        复选框事件监听
        """
        cb = e.GetEventObject()
        self.open_result = cb.GetValue()

    # ----------------------------------------------------------------------
    def OnButton(self, event):
        """
        文件按钮点击事件
        """
        if self.selected:
            wx.MessageBox("正在解析...等待解析结束后可选择", parent=self.scrollWin)
            return
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        dlg = wx.DirDialog(self, u"请选择需要解析的pdf文件夹", style=style)

        self.files_names.SetLabel('正在解析...(请勿关闭程序)')
        # 选择了文件夹
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetPath():
                self.selected = True
                logger.info('已选文件夹:%s' % dlg.GetPath())
                self.files_names.SetLabel('已选解析文件目录:%s' % dlg.GetPath())
                # 主要的解析导出流出
                (label_text, export_path) = analyse_and_export(
                    dlg.GetPath(), self.files_names.LabelText)
                self.files_names.LabelText = label_text
                if export_path and self.open_result:
                    os_open_file(export_path)
                # 使用文本的大小来设置滚动条
                w, h = self.files_names.GetSize()
                # 滚动条
                self.scrollWin.SetScrollbars(0, 1, 0, h + 60)
                self.scrollWin.SetScrollRate(1, 1)  # Pixels per scroll increment
                self.selected = False
        elif dlg.ShowModal() == wx.ID_CANCEL:
            self.selected = False
            self.files_names.LabelText = '已取消选择，请重新选择解析目录'
        dlg.Destroy()


###############################################################################
if __name__ == '__main__':
    frame = wx.App()
    app = DirDialog()
    app.Show()
    frame.MainLoop()
