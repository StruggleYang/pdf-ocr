#!/usr/bin/env python
# coding:utf-8
import pandas


def pandas_toexcel(data, file_name):
    """ pandas写execl """
    # 创建DataFrame
    df = pandas.DataFrame(data)
    # 存表，去除原始索引列（0,1,2...）
    df.to_excel(r'%s' % file_name, index=False)
