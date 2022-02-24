#!/usr/bin/env python
# coding:utf-8
import re
import pdfplumber
from model.customer import Customer
from util.log import logger

company_keys = ["中国人民财产保险", "中国大地财产保险", "中华联合财产保险", "中国太平洋财产保险", "中国平安财产保险", "天安财产保险", "史带财产保险", "华安财产保险", "永安财产保险",
                "太平财产保险", "亚太财产保险", "美亚财产保险", "东京海上日动火灾保险", "瑞再企商保险", "安达保险", "三井住友海上火灾保险", "三星财产保险", "中银保险", "安联财产保险",
                "日本财产保险", "利宝保险", "安信农业保险", "中航安盟财产保险", "永诚财产保险", "安华农业保险", "安盛天平财产保险", "阳光财产保险", "阳光农业相互保险公司",
                "都邦财产保险", "渤海财产保险", "华农财产保险", "苏黎世财产保险", "中国人寿财产保险", "安诚财产保险", "现代财产保险", "长安责任保险", "劳合社保险", "中意财产保险",
                "爱和谊日生同和财产保险", "国元农业保险", "鼎和财产保险", "中煤财产保险", "国泰财产保险",
                "英大泰和财产保险", "紫金财产保险", "日本兴亚财产保险", "浙商财产保险", "国任财产保险", "乐爱金财产保险", "富邦财产保险", "信利保险", "泰山财产保险", "锦泰财产保险",
                "众诚汽车保险", "华泰财产保险", "长江财产保险", "诚泰财产保险", "安邦财产保险", "富德财产保险", "鑫安汽车保险", "北部湾财产保险", "众安在线财产保险",
                "中石油专属财产保险", "华海财产保险", "燕赵财产保险", "恒邦财产保险", "合众财产保险", "中路财产保险", "中原农业保险", "中国铁路财产保险自保", "泰康在线财产保险",
                "东海航运保险", "安心财产保险", "阳光信用保证保险", "易安财产保险", "久隆财产保险", "新疆前海联合财产保险", "珠峰财产保险", "海峡金桥财产保险", "建信财产保险",
                "中远海运财产保险自保", "众惠财产相互保险社", "广东粤电财产保险自保", "黄河财产保险", "太平科技保险", "融盛财产保险", "汇友财产相互保险社"]
match_keywords = {"客户": ["被保险人", "投保人", "投保人名称", "姓名"],
                  "身份证号": ["身份证", "身份证号", "证件号码", "营业执照"],
                  "签单日期": ["签单日期"],
                  "车牌号": ["号码号牌", "号牌号码", "车牌号"],
                  "发动机号": ["发动机号码", "发动机号", "发动机"],
                  "车架号": ["车辆识别代码", "车架号", "识别代码"],
                  "初登日期": ["初次", "首次", "登记日期"],
                  "保险过期": ["保险期间", "起至", "起止"],
                  "保险金额": ["人民币大写", "人民币", "大写"]}
date_pt = r'签单日期\s{0,}[:|：]\s{0,}(\d{4}[年|,|\-|\\|\/]\d{1,2}[月|,|\-|\\|\/]\d{1,2})'
id_number_18_pt = r'([1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx])'  # 身份证18位
id_number_15_pt = r'([1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3})'  # 身份证15位
id_number_business_pt = r'([1-9ANY^IOZSV][1-9A-Z^IOZSV]\d{6}[0-9A-Z^IOZSV]{9}[0-9A-Z^IOZSV])'  # 营业执照，统一社会信用代码
car_number_pt = r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1})'
rmb_pt = r'[￥|¥]\s*[:|：]\s*([0-9,]+\.\d+)\s*元'
engine_number_pt = r'发动机号\W{0,}\s{0,}[:|：]\s{0,}([0-9+a-z+A-Z+]+)'
chassis_number_pt = r'[\S{0,}]+[车架号\W{0,}|\W{0,}识别代码\W{0,}]\W{0,}\s{0,}[:|：]\s{0,}([0-9+a-z+A-Z+]+)'
first_date_pt = r'[\s|初次]+登记日期\s{0,}[:|：]\s{0,}(\d\d\d\d[年|,|\-|\\|\/]\d{1,2}[月|,|\-|\\|\/]\d{1,2})'
expire_date_pt = r'保险期间.*起至\s{0,}(\d{4}\s{0,}[年|,|\-|\\|\/]\s{0,}\d{1,2}\s{0,}[月|,|\-|\\|\/]\s{0,}\d{1,2}\s{0,}日).*'


