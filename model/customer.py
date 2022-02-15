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
    first_date = ''  # 初次登记日期
    expire_date = ''  # 到期日期
    accident_amount = 0  # 意外险金额
    jq_amount = 0  # 交强险
    business_amount = 0  # 商业险
    from_file = ''  # 来源文件

    def description(self):
        """
        描述此条记录
        """
        des = '没有内容'
        if self.not_empty():
            des = '%s/%s/%s...' % (self.insurant,
                                   self.id_number, self.plate_number)

        return des

    def not_empty(self):
        """
        客户信息不是空的
        """
        yes = False
        if self.insurant and self.id_number and self.plate_number:
            yes = True
        return yes

    def total_amount(self):
        """
        所有涉及的保险类别金额总计
        """
        return float(self.accident_amount)+float(self.jq_amount)+float(self.business_amount)

    def identity(self, insurant, id_number, plate_number):
        """
        判断是否为同一客户
        """
        return insurant == self.insurant and id_number == self.id_number and plate_number == self.plate_number
