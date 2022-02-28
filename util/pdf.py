#!/usr/bin/env python
# coding:utf-8
import re
import pdfplumber
from model.customer import Customer
from util.log import logger

company_keys = ["中国人民财产保险", "中国大地财产保险", "中华联合财产保险", "太平洋财产保险", "中国平安财产保险", "天安财产保险", "史带财产保险", "华安财产保险", "永安财产保险",
                "太平财产保险", "亚太财产保险", "美亚财产保险", "东京海上日动火灾保险", "瑞再企商保险", "安达保险", "三井住友海上火灾保险", "三星财产保险", "中银保险", "安联财产保险",
                "日本财产保险", "利宝保险", "安信农业保险", "中航安盟财产保险", "永诚财产保险", "安华农业保险", "安盛天平", "阳光财产保险", "阳光农业相互保险公司",
                "都邦财产保险", "渤海财产保险", "华农财产保险", "苏黎世财产保险", "中国人寿财产保险", "安诚财产保险", "现代财产保险", "长安责任保险", "劳合社保险", "中意财产保险",
                "爱和谊日生同和财产保险", "国元农业保险", "鼎和财产保险", "中煤财产保险", "国泰财产保险",
                "英大泰和财产保险", "紫金财产保险", "日本兴亚财产保险", "浙商财产保险", "国任财产保险", "乐爱金财产保险", "富邦财产保险", "信利保险", "泰山财产保险", "锦泰",
                "众诚汽车保险", "华泰财产保险", "长江财产保险", "诚泰", "安邦财产保险", "富德财产保险", "鑫安汽车保险", "北部湾财产保险", "众安在线财产保险",
                "中石油专属财产保险", "华海财产保险", "燕赵财产保险", "恒邦财产保险", "合众财产保险", "中路财产保险", "中原农业保险", "中国铁路财产保险自保", "泰康在线财产保险",
                "东海航运保险", "安心财产保险", "阳光信用保证保险", "易安财产保险", "久隆财产保险", "新疆前海联合财产保险", "珠峰财产保险", "海峡金桥财产保险", "建信财产保险",
                "中远海运财产保险自保", "众惠财产相互保险社", "广东粤电财产保险自保", "黄河财产保险", "太平科技保险", "融盛财产保险", "汇友财产相互保险社"]
match_keywords = {"客户": ["行驶证车主", "被保险人", "投保人名称", "投保人", "姓名"],
                  "身份证号": ["身份证号", "证件号码", "身份证", "营业执照"],
                  "签单日期": ["签单日期"],
                  "车牌号": ["号码号牌", "号牌号码", "车牌号", "车牌"],
                  "发动机号": ["发动机号码", "发动机号", "发动机"],
                  "车架号": ["车辆识别代码", "车架号", "识别代码"],
                  "车型": ["厂牌型号", "车型"],
                  "初登日期": ["初次", "首次", "登记日期"],
                  "保险过期": ["保险期间", "起至", "起止"],
                  "保险金额": ["人民币大写", "保险费合计", "人民币", "大写", "CNY", "￥", "¥"],
                  "电话": ["被保险人电话", "联系电话"]}
date_pt = r'签单日期\s{0,}[:|：]\s{0,}(\d{4}[年|,|\-|\\|\/]\d{1,2}[月|,|\-|\\|\/]\d{1,2})'
id_number_18_pt = r'([1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx])'  # 身份证18位
id_number_15_pt = r'([1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3})'  # 身份证15位
id_number_business_pt = r'([1-9ANY^IOZSV][1-9A-Z^IOZSV]\d{6}[0-9A-Z^IOZSV]{9}[0-9A-Z^IOZSV])'  # 营业执照，统一社会信用代码
car_number_pt = r'([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1})'
rmb_pt = r"[￥|¥]\s*[\u00a0]{0,}[:|：]\s*[\u00a0]{0,}[RMB]{0,}([0-9,\.\s[\u00a0]]*)\s*元"
rmb_pt_old = r'[￥|¥]?\s*[:|：]\s*[￥|¥]?[RMB]{0,}[CNY]{0,}\s*([0-9,\.]*)\s*元'
cny_pt = r'CNY\s*([0-9,\.]*)'
engine_number_pt = r'发动机号\W{0,}\s{0,}[:|：]\s{0,}([0-9+a-z+A-Z+]+)'
chassis_number_pt = r'[\S{0,}]+[车架号\W{0,}|\W{0,}识别代码\W{0,}]\W{0,}\s{0,}[:|：]\s{0,}([0-9+a-z+A-Z+]+)'
first_date_pt = r'[\s|初次]+登记日期\s{0,}[:|：]\s{0,}(\d\d\d\d[年|,|\-|\\|\/]\d{1,2}[月|,|\-|\\|\/]\d{1,2})'
expire_date_pt = r'保险期间.*起至\s{0,}(\d{4}\s{0,}[年|,|\-|\\|\/]\s{0,}\d{1,2}\s{0,}[月|,|\-|\\|\/]\s{0,}\d{1,2}\s{0,}日).*'


