# -*- coding: utf-8 -*-
import scrapy
import urllib
import datetime
from pathlib import Path

class MySpider(scrapy.Spider):
    name = 'monAnn'
    allowed_domains = ['service1.most.gov.cn','service.most.gov.cn']
    start_urls = ['https://service1.most.gov.cn/sousuo/s.html?year=&channel=%E7%A7%91%E6%8A%80%E8%AE%A1%E5%88%92%E5%B9%B4%E5%BA%A6%E6%8A%A5%E5%91%8A&pager.pageNumber=1']
	
    def parse(self, response):
        # 检查该域名是否有项目
        totalCount = response.xpath('//div[@class="commonDispagePanel"]/input[@name="pager.totalCount"]/@value').get()
        if totalCount != None:
            # 获取页面内项目链接
            urls = response.xpath('//body//div[@class="seach_list"]/dl/dt/a/@href').extract() 
            # 下载链接内 pdf
            for i in range(len(urls)):
                yield scrapy.Request(urls[i], callback=self.parse_url_item)

        # 查看当前页面数
        pageNumber = int(response.xpath('//div[@class="commonDispagePanel"]/input[@name="pager.pageNumber"]/@value').get())
        # 查看总页数
        pageCount = int(response.xpath('//div[@class="commonDispagePanel"]/input[@name="pager.pageCount"]/@value').get())
        # 爬取下一页
        if pageNumber < pageCount + 1 :
            yield scrapy.Request("https://service1.most.gov.cn/sousuo/s.html?year=&channel=%E7%A7%91%E6%8A%80%E8%AE%A1%E5%88%92%E5%B9%B4%E5%BA%A6%E6%8A%A5%E5%91%8A&pager.pageNumber=" + str(pageNumber + 1), callback=self.parse)

    # 下载页面内 pdf
    def parse_url_item(self, response):
        # 获取项目标题
        title = response.xpath('//div[@class="t18"]/text()').get()
        # 获取附件地址
        url = response.xpath("//a/@href").extract()
        # 筛选 pdf
        url = [item for item in url if 'pdf' in item]

        for i in range(len(url)):
            # 下载地址补足 http 前缀
            if "http" not in url[i]:
                url[i] = "https://service.most.gov.cn/" + url[i]    
            # 获取 pdf 原名字
            name = url[i].split('/')[-1]
            urllib.request.urlretrieve(url[i], filename=".//file/%s" % title + name)

    
    
    