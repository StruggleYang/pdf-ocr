#!/usr/bin/env python
# coding:utf-8
"""
  Created: 2014/8/26
"""
import os
import time
from util.pdf import read_pdf
from util.execl import pandas_toexcel


###############################################################################
def analyse_and_export(select_path, append_text=''):
    """
    分析和导出
    """
    files = os.listdir(select_path)
    data = {'日期': [], '客户': [],
            '车牌号': [], '销售': [], '渠道': [], '公司': [], '初登': [], '电话': [], '身份证号': [], '车架号': [], '发动机号': [], '车型': [], '保险到期': [], '驾意险': [], '交强': [], '商业': [], '合计': [], '佣金比例': [], '手续费': [], '实收': [], '返点': [], '利润总额': [], '结算': [], '来源文件': []}
    all_customer = []
    for file in files:
        if file.endswith('.pdf'):
            file_path = '%s/%s' % (select_path, file)
            (new_all_customer, successful, description) = read_pdf(
                file_path, all_customer)
            all_customer = new_all_customer
            if successful:
                append_text = '%s\n\n✅已解析完成：%s=>%s' % (
                    append_text, file, description)
            else:
                append_text = '%s\n\n❌未解析到内容：%s=>%s' % (
                    append_text, file, description)
    for customer in all_customer:
        if customer.not_empty():
            data['日期'].append(customer.date)
            data['客户'].append(customer.insurant)
            data['车牌号'].append(customer.plate_number)
            data['销售'].append('')
            data['渠道'].append('')
            data['公司'].append(customer.insurance_company.replace(
                '中国', '').replace('财产保险', ''))
            data['初登'].append(customer.first_date)
            data['电话'].append('')
            data['身份证号'].append(customer.id_number)
            data['车架号'].append(customer.chassis_number)
            data['发动机号'].append(customer.engine_number)
            data['车型'].append('')
            data['保险到期'].append(customer.expire_date)
            data['驾意险'].append(customer.accident_amount)
            data['交强'].append(customer.jq_amount)
            data['商业'].append(customer.business_amount)
            data['合计'].append(customer.total_amount())
            data['佣金比例'].append('')
            data['手续费'].append('')
            data['实收'].append('')
            data['返点'].append('')
            data['利润总额'].append('')
            data['结算'].append('未结')
            data['来源文件'].append(customer.from_file)
    if all_customer:
        execl_path = '%s/%s保险单解析汇总.xlsx' % (select_path, time.strftime(
            "%Y-%m-%d-%H-%M-%S", time.localtime()))
        pandas_toexcel(data, execl_path)
        append_text = '%s\n\n共解析出%d条记录，结果execl文件位于:%s' % (
            append_text, len(all_customer), execl_path)
    else:
        append_text = '%s\n\n本次没有解析到有效内容,请检查目录是否正确！！！' % (
            append_text)
    return append_text