def get_insurant(keyword, keyword_full, rows, index):
    """
    获得被保险人
    """
    insurant = ''
    if '被保险' in keyword:
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
    if len(insurant) > 5 and '\n' in insurant:
        logger.error("识别到保险人信息过长%s" % insurant)
        insurant = ""
    if not insurant:
        for mkey in match_keywords['客户']:
            if mkey in keyword_full:
                for spl in [":", "："]:
                    if spl in keyword_full:
                        logger.info("识别到被保险人,关键字[%s]::%s" % (mkey, keyword_full))
                        insurant = keyword_full.split(spl)[1].replace(" ", "")
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
        logger.info("识别到签单日期::%s" % keyword)
        date_matchs = re.findall(date_pt, keyword)
        if date_matchs:
            date = date_unify(date_matchs[0])
    return date


def get_id_number(keyword):
    """
    获取身份证
    """

    def match_id_number(kw):
        inner_id_number = ""
        id_number_matchs = re.findall(
            id_number_18_pt, kw)
        if not id_number_matchs:
            id_number_matchs = re.findall(
                id_number_15_pt, kw)
        if not id_number_matchs:
            id_number_matchs = re.findall(
                id_number_business_pt, kw)
        if id_number_matchs:
            if isinstance(id_number_matchs[0], str):
                inner_id_number = id_number_matchs[0]
            else:
                inner_id_number = id_number_matchs[0][0]
        return inner_id_number

    id_number = match_id_number(keyword)
    if not id_number:
        for mkey in match_keywords['身份证号']:
            if mkey in keyword:
                id_number = match_id_number(keyword)
    return id_number


def get_plate_number(keyword):
    """
    获取车牌号
    """
    keyword = keyword.replace(" ", "")
    plate_number = ''
    # 单号的规则可能会影响到车牌识别
    if '单号' in keyword:
        return plate_number
    # ===========非单元格内容匹配============
    for mkey in match_keywords['车牌号']:
        if mkey in keyword:
            plate_number_matchs = re.findall(
                car_number_pt, keyword)
            if plate_number_matchs:
                plate_number = plate_number_matchs[0]
    # ===========单元格内容匹配============
    if not plate_number:
        plate_number_matchs = re.findall(
            car_number_pt, keyword)
        if plate_number_matchs:
            if len(keyword) == 7:  # 车牌为7位，这样表格匹配几率更大
                plate_number = plate_number_matchs[0]
    return plate_number


def get_engine_number(keyword, rows, index):
    """
    发动机号
    """
    engine_number = ''
    if '发动机号' in keyword:
        logger.info("识别到发动机号::%s" % keyword)
        engine_number_matchs = re.findall(
            engine_number_pt, keyword)
        if engine_number_matchs:
            engine_number = engine_number_matchs[0]
        elif index + 1 < len(rows):
            engine_number = remove_newline(rows[index + 1])
    return engine_number


def get_chassis_number(keyword, rows, index):
    """
    车架号
    """
    chassis_number = ''
    if '车架号' in keyword or '识别代码' in keyword:
        logger.info("识别到车架号::%s" % keyword)
        chassis_number_matchs = re.findall(
            chassis_number_pt, keyword)
        if chassis_number_matchs:
            chassis_number = chassis_number_matchs[0]
        elif index + 1 < len(rows):
            chassis_number = remove_newline(rows[index + 1])
    return chassis_number


def get_car_models(keyword, rows, index):
    """
    车型，厂牌型号
    """
    car_models = ''
    for ckey in match_keywords["车型"]:
        if ckey in remove_blank(keyword):
            for spl in [":", "："]:
                if spl in keyword:
                    logger.info("识别到车型,关键字[%s]::%s" % (ckey, keyword))
                    car_models = keyword.split(spl)[1].strip().split(" ")[0]
            if not car_models:
                if index + 1 < len(rows):
                    car_models = remove_newline(rows[index + 1])
    return car_models


def get_tel(keyword, rows, index):
    """
    联系电话
    """
    tel = ''
    for ckey in match_keywords["电话"]:
        if ckey in remove_blank(keyword):
            for spl in [":", "："]:
                if spl in keyword:
                    logger.info("识别到电话,关键字[%s]::%s" % (ckey, keyword))
                    tel = keyword.split(spl)[1].strip().split(" ")[0]
            if not tel:
                if index + 1 < len(rows):
                    tel = remove_newline(rows[index + 1])
    if '****' not in tel:
        tel = ''
    return tel


