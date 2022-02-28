#!/usr/bin/env python
# coding:utf-8
"""
  Created: 2014/8/26
"""
import os
import time
from util.pdf import read_pdf
from util.execl import pandas_toexcel
from util.log import logger


###############################################################################
def analyse_and_export(select_path, append_text=''):
    """
    分析和导出
    """
    files = os.listdir(select_path)
    data = {'日期': [], '客户': [],
            '车牌号': [], '销售': [], '渠道': [], '公司': [], '初登': [], '电话': [], '身份证号': [], '车架号': [], '发动机号': [], '车型': [],
            '保险到期': [], '驾意险': [], '交强': [], '商业': [], '合计': [], '佣金比例': [], '手续费': [], '实收': [], '返点': [], '利润总额': [],
            '结算': [], '来源文件1(单击打开)': [], '来源文件2(单击打开)': [], '来源文件3(单击打开)': []}
    all_customer = []
    for file in files:
        if file.endswith('.pdf'):
            file_path = os.path.join(select_path, file)
            (new_all_customer, successful, description) = read_pdf(
                file_path, all_customer)
            all_customer = new_all_customer
            if successful:
                ok = '已解析完成：%s=>%s' % (
                    file, description)
                logger.info(ok)
                append_text = '%s\n\n✅%s' % (
                    append_text, ok)
            else:
                err = '未解析到内容：%s=>%s' % (file, description)
                logger.info(err)
                append_text = '%s\n\n❌%s' % (
                    append_text, err)
    # 按照时间排序
    all_customer_sorted = sorted(all_customer, key=lambda e: e.date)
    for cindex in range(len(all_customer_sorted)):
        customer = all_customer_sorted[cindex]
        execl_index = cindex + 2  # 要加上头部标题
        if customer.not_empty():
            data['日期'].append(customer.date)
            data['客户'].append(customer.insurant)
            data['车牌号'].append(customer.plate_number)
            data['销售'].append('')
            data['渠道'].append('')
            data['公司'].append(customer.insurance_company.replace(
                '中国', '').replace('财产保险', ''))
            data['初登'].append(customer.first_date)
            data['电话'].append(customer.tel)
            data['身份证号'].append(customer.id_number)
            data['车架号'].append(customer.chassis_number)
            data['发动机号'].append(customer.engine_number)
            data['车型'].append(customer.car_models)
            data['保险到期'].append(customer.expire_date)
            data['驾意险'].append(customer.accident_amount)
            data['交强'].append(customer.jq_amount)
            data['商业'].append(customer.business_amount)
            data['合计'].append(
                "=SUM({驾意险}{row}+{交强}{row}+{商业}{row})".format(
                    row=execl_index,
                    驾意险=location_on_execl(data, '驾意险'),
                    交强=location_on_execl(data, '交强'),
                    商业=location_on_execl(data, '商业')))
            data['佣金比例'].append(0.00)
            data['手续费'].append('=SUM({合计}{row}*{佣金比例}{row})'.format(
                row=execl_index,
                合计=location_on_execl(data, '合计'),
                佣金比例=location_on_execl(data, '佣金比例')))
            data['实收'].append(0)
            data['返点'].append('=SUM({合计}{row}-{实收}{row})'.format(
                row=execl_index,
                合计=location_on_execl(data, '合计'),
                实收=location_on_execl(data, '实收')))
            data['利润总额'].append('=SUM({手续费}{row}-{返点}{row})'.format(
                row=execl_index,
                手续费=location_on_execl(data, '手续费'),
                返点=location_on_execl(data, '返点')))
            data['结算'].append('未结')
            files = customer.from_file.split(",")
            for index in range(3):
                link = ""
                if index < len(files):
                    text = str(files[index]).replace("\\\\", "@@").replace("/", "@@").split("@@")[-1]
                    link = '=HYPERLINK("%s","%s")' % (files[index], text)
                data['来源文件%d(单击打开)' % (index + 1)].append(link)

    execl_path = None
    if all_customer:
        execl_path = os.path.join(select_path, ('%s保险单解析汇总.xlsx' % time.strftime(
            "%Y-%m-%d-%H-%M-%S", time.localtime())))
        pandas_toexcel(data, execl_path)
        ok = '共解析出%d条记录，结果execl文件位于:%s' % (
            len(all_customer), execl_path)
        logger.info(ok)
        append_text = '%s\n\n%s' % (
            append_text, ok)
    else:
        err = '本次没有解析到有效内容,请检查目录是否正确！！！'
        logger.error(err)
        append_text = '%s\n\n%s' % (
            append_text, err)
    return (append_text, execl_path)


def location_on_execl(dict_obj: dict, field: str):
    """
    获得字段在execl中的位置，ABC
    """
    location = None
    a_to_z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    a_to_z_arr = list(a_to_z)
    if len(dict_obj.keys()) > len(a_to_z_arr):
        for item in a_to_z_arr:
            a_to_z_arr.append('A%s' % item)
    if len(dict_obj.keys()) > len(a_to_z_arr):
        for item in a_to_z_arr:
            a_to_z_arr.append('B%s' % item)
    zipped = zip(list(dict_obj.keys()), a_to_z_arr)
    for (key, lc) in zipped:
        if key == field:
            location = lc
    return location
