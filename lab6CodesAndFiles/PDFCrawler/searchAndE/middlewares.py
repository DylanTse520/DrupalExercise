# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class SearchandeSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        receivers = '994084319@qq.com'
        # receivers = 'wuqq@xmu.edu.cn,an.xinying@imicams.ac.cn,994084319@qq.com,fan.shaoping@imicams.ac.cn,shan.lianhui@imicams.ac.cn, 1013265149@qq.com'
        username = '994084319@qq.com'
        password = 'yfilsenwekfqbdgb'
        sender = username
        msg = MIMEMultipart()
        msg['Subject'] = '【无法访问】国家科技管理信息系统公共服务平台异常'
        msg['From'] = sender
        msg['To'] = receivers

        file_comment = 'https://service1.most.gov.cn/'

        puretext = MIMEText(file_comment, 'plain', 'utf-8')
        msg.attach(puretext)

        try:
            client = smtplib.SMTP_SSL('smtp.qq.com')
            client.connect('smtp.qq.com', 465)
            client.login(username, password)
            client.sendmail(sender, receivers.split(","), msg.as_string())
            client.quit()
            print('邮件发送成功！')
        except smtplib.SMTPRecipientsRefused:
            print('Recipient refused')
        except smtplib.SMTPAuthenticationError:
            print('Auth error')
        except smtplib.SMTPSenderRefused:
            print('Sender refused')
        except smtplib.SMTPException:
            print('Error: 无法发送邮件!')

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SearchandeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
