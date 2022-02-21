#!/usr/bin/env python
# coding:utf-8
from threading import Thread
# 异步方法
def async_method(fn):
    """
    异步方法装饰器
    :param fn:
    :return:
    """

    def wrapper(*args, **kwargs):
        # 通过target关键字参数指定线程函数fun
        Thread(target=fn, args=(args,), kwargs=kwargs).start()
        return True

    return wrapper