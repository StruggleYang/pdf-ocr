#!/usr/bin/env python
# coding:utf-8
class Customer:
    """
    客户信息
    """
    date = ''  # 本次保险时间
    insurance_company = ''  # 保险公司，渠道
    insurant = ''  # 客户｜被保险人
    id_number = ''  # 证件号()
    plate_number = ''  # 车牌号
    engine_number = ''  # 发动机号码
    chassis_number = ''  # 车架号
    car_models = ''  # 车型(厂牌型号)
    tel = ''  # 电话
    first_date = ''  # 初次登记日期
    expire_date = ''  # 到期日期
    accident_amount = 0  # 意外险金额
    jq_amount = 0  # 交强险
    business_amount = 0  # 商业险
    from_file = ''  # 来源文件
    """
    temp
    """
    insurance_categories = ''
    insured_amount = 0

    def description(self):
        """
        描述此条记录
        """
        des = '没有内容'
        if self.not_empty():
            des = '%s/%s/%s...' % (self.insurant, self.plate_number, self.id_number)

        return des

    def not_empty(self):
        """
        客户信息不是空的
        """
        yes = False
        if self.id_number:
            yes = True
        return yes

    def total_amount(self):
        """
        所有涉及的保险类别金额总计
        """
        return float(self.accident_amount) + float(self.jq_amount) + float(self.business_amount)

    def identity(self, id_number, plate_number):
        """
        判断是否为同一客户
        一些极端情况下，比如商业险是个人购买但为公司车辆，则不适用，因为证件号码可能一个为营业执照的号码，一个为身份证，此时要用车牌号
        """
        return id_number == self.id_number and plate_number == self.plate_number
