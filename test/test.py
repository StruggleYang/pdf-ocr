#!/usr/bin/env python
# coding:utf-8
import pdfplumber

if __name__ == '__main__':
    with pdfplumber.open('/Users/struy/working/测试保险单/李来秋驾乘险.pdf') as pdf:
        match_keywords = ["姓名","投保人","投保人名称","身份证","签单日期", "被保险人","车牌号", "发动机号", "车架号", "识别代码", "登记日期", "保险期间","人民币", "人民币大写"]
        for page in pdf.pages:
            # 默认解析前5页
            if page.page_number > 5:
                continue
            all_content = page.extract_text(x_tolerance=0, y_tolerance=0)
            all_content = all_content.split("\n")
            tables = page.extract_table()
            img = page.to_image()
            img.draw_rects(page.extract_words())
            img.save('解析page-%s.png' % page.page_number, format="PNG")
            print(page.page_number)
            #print(tables)
            #print(all_content)
            for item in all_content:
                for key in match_keywords:
                    if key in item :
                        print(item)