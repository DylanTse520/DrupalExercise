# -*- coding: utf-8 -*-

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
import jieba
import os

all_pdf = [f for f in os.listdir('./') if 'pdf' in f]
for pdf in all_pdf:
    text = ""
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
            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)
                layout = device.get_result()
                for y in layout:
                    if(isinstance(y, LTTextBoxHorizontal)):
                        text = text + y.get_text()

    seg_list = jieba.cut(text, cut_all=True)

    with open(pdf.replace('pdf', 'txt'),"w+", encoding='utf-8') as f_result:
        f_result.write(" | ".join(seg_list))
