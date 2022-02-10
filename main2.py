import pdfplumber

with pdfplumber.open("秦绯艳-大地-.pdf") as pdf:
    for page in pdf.pages:
        print('页数', page.page_number)
        print(page.extract_text(x_tolerance=0, y_tolerance=0))
        tables = page.extract_table()
        if tables:
            for item in tables:
                print(item)
