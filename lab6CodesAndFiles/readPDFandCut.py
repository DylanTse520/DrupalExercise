# -*- coding: utf-8 -*-
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
import jieba.analyse
import os
import re

all_pdf = [f for f in os.listdir('./pdf') if '.pdf' in f]
for pdf in all_pdf:
    pdf = './pdf/' + pdf
    try:
        with open(pdf.replace('pdf', 'txt'),"w+", encoding='utf-8') as f_result:
            f_result.write('page_number, keyword\n')
            with open(pdf, "rb") as path:
                parser = PDFParser(path)
                document = PDFDocument(parser)
                if not document.is_extractable:
                    raise PDFTextExtractionNotAllowed
                else:
                    resmag = PDFResourceManager()
                    laparams = LAParams()
                    device = PDFPageAggregator(resmag, laparams=laparams)
                    interpreter = PDFPageInterpreter(resmag, device)
                    pages = []
                    for page in PDFPage.create_pages(document):
                        interpreter.process_page(page)
                        layout = device.get_result()
                        text = ""
                        for y in layout:
                            if(isinstance(y, LTTextBoxHorizontal)):
                                text = text + y.get_text()
                        text = re.sub(r'( \| cid \| : \| .* \| )', '', text)
                        pages.append(text)
                    k = int(20 / len(pages)) + 1
                    for i in range(len(pages)):
                        keywords = jieba.analyse.extract_tags(pages[i], topK=k)
                        for keyword in keywords:
                            if not keyword.isnumeric():
                                f_result.write(str(i) + ', ' + keyword + '\n')
    except:
        continue