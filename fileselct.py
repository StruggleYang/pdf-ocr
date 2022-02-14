#!/usr/bin/env python
# coding:utf-8
"""
  Created: 2014/8/26
"""
import os
import re
import wx
import pdfplumber
import pandas as pd


class Customer:
    time = ''  # 时间
    insurance_categories = ''  # 保险类别
    insurance_company = ''  # 保险公司
    insurant = ''  # 客户｜被保险人
    id_number = ''  # 证件号()
    plate_number = ''  # 车牌号
    insured_amount = 0  # 保险金额

    def not_empty(self):
        yes = False
        if self.insurant and self.insurance_company and self.insurance_categories and self.time:
            yes = True
        return yes


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
                data = {'签单时间': [], '客户': [],
                        '身份证': [], '公司名称': [], '保险类别': []}
                for file in files:
                    if file.endswith('.pdf'):
                        file_path = '%s/%s' % (dlg.GetPath(), file)
                        customer = self.readPdf(file_path)
                        if customer.not_empty():
                            data['签单时间'].append(customer.time)
                            data['客户'].append(customer.insurant)
                            data['身份证'].append(customer.id_number)
                            data['公司名称'].append(customer.insurance_company)
                            data['保险类别'].append(customer.insurance_categories)
                print(data)
                self.pd_toexcel(data, '%s/统计.xlsx' % dlg.GetPath())

        dlg.Destroy()

    def pd_toexcel(self, data, file_name):
        """ pandas方式 """
        # 创建DataFrame
        df = pd.DataFrame(data)
        # 存表，去除原始索引列（0,1,2...）
        df.to_excel(r'%s' % file_name, index=False)

    def readPdf(self, file):
        company_keys = ['大地财产保险', '太平洋财产保险', '太平保险',
                        '中国人民财产保险', '平安保险', '天平保险', '紫金财产保险']
        date_pt = r'签单日期[:|：]\s{0,}(\d\d\d\d[-|\\|\/]\d{1,2}[-|\\|\/]\d{1,2})'
        id_number_18 = r'([1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx])'
        id_number_15 = r'([1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3})'
        with pdfplumber.open(file) as pdf:
            print(file)
            customer = Customer()
            for page in pdf.pages:
                all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
                if not customer.insurance_categories:
                    if '强制' in all_content:
                        customer.insurance_categories = '交强'
                    else:
                        customer.insurance_categories = '商业'
                    tables = page.extract_table()
                if not customer.time:
                    if '签单日期':
                        date = re.findall(date_pt, all_content)
                        if date:
                            customer.time = date[0]
                if tables:
                    for item in tables:
                        valid = list(filter(lambda x: x != None, item))
                        for index in range(len(valid)):
                            strs = valid[index]
                            if not customer.insurant:
                                if '被保险人' in strs.replace('\n', ''):
                                    if not '\n' in strs:
                                        customer.insurant = strs.replace(
                                            '被保险人：', '')
                                        if '被保险人' in customer.insurant:
                                            customer.insurant = valid[1]
                                    else:
                                        names = list(filter(
                                            lambda x: x != '被\n保\n险\n人' and x != '名 称', valid))
                                        if names:
                                            customer.insurant = names[-1]
                            if not customer.insurance_company:
                                for cm in company_keys:
                                    if cm in strs:
                                        customer.insurance_company = cm
                            if not customer.time:
                                if '签单日期' in strs.replace('\n', ''):
                                    date = re.findall(date_pt, strs)
                                    if date:
                                        customer.time = date[0]
                            if not customer.id_number:
                                id_number = re.findall(id_number_18, strs)
                                if not id_number:
                                    id_number = re.findall(id_number_15, strs)
                                if id_number:
                                    customer.id_number = id_number[0][0]
                            if not customer.plate_number:
                                xxx = strs.replace('\n', '')
                                if '号' in xxx and '牌' in xxx and '号' in xxx and '码' in xxx:
                                    print(valid)
                                    print(xxx)
                                    if not '\n' in strs:
                                        customer.plate_number = strs.replace(
                                            '号牌号码：', '')
                                        if '号牌号码' in customer.insurant:
                                            customer.plate_number = valid[1]
                                    else:
                                        names = list(filter(
                                            lambda x: x != '号\n牌\n号\n码' and x != '名 称', valid))
                                        if names:
                                            customer.plate_number = names[-1]

            print('签单时间', customer.time)
            print('客户', customer.insurant)
            print('身份证', customer.id_number)
            print('车牌号', customer.plate_number)
            print('公司名称', customer.insurance_company)
            print('保险类别', customer.insurance_categories)
            return customer


###############################################################################
if __name__ == '__main__':
    frame = wx.PySimpleApp()
    app = DirDialog()
    app.Show()
    frame.MainLoop()
