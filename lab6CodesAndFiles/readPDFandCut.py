# -*- coding: utf-8 -*-

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
import jieba

text = ""

with open(r"“高性能计算”重点专项2018年度项目申报指南16151950vevx.pdf","rb") as path:
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

seg_list = jieba.cut(text, cut_all=False)

with open("“高性能计算”重点专项2018年度项目申报指南16151950vevx.txt","w") as f_result:
    f_result.write(" | ".join(seg_list))
