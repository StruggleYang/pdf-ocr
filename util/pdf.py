#!/usr/bin/env python
# coding:utf-8
from cmath import log
import re
import pdfplumber
from model.customer import Customer
from util.logging import logger

company_keys = ["中国人民财产保险", "中国大地财产保险", "中华联合财产保险", "中国太平洋财产保险", "中国平安财产保险", "天安财产保险", "史带财产保险", "华安财产保险", "永安财产保险", "太平财产保险", "亚太财产保险", "美亚财产保险", "东京海上日动火灾保险", "瑞再企商保险", "安达保险", "三井住友海上火灾保险", "三星财产保险", "中银保险", "安联财产保险", "日本财产保险", "利宝保险", "安信农业保险", "中航安盟财产保险", "永诚财产保险", "安华农业保险", "安盛天平财产保险", "阳光财产保险", "阳光农业相互保险公司", "都邦财产保险", "渤海财产保险", "华农财产保险", "苏黎世财产保险", "中国人寿财产保险", "安诚财产保险", "现代财产保险", "长安责任保险", "劳合社保险", "中意财产保险", "爱和谊日生同和财产保险", "国元农业保险", "鼎和财产保险", "中煤财产保险", "国泰财产保险",
                "英大泰和财产保险", "紫金财产保险", "日本兴亚财产保险", "浙商财产保险", "国任财产保险", "乐爱金财产保险", "富邦财产保险", "信利保险", "泰山财产保险", "锦泰财产保险", "众诚汽车保险", "华泰财产保险", "长江财产保险", "诚泰财产保险", "安邦财产保险", "富德财产保险", "鑫安汽车保险", "北部湾财产保险", "众安在线财产保险", "中石油专属财产保险", "华海财产保险", "燕赵财产保险", "恒邦财产保险", "合众财产保险", "中路财产保险", "中原农业保险", "中国铁路财产保险自保", "泰康在线财产保险", "东海航运保险", "安心财产保险", "阳光信用保证保险", "易安财产保险", "久隆财产保险", "新疆前海联合财产保险", "珠峰财产保险", "海峡金桥财产保险", "建信财产保险", "中远海运财产保险自保", "众惠财产相互保险社", "广东粤电财产保险自保", "黄河财产保险", "太平科技保险", "融盛财产保险", "汇友财产相互保险社"]
date_pt = r'签单日期\s{0,}[:|：]\s{0,}(\d{4}[年|,|\-|\\|\/]\d{1,2}[月|,|\-|\\|\/]\d{1,2})'
id_number_18 = r'([1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx])'
id_number_15 = r'([1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3})'
car_number_pt = r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1})'
rmb_pt = r'[￥|¥]\s*[:|：]\s*([0-9,]+\.\d+)\s*元'
engine_number_pt = r'发动机号\W{0,}\s{0,}[:|：]\s{0,}([0-9+a-z+A-Z+]+)'
chassis_number_pt = r'[\S{0,}]+[车架号\W{0,}|\W{0,}识别代码\W{0,}]\W{0,}\s{0,}[:|：]\s{0,}([0-9+a-z+A-Z+]+)'
first_date_pt = r'[\s|初次]+登记日期\s{0,}[:|：]\s{0,}(\d\d\d\d[年|,|\-|\\|\/]\d{1,2}[月|,|\-|\\|\/]\d{1,2})'
expire_date_pt = r'保险期间.*起至\s{0,}(\d{4}\s{0,}[年|,|\-|\\|\/]\s{0,}\d{1,2}\s{0,}[月|,|\-|\\|\/]\s{0,}\d{1,2}\s{0,}日).*'


def read_pdf(file, all_customer):
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
    description = ''
    try:
        with pdfplumber.open(file) as pdf:
            logger.info('开始解析文件:%s' % file)
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
                            date = date_unify(date_matchs[0])
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
                                        date = date_unify(date_matchs[0])
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
                                    elif index+1 < len(valid):
                                        engine_number = valid[index+1]
                            if not chassis_number:
                                if '车架号' in xxx or '识别代码' in xxx:
                                    chassis_number_matchs = re.findall(
                                        chassis_number_pt, xxx)
                                    if chassis_number_matchs:
                                        chassis_number = chassis_number_matchs[0]
                                    elif index+1 < len(valid):
                                        chassis_number = valid[index+1]
                            if not first_date:
                                if '登记日期' in xxx:
                                    first_date_matchs = re.findall(
                                        first_date_pt, xxx)
                                    if first_date_matchs:
                                        first_date = date_unify(
                                            first_date_matchs[0])
                                    elif index+1 < len(valid):
                                        first_date = date_unify(valid[index+1])
                            if not expire_date:
                                if '保险期间' in xxx:
                                    expire_date_matchs = re.findall(
                                        expire_date_pt, xxx)
                                    if expire_date_matchs:
                                        expire_date = date_unify(
                                            expire_date_matchs[0])
                            if not insured_amount:
                                if '人民币大写' in xxx:
                                    insured_amount_matchs = re.findall(
                                        rmb_pt, xxx)
                                    if insured_amount_matchs:
                                        insured_amount = str(insured_amount_matchs[0]).replace(
                                            ',', '')
    except Exception as e:
        description = '解析出现异常:%s' % str(e)
        logger.exception(description)
    match_customer = list(filter(lambda x: x.identity(
        insurant, id_number, plate_number), all_customer))
    customer = Customer()
    if match_customer:
        customer = match_customer[0]
        customer.from_file = '%s,%s' % (customer.from_file, file)
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
        # 解析来源文件，便于检查
        customer.from_file = file
        if customer.not_empty():
            all_customer.append(customer)
    successful = customer.not_empty()
    if not description:
        description = customer.description()
    return (all_customer, successful, description)


def date_unify(strdate: str):
    """
    时间统一
    """
    strdate = strdate.replace(' ', '').replace(' ', '')
    strdate = strdate.replace('年', '-').replace('月', '-').replace('日', '')
    strdate = strdate.replace('/', '-')
    strdate = strdate.replace('\\', '-')
    arr = strdate.split('-')
    if len(arr) == 3:
        year = arr[0]
        mon = arr[1]
        day = arr[2]
        if (not '0' in mon) and int(mon) < 10:
            mon = str('0%s' % mon)
        if (not '0' in mon) and int(day) < 10:
            day = str('0%s' % day)
        strdate = '%s-%s-%s' % (year, mon, day)
    return strdate
