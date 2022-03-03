#!/usr/bin/env python
# coding:utf-8
import time
import pdfplumber
import os
# from util.log import logger

if __name__ == '__main__':
    print("hello")
    user_path = os.path.expanduser('~')
    print(user_path)
    with pdfplumber.open(os.path.join(user_path, "working", "pdftest", "test.pdf")) as pdf:
        for page in pdf.pages:
            all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
            tables = page.extract_table()
            print(page.page_number)
            print(tables)
            print(all_content)
    print("end")
    time.sleep(10)