def get_insurant(keyword, keyword_full, rows, index):
    """
    获得被保险人
    """
    insurant = ''
    if '被保险人' in keyword:
        if not '\n' in keyword_full:
            insurant = keyword_full.replace(
                '被保险人：', '')
            if '被保险人' in insurant:
                if index + 1 < len(rows):
                    insurant = rows[index + 1]
        else:
            names = list(filter(
                lambda x: x != '被\n保\n险\n人' and x != '名 称', rows))
            if names:
                insurant = names[-1]
    return insurant


def get_insurance_company(keyword):
    """
    保险公司
    """
    insurance_company = ''
    for cm in company_keys:
        if cm in keyword:
            insurance_company = cm
    return insurance_company


def get_date(keyword):
    """
    出保单的日期
    """
    date = ''
    if '签单日期' in keyword:
        date_matchs = re.findall(date_pt, keyword)
        if date_matchs:
            date = date_unify(date_matchs[0])
    return date


def get_id_number(keyword):
    """
    获取身份证
    """
    id_number = ''
    id_number_matchs = re.findall(
        id_number_18_pt, keyword)
    if not id_number_matchs:
        id_number_matchs = re.findall(
            id_number_15_pt, keyword)
    if not id_number_matchs:
        id_number_matchs = re.findall(
            id_number_business_pt, keyword)
    if id_number_matchs:
        if isinstance(id_number_matchs[0], str):
            id_number = id_number_matchs[0]
        else:
            id_number = id_number_matchs[0][0]
    return id_number


def get_plate_number(keyword):
    """
    获取车牌号
    """
    plate_number = ''
    plate_number_matchs = re.findall(
        car_number_pt, keyword)
    if plate_number_matchs:
        plate_number = plate_number_matchs[0]
    return plate_number


def get_engine_number(keyword, rows, index):
    """
    发动机号
    """
    engine_number = ''
    if '发动机号' in keyword:
        engine_number_matchs = re.findall(
            engine_number_pt, keyword)
        if engine_number_matchs:
            engine_number = engine_number_matchs[0]
        elif index + 1 < len(rows):
            engine_number = rows[index + 1]
    return engine_number


def get_chassis_number(keyword, rows, index):
    """
    车架号
    """
    chassis_number = ''
    if '车架号' in keyword or '识别代码' in keyword:
        chassis_number_matchs = re.findall(
            chassis_number_pt, keyword)
        if chassis_number_matchs:
            chassis_number = chassis_number_matchs[0]
        elif index + 1 < len(rows):
            chassis_number = rows[index + 1]
    return chassis_number


def get_first_date(keyword, rows, index):
    """
    初次登记日期
    """
    first_date = None
    if '登记日期' in keyword:
        first_date_matchs = re.findall(
            first_date_pt, keyword)
        if first_date_matchs:
            first_date = date_unify(
                first_date_matchs[0])
        elif index + 1 < len(rows):
            first_date = date_unify(rows[index + 1])
    return first_date


def get_expire_date(keyword):
    """
    到期日期
    """
    expire_date = None
    if '保险期间' in keyword:
        expire_date_matchs = re.findall(
            expire_date_pt, keyword)
        if expire_date_matchs:
            expire_date = date_unify(
                expire_date_matchs[0])
    return expire_date


def get_insured_amount(keyword):
    """
    保险金额
    """
    insured_amount = 0
    if '人民币大写' in keyword:
        insured_amount_matchs = re.findall(
            rmb_pt, keyword)
        if insured_amount_matchs:
            insured_amount = str(insured_amount_matchs[0]).replace(
                ',', '')
    return insured_amount


