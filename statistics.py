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
    date = ''  # 本次保险时间
    insurance_company = ''  # 保险公司，渠道
    insurant = ''  # 客户｜被保险人
    id_number = ''  # 证件号()
    plate_number = ''  # 车牌号
    engine_number = ''  # 发动机号码
    chassis_number = ''  # 车架号
    first_date = ''  # 初次登记日期
    expire_date = ''  # 到期日期
    accident_amount = 0  # 意外险金额
    jq_amount = 0  # 交强险
    business_amount = 0  # 商业险

    def not_empty(self):
        """
        不是空的
        """
        yes = False
        if self.insurant and self.id_number and self.plate_number:
            yes = True
        return yes

    def total_amount(self):
        """
        金额总计
        """
        return float(self.accident_amount)+float(self.jq_amount)+float(self.business_amount)

    def identity(self, insurant, id_number, plate_number):
        """
        是同一客户
        """
        return insurant == self.insurant and id_number == self.id_number and plate_number == self.plate_number


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
                data = {'登记日期': [], '客户': [],
                        '身份证': [], '车牌号': [], '发动机号': [], '车架号': [], '初登日期': [], '到期日期': [], '渠道': [], '意外险': [], '交强': [], '商业': [], '合计费用': [], '佣金比例': [], '手续费': [], '返点实收': [], '销售': [], '渠道对接': []}
                all_customer = []
                for file in files:
                    if file.endswith('.pdf'):
                        file_path = '%s/%s' % (dlg.GetPath(), file)
                        all_customer = self.readPdf(file_path, all_customer)
                for customer in all_customer:
                    if customer.not_empty():
                        data['登记日期'].append(customer.date)
                        data['客户'].append(customer.insurant)
                        data['身份证'].append(customer.id_number)
                        data['车牌号'].append(customer.plate_number)
                        data['发动机号'].append(customer.engine_number)
                        data['车架号'].append(customer.chassis_number)
                        data['初登日期'].append(customer.first_date)
                        data['到期日期'].append(customer.expire_date)
                        data['渠道'].append(customer.insurance_company)
                        data['意外险'].append(customer.accident_amount)
                        data['交强'].append(customer.jq_amount)
                        data['商业'].append(customer.business_amount)
                        data['合计费用'].append(customer.total_amount())
                        data['佣金比例'].append('')
                        data['手续费'].append('')
                        data['返点实收'].append('')
                        data['销售'].append('')
                        data['渠道对接'].append('')
                self.pd_toexcel(data, '%s/统计.xlsx' % dlg.GetPath())

        dlg.Destroy()

    def pd_toexcel(self, data, file_name):
        """ pandas方式 """
        # 创建DataFrame
        df = pd.DataFrame(data)
        # 存表，去除原始索引列（0,1,2...）
        df.to_excel(r'%s' % file_name, index=False)

    def readPdf(self, file, all_customer):
        company_keys = ['大地财产保险', '太平洋财产保险', '太平保险',
                        '中国人民财产保险', '平安保险', '天平保险', '紫金财产保险']
        date_pt = r'签单日期\s{0,}[:|：]\s{0,}(\d{4}[年|,|\-|\\|\/]\d{1,2}[月|,|\-|\\|\/]\d{1,2})'
        id_number_18 = r'([1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx])'
        id_number_15 = r'([1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3})'
        car_number_pt = r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1})'
        rmb_pt = r'[￥|¥]\s*[:|：]\s*([0-9,]+\.\d+)\s*元'
        engine_number_pt = r'发动机号\W{0,}\s{0,}[:|：]\s{0,}([0-9+a-z+A-Z+]+)'
        chassis_number_pt = r'[\S{0,}]+[车架号\W{0,}|\W{0,}识别代码\W{0,}]\W{0,}\s{0,}[:|：]\s{0,}([0-9+a-z+A-Z+]+)'
        first_date_pt = r'[\s|初次]+登记日期\s{0,}[:|：]\s{0,}(\d\d\d\d[年|,|\-|\\|\/]\d{1,2}[月|,|\-|\\|\/]\d{1,2})'
        expire_date_pt = r'保险期间.*起至\s{0,}(\d{4}\s{0,}[年|,|\-|\\|\/]\s{0,}\d{1,2}\s{0,}[月|,|\-|\\|\/]\s{0,}\d{1,2}\s{0,}日).*'

        insurance_categories_list = ['意外险', '交强', '商业']
        insurance_categories = ''
        insured_amount = 0
        plate_number = ''
        engine_number = ''
        chassis_number = ''
        first_date = ''
        expire_date = ''
        id_number = ''
        date = ''
        insurant = ''
        insurance_company = ''
        with pdfplumber.open(file) as pdf:
            print(file)
            for page in pdf.pages:
                all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
                if not insurance_categories:
                    if '强制保险' in all_content:
                        insurance_categories = '交强'
                    else:
                        insurance_categories = '商业'
                if not date:
                    if '签单日期' in all_content:
                        date_matchs = re.findall(date_pt, all_content)
                        if date_matchs:
                            date = date_matchs[0].replace(
                                ' ', '')
                tables = page.extract_table()
                if tables:
                    for item in tables:
                        valid = list(filter(lambda x: x != None, item))
                        for index in range(len(valid)):
                            strs = valid[index]
                            xxx = strs.replace('\n', '')
                            if not insurant:
                                if '被保险人' in xxx:
                                    if not '\n' in strs:
                                        insurant = strs.replace(
                                            '被保险人：', '')
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
                            if not date:
                                if '签单日期' in xxx:
                                    date_matchs = re.findall(date_pt, strs)
                                    if date_matchs:
                                        date = date_matchs[0].replace(
                                            ' ', '')
                            if not id_number:
                                id_number_matchs = re.findall(
                                    id_number_18, strs)
                                if not id_number_matchs:
                                    id_number_matchs = re.findall(
                                        id_number_15, strs)
                                if id_number_matchs:
                                    id_number = id_number_matchs[0][0]
                            if not plate_number:
                                plate_number_matchs = re.findall(
                                    car_number_pt, xxx)
                                if plate_number_matchs:
                                    plate_number = plate_number_matchs[0]
                            if not engine_number:
                                if '发动机号' in xxx:
                                    engine_number_matchs = re.findall(
                                        engine_number_pt, xxx)
                                    if engine_number_matchs:
                                        engine_number = engine_number_matchs[0]
                                    else:
                                        engine_number = valid[index+1]
                            if not chassis_number:
                                if '车架号' in xxx or '识别代码' in xxx:
                                    chassis_number_matchs = re.findall(
                                        chassis_number_pt, xxx)
                                    if chassis_number_matchs:
                                        chassis_number = chassis_number_matchs[0]
                                    else:
                                        chassis_number = valid[index+1]
                            if not first_date:
                                if '登记日期' in xxx:
                                    first_date_matchs = re.findall(
                                        first_date_pt, xxx)
                                    if first_date_matchs:
                                        first_date = first_date_matchs[0].replace(
                                            ' ', '')
                                    else:
                                        first_date = valid[index+1].replace(
                                            ' ', '')
                            if not expire_date:
                                if '保险期间' in xxx:
                                    expire_date_matchs = re.findall(
                                        expire_date_pt, xxx)
                                    if expire_date_matchs:
                                        expire_date = expire_date_matchs[0].replace(
                                            ' ', '')
                            if not insured_amount:
                                if '人民币大写' in xxx:
                                    insured_amount_matchs = re.findall(
                                        rmb_pt, xxx)
                                    if insured_amount_matchs:
                                        insured_amount = str(insured_amount_matchs[0]).replace(
                                            ',', '')

            match_customer = list(filter(lambda x: x.identity(
                insurant, id_number, plate_number), all_customer))
            customer = Customer()
            if match_customer:
                customer = match_customer[0]
            # 保险类别区分
            if insurance_categories == '商业':
                customer.business_amount = insured_amount
            elif insurance_categories == '交强':
                customer.jq_amount = insured_amount
            else:
                customer.accident_amount = insured_amount
            if not customer.date:
                customer.date = date
            if not customer.insurance_company:
                customer.insurance_company = insurance_company
            if not customer.engine_number:
                customer.engine_number = engine_number
            if not customer.chassis_number:
                customer.chassis_number = chassis_number
            if not customer.first_date:
                customer.first_date = first_date
            if not customer.expire_date:
                customer.expire_date = expire_date
            if not customer.not_empty():
                customer.insurant = insurant
                customer.id_number = id_number
                customer.plate_number = plate_number
                all_customer.append(customer)
            return all_customer


###############################################################################
if __name__ == '__main__':
    frame = wx.PySimpleApp()
    app = DirDialog()
    app.Show()
    frame.MainLoop()