def get_first_date(keyword, rows, index):
    """
    初次登记日期
    """
    first_date = None
    if '登记日期' in keyword:
        logger.info("识别到登记日期::%s" % keyword)
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
        logger.info("识别到保险期间(到期时间)::%s" % keyword)
        expire_date_matchs = re.findall(
            expire_date_pt, keyword)
        if expire_date_matchs:
            expire_date = date_unify(
                expire_date_matchs[0])
    return expire_date


def get_insured_amount(keyword, insurance_categories):
    """
    保险金额 
    TODO 这里用人民币大写转为数字可能更加准确。。。。
    """
    insured_amount = 0
    for mkey in match_keywords['保险金额']:
        if mkey in keyword:
            logger.info("识别到人民币，关键字%s::%s" % (mkey, keyword))
            insured_amount_matchs = re.findall(
                rmb_pt_old, money_unify(keyword))
            if insured_amount_matchs:
                insured_amount = money_unify(str(insured_amount_matchs[0]))
    if insured_amount == 0:
        if 'CNY' in keyword:
            logger.info("识别到人民币标准货币符号CNY::%s" % keyword)
            insured_amount_matchs = re.findall(
                cny_pt, money_unify(keyword))
            if insured_amount_matchs:
                insured_amount = money_unify(str(insured_amount_matchs[0]))
    # 调研了历史数据，意外险都是几百块，主要应对没有办法区别保险方案额度的情况
    if insurance_categories == '意外' and float(insured_amount) > 8000:
        insured_amount = 0
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
                if not temp_customer.car_models:
                    temp_customer.car_models = get_car_models(strs, valid, index)
                if not temp_customer.first_date:
                    temp_customer.first_date = get_first_date(strs, valid, index)
                if not temp_customer.expire_date:
                    temp_customer.expire_date = get_expire_date(strs)
                if not temp_customer.insured_amount:
                    temp_customer.insured_amount = get_insured_amount(strs, temp_customer.insurance_categories)
                if not temp_customer.tel:
                    temp_customer.tel = get_tel(strs, valid, index)

        with pdfplumber.open(file) as pdf:
            logger.info('开始解析文件:%s' % file)
            page_content_cache = []
            for page in pdf.pages:
                # 默认解析前5页
                if page.page_number > 5:
                    break
                all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
                # 加入到缓存，做加强处理
                page_content_cache.append(all_content)  # 这可能有问题
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
                        valid = list(filter(lambda x: x is not None, item))
                        file_extract(valid)
            # 如果没有办法读取到表格或这数据不是常见的表格形式
            # 且信息没有获取到，需要从完整文本中获取
            if not temp_customer.insurant and not temp_customer.id_number and not temp_customer.plate_number:
                for cache_content in page_content_cache:
                    all_content_arr = cache_content.split("\n")
                    all_match_keywords = []
                    for field, keywords in match_keywords.items():
                        all_match_keywords.extend(keywords)
                    match_rows = list(filter(lambda x: any(map(lambda y: y in x, all_match_keywords)), all_content_arr))
                    for item in match_rows:
                        valid = [item]
                        file_extract(valid)
    except Exception as e:
        description = '解析出现异常:%s' % str(e)
        logger.exception(description)
    # 先严格匹配
    match_customer = list(
        filter(lambda x: x.identity(temp_customer.id_number, temp_customer.plate_number), all_customer))
    # 宽松匹配，车牌号，但是也比较精确。主要应多部分信息不一致的情况
    if not match_customer:
        match_customer = list(
            filter(lambda x: x.plate_number == temp_customer.plate_number, all_customer))
    customer = Customer()
    # print(temp_customer.insurant, temp_customer.id_number, temp_customer.plate_number)
    if match_customer:
        customer = match_customer[0]
        # 公司名义，则以公司为准
        if '公司' not in customer.insurant and '公司' in temp_customer.insurant:
            customer.insurant = temp_customer.insurant
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
    if not customer.car_models:
        customer.car_models = temp_customer.car_models
    if not customer.first_date:
        customer.first_date = temp_customer.first_date
    if not customer.expire_date:
        customer.expire_date = temp_customer.expire_date
    if not customer.tel:
        customer.tel = temp_customer.tel
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


def all_char_in_content(match_key, keyword):
    """
    关键字的所有字符都在内容中存在，用于匹配字段中间空格的情况
    """
    char_arr = []
    for ckey_char in match_key:
        char_arr.append(ckey_char)
    return all(list(map(lambda x: x in keyword, char_arr)))


def remove_blank(keyword: str):
    """
    去除空白
    """
    return keyword.replace('\u00a0', '').replace(" ", "")


def remove_newline(keyword: str):
    """
    去除 换行
    """
    return keyword.replace('\n', '')


def money_unify(money: str):
    """
    金额统一
    \u00a0 = NBSP 空格
    """
    return remove_blank(money.replace(",", ""))


def date_unify(strdate: str):
    """
    时间统一
    """
    strdate = remove_blank(strdate)
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
