import scrapy
import os
import re
# from baidubaike.items import BaidubaikeItem

class FirstfuncSpider(scrapy.Spider):
    name = 'firstfunc'
    allowed_domains = ['baike.baidu.com']
    start_urls = ['https://baike.baidu.com/']

    def parse(self, response):
        all_txt = os.listdir('./txt')
        for txt in all_txt:
            txt = './txt/' + txt
            csv = open(txt.replace('txt', 'CSV'), "w+", encoding='utf-8')
            csv.write('page_id,keyword,annotation,url\n')
            with open(txt, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    if i == 0:
                        continue
                    line = lines[i].split(', ')
                    page_id = str(int(line[0]) + 1)
                    keyword = line[1]
                    yield scrapy.Request("https://baike.baidu.com/search/none?word=%s"%keyword,callback=self.parse_search,meta={'page_id': page_id, 'key': keyword, 'csv': csv},dont_filter=True)
        
    def parse_search(self, response):
        # 获取当前爬取的关键词
        key = response.meta['key']
        page_id = response.meta['page_id']
        csv = response.meta['csv']

        # 获取第一个链接
        url = response.xpath('//a[@class="result-title"]/@href').extract_first()
        if url == None:
            url = 'https://baike.baidu.com/item/' + key
        elif 'baike.baidu' not in url:
            url = 'https://baike.baidu.com/' + url
        yield scrapy.Request(url,callback=self.parse_entry,meta={'page_id': page_id, 'key': key, 'url':url, 'csv': csv},dont_filter=True)


    def parse_entry(self, response):
        # 获取当前爬取的关键词
        page_id = response.meta['page_id']
        key = response.meta['key']
        url = response.meta['url']
        csv = response.meta['csv']

        # 获取annotation_list
        annotation_list = response.xpath('//div[@class="lemma-summary"]/div[@class="para"]//text()').extract()
        annotation = ''
        # 处理获得的annotation_list
        for i in annotation_list:
            annotation = annotation + i.strip()

        csv.write(page_id + ',' + key.strip() + ',' + re.sub(r"\[\d+\]", "", annotation) + ',' + url + '\n')
        # # 将数据存入item
        # item = BaidubaikeItem()
        # item['page_id'] = page_id
        # item['keyname'] = key
        # item['annotation'] = annotation
        # item['url'] = url
        # yield item
        # print(item)

        #输出item：scrapy crawl fistfunc -o  test.csv
    