def read_pdf(file, all_customer):
    temp_customer = Customer()
    temp_customer.insurance_categories = ''
    temp_customer.insured_amount = 0
    temp_customer.plate_number = ''
    temp_customer.engine_number = ''
    temp_customer.chassis_number = ''
    temp_customer.first_date = ''
    temp_customer.expire_date = ''
    temp_customer.id_number = ''
    temp_customer.date = ''
    temp_customer.insurant = ''
    temp_customer.insurance_company = ''
    description = ''
    try:
        def file_extract(valid):
            for index in range(len(valid)):
                strs = valid[index]
                xxx = strs.replace('\n', '')
                if not temp_customer.insurant:
                    temp_customer.insurant = get_insurant(xxx, strs, valid, index)
                if not temp_customer.insurance_company:
                    temp_customer.insurance_company = get_insurance_company(strs)
                if not temp_customer.date:
                    temp_customer.date = get_date(strs)
                if not temp_customer.id_number:
                    temp_customer.id_number = get_id_number(strs)
                if not temp_customer.plate_number:
                    temp_customer.plate_number = get_plate_number(strs)
                if not temp_customer.engine_number:
                    temp_customer.engine_number = get_engine_number(strs, valid, index)
                if not temp_customer.chassis_number:
                    temp_customer.chassis_number = get_chassis_number(strs, valid, index)
                if not temp_customer.first_date:
                    temp_customer.first_date = get_first_date(strs, valid, index)
                if not temp_customer.expire_date:
                    temp_customer.expire_date = get_expire_date(strs)
                if not temp_customer.insured_amount:
                    temp_customer.insured_amount = get_insured_amount(strs)

        with pdfplumber.open(file) as pdf:
            logger.info('开始解析文件:%s' % file)
            for page in pdf.pages:
                # 默认解析前5页
                if page.page_number > 5:
                    continue
                all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
                if not temp_customer.insurance_categories:
                    if '强制保险' in all_content:
                        temp_customer.insurance_categories = '交强'
                    elif '人身意外伤害' in all_content:
                        temp_customer.insurance_categories = '意外'
                    else:
                        temp_customer.insurance_categories = '商业'
                if not temp_customer.date:
                    if '签单日期' in all_content:
                        date_matchs = re.findall(date_pt, all_content)
                        if date_matchs:
                            temp_customer.date = date_unify(date_matchs[0])
                tables = page.extract_table()
                if tables:
                    for item in tables:
                        valid = list(filter(lambda x: x != None, item))
                        file_extract(valid)
                # 如果没有办法读取到表格或这数据不是常见的表格形式
                # 且信息没有获取到，需要从完整文本中获取
                if not temp_customer.insurant and not temp_customer.id_number and not temp_customer.plate_number:
                    all_content_arr = all_content.split("\n")
                    all_match_keywords = []
                    for field, keywords in match_keywords.items():
                        all_match_keywords.extend(keywords)
                    match_rows = list(filter(lambda x: any(map(lambda y: y in x, all_match_keywords)), all_content_arr))
                    for item in match_rows:
                        # if '：' in item:
                        #     valid = item.split("：")
                        # elif ':' in item:
                        #     valid = item.split(":")
                        # else:
                        valid = [item]
                        file_extract(valid)
    except Exception as e:
        description = '解析出现异常:%s' % str(e)
        logger.exception(description)
    match_customer = list(
        filter(lambda x: x.identity(temp_customer.id_number, temp_customer.plate_number), all_customer))
    customer = Customer()
    # print(temp_customer.insurant, temp_customer.id_number, temp_customer.plate_number)
    if match_customer:
        customer = match_customer[0]
        customer.from_file = '%s,%s' % (customer.from_file, file)
    # 保险类别区分
    if temp_customer.insurance_categories == '交强':
        customer.jq_amount = temp_customer.insured_amount
    elif temp_customer.insurance_categories == '意外':
        customer.accident_amount = temp_customer.insured_amount
    else:
        customer.business_amount = temp_customer.insured_amount
    if not customer.date:
        customer.date = temp_customer.date
    if not customer.insurance_company:
        customer.insurance_company = temp_customer.insurance_company
    if not customer.engine_number:
        customer.engine_number = temp_customer.engine_number
    if not customer.chassis_number:
        customer.chassis_number = temp_customer.chassis_number
    if not customer.first_date:
        customer.first_date = temp_customer.first_date
    if not customer.expire_date:
        customer.expire_date = temp_customer.expire_date
    if not customer.not_empty():
        customer.insurant = temp_customer.insurant
        customer.id_number = temp_customer.id_number
        customer.plate_number = temp_customer.plate_number
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
    strdate = strdate.replace('年', '.').replace('月', '.').replace('日', '')
    strdate = strdate.replace('/', '.')
    strdate = strdate.replace('-', '.')
    strdate = strdate.replace('\\', '.')
    arr = strdate.split('.')
    if len(arr) == 3:
        year = arr[0]
        mon = arr[1]
        day = arr[2]
        if (not '0' in mon) and int(mon) < 10:
            mon = str('0%s' % mon)
        if (not '0' in mon) and int(day) < 10:
            day = str('0%s' % day)
        strdate = '%s.%s.%s' % (year, mon, day)
    return strdate
