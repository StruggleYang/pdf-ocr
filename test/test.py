#!/usr/bin/env python
# coding:utf-8
import pdfplumber
import os
from util.log import logger

if __name__ == '__main__':
    user_path = os.path.expanduser('~')
    with pdfplumber.open(os.path.join(user_path, "working", "pdftest", "test.pdf")) as pdf:
        for page in pdf.pages:
            # 默认解析前5页
            if page.page_number > 5:
                continue
            all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
            all_content = all_content.split("\n")
            tables = page.extract_table()
            # img = page.to_image()
            # img.draw_rects(page.extract_words())
            # img.save('解析page-%s.png' % page.page_number, format="PNG")
            logger.info(page.page_number)
            logger.info(tables)
            logger.info(all_content)
