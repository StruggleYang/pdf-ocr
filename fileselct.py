#!/usr/bin/env python
# coding:utf-8
"""
  Created: 2014/8/26
"""

import os
import re
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
                        self.readPdf(file_path)

        dlg.Destroy()

    def readPdf(self, file):
        company_keys = ['大地财产保险', '太平洋财产保险', '太平保险',
                        '中国人民财产保险', '平安保险', '天平保险', '紫金财产保险']
        date_pt = r'(\d\d\d\d[-|\\|\/]\d{1,2}[-|\\|\/]\d{1,2})'
        with pdfplumber.open(file) as pdf:
            time = ''  # 时间
            insurance_categories = ''  # 保险类别
            insurance_company = ''  # 保险公司
            insurant = ''  # 客户｜被保险人
            id_number = ''  # 证件号()
            plate_number = ''  # 车牌号
            insured_amount = 0  # 保险金额
            print(file)
            for page in pdf.pages:
                all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
                if not insurance_categories:
                    if '强制' in all_content:
                        insurance_categories = '交强'
                    else:
                        insurance_categories = '商业'
                    tables = page.extract_table()
                if tables:
                    for item in tables:
                        valid = list(filter(lambda x: x != None, item))
                        for strs in valid:
                            if not insurant:
                                if '被保险人' in strs.replace('\n', ''):
                                    if not '\n' in strs:
                                        insurant = strs.replace('被保险人：', '')
                                        if '被保险人' in insurant:
                                            insurant = valid[1]
                                    else:
                                        names = list(filter(
                                            lambda x: x != '被\n保\n险\n人' and x != '名 称', valid))
                                        if names:
                                            insurant = names[-1]
                            if not insurance_company:
                                for cm in company_keys:
                                    if cm in strs:
                                        insurance_company = cm
                            if not time:
                                if '签单日期' in strs.replace('\n', ''):
                                    date = re.findall(date_pt, strs)
                                    if date:
                                        time = date[0]

            print('签单时间', time)
            print('客户', insurant)
            print('公司名称', insurance_company)
            print('保险类别', insurance_categories)


###############################################################################
if __name__ == '__main__':
    frame = wx.PySimpleApp()
    app = DirDialog()
    app.Show()
    frame.MainLoop()
