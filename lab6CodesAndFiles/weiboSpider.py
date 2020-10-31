# -*- coding: utf-8 -*-
import time
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import xlwt
import jieba.analyse
import os

# 先调用无界面浏览器PhantomJS或Firefox
# driver = webdriver.PhantomJS()
# driver = webdriver.Firefox()
# 下载chrome：https://www.google.cn/intl/zh-CN/chrome/
# 要使用Chrome浏览器，必须得有chromedriver
# 并且需要设置环境变量PATH
# 参考：https://www.cnblogs.com/lfri/p/10542797.html
# 如80.0.3987.132版本的chrome对应下载80.0.3987.16即可
driver = webdriver.Chrome()


# ********************************************************************************
#                            第一步: 登陆login.sina.com
#                     这是一种很好的登陆方式，有可能有输入验证码
#                          登陆之后即可以登陆方式打开网页
# ********************************************************************************

def LoginWeibo(username, password):
    try:
        # 输入用户名/密码登录
        print('准备登陆Weibo.cn网站...')
        driver.get("http://login.sina.com.cn/")
        elem_user = driver.find_element_by_name("username")
        elem_user.send_keys(username)  # 用户名
        elem_pwd = driver.find_element_by_name("password")
        elem_pwd.send_keys(password)  # 密码
        elem_sub = driver.find_element_by_xpath("//input[@class='W_btn_a btn_34px']")
        elem_sub.click()  # 点击登陆 因无name属性

        try:
            # 输入验证码
            time.sleep(10)
            elem_sub.click()
        except:
            # 不用输入验证码
            pass

        # 获取Coockie 推荐资料：http://www.cnblogs.com/fnng/p/3269450.html
        print('Crawl in ', driver.current_url)
        print('输出Cookie键值对信息:')
        for cookie in driver.get_cookies():
            print(cookie)
            for key in cookie:
                print(key, cookie[key])
        print('登陆成功...')
    except Exception as e:
        print("Error: ", e)
    finally:
        print('End LoginWeibo!\n')


# ********************************************************************************
#                  第二步: 访问http://s.weibo.com/页面搜索结果
#               输入关键词、时间范围，得到所有微博信息、博主信息等
#                     考虑没有搜索结果、翻页效果的情况
# ********************************************************************************

def GetSearchContent(key):
    driver.get("http://s.weibo.com/")
    print('搜索热点主题：')

    # 输入关键词并点击搜索
    item_inp = driver.find_element_by_xpath("//input[@type='text']")
    item_inp.send_keys(key)
    item_inp.send_keys(Keys.RETURN)  # 采用点击回车直接搜索

    time.sleep(5)

    handlePage(key)  # 处理当前页面内容



# time.sleep(1)

# ********************************************************************************
#                  辅助函数，考虑页面加载完成后得到页面所需要的内容
# ********************************************************************************

# 页面加载完成后，对页面内容进行处理
def handlePage(key):
    # while True:
        # 之前认为可能需要sleep等待页面加载，后来发现程序执行会等待页面加载完毕
        # sleep的原因是对付微博的反爬虫机制，抓取太快可能会判定为机器人，需要输入验证码
    time.sleep(1)
    # 先行判定是否有内容
    if checkContent():
        print("getContent")
        getContent(key)
        # 先行判定是否有下一页按钮
        # if checkNext():
        #     # 拿到下一页按钮
        #     next_page_btn = driver.find_element_by_css_selector("#pl_feedlist_index > div.m-page > div > a.next")
        #     next_page_btn.click()
        # else:
        #     print("no Next")
        #     break
    else:
        print("no Content")
        # break


# 判断页面加载完成后是否有内容
def checkContent():
    # 有内容的前提是有“导航条”？错！只有一页内容的也没有导航条
    # 但没有内容的前提是有“pl_noresult”
    try:
        driver.find_element_by_xpath("//div[@class='card card-no-result s-pt20b40']")
        flag = False
    except:
        flag = True
    return flag


# 判断是否有下一页按钮
def checkNext():
    try:
        driver.find_element_by_css_selector("#pl_feedlist_index > div.m-page > div > a.next")
        flag = True
    except:
        flag = False
    return flag


# 判断是否有展开全文按钮
def checkqw():
    try:
        driver.find_element_by_xpath(".//div[@class='content']/p[@class='txt']/a")
        flag = True
    except:
        flag = False
    return flag


# 在添加每一个sheet之后，初始化字段
def initCSV():
    name = ['关键词', '微博内容', '微博地址']

    global file_name

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(','.join(name) + '\n')


# 将dic中的内容写入excel
def writeXLS(dic):
    global file_name

    with open(file_name, 'a', encoding='utf-8') as f:
        for i in range(len(dic)):
            f.write(','.join(dic[i]) + '\n')


# 在页面有内容的前提下，获取内容
def getContent(key):
    # 寻找到每一条微博的class
    try:
        # nodes = driver.find_elements_by_xpath("//div[@class='WB_cardwrap S_bg2 clearfix']")
        # nodes = driver.find_elements_by_xpath("//div[@class='card-wrap']")
        nodes = driver.find_elements_by_xpath("//div[@class='card-wrap']/div[@class='card']")
    except Exception as e:
        print(e)

    # 在运行过程中微博数==0的情况，可能是微博反爬机制，需要输入验证码
    if len(nodes) == 0:
        input("请在微博页面输入验证码！")
        url = driver.current_url
        driver.get(url)
        getContent(key)
        return

    dic = {}

    # global page
    # print(start_stamp.strftime("%Y-%m-%d-%H"))
    # print('页数:', page)
    # page = page + 1
    print('微博数量', len(nodes))

    for i in range(len(nodes)):
        dic[i] = []
        dic[i].append(str(key))
        try:
            # BZNC = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='W_texta W_fb']").text
            BZNC = nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='txt']").get_attribute("nick-name")
            # print(nodes[2].find_element_by_xpath(".//div[@class='content']/p[@class='txt']").get_attribute("nick-name"))
        except:
            BZNC = ''
        # print('博主昵称:', BZNC)
        # dic[i].append(BZNC)

        try:
            BZZY = nodes[i].find_element_by_xpath(".//div[@class='content']/div[@class='info']/div[2]/a").get_attribute("href")
            # print(nodes[1].find_element_by_xpath("//*[@id="pl_feedlist_index"]/div[2]/div[1]/div/div[1]/div[1]/a").get_attribute("href"))
            # print(nodes[1].find_element_by_css_selector("#pl_feedlist_index > div:nth-child(2) > div:nth-child(1) > div > div.card-feed > div.avator > a").get_attribute("href"))
        except:
            BZZY = ''
        # print('博主主页:', BZZY)
        # dic[i].append(BZZY)
        # 微博官方认证，没有爬取
        try:
            # WBRZ = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='approve_co']").get_attribute('title')#若没有认证则不存在节点
            WBRZ = nodes[i].find_element_by_xpath(".//div[@class='info']/div/a[contains(@title,'微博')]").get_attribute('title') # 若没有认证则不存在节点
        except:
            WBRZ = ''
        # print('微博认证:', WBRZ)
        # dic[i].append(WBRZ)

        try:
            # WBDR = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='ico_club']").get_attribute('title')#若非达人则不存在节点
            WBDR = nodes[i].find_element_by_xpath(".//div[@class='feed_content wbcon']/a[@class='ico_club']").get_attribute('title')  # 若非达人则不存在节点
        except:
            WBDR = ''
        # print('微博达人:', WBDR)
        # dic[i].append(WBDR)

        # 判断展开全文和网页链接是否存在
        try:
            nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='txt']/a[@action-type='fl_unfold']").is_displayed()
            flag = True
        except:
            flag = False
        # 获取微博内容
        try:
            if flag:
                nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='txt']/a[@action-type='fl_unfold']").click()
                time.sleep(1)
                WBNR = nodes[i].find_element_by_xpath(".//div[@class='content']/p[2]").text.replace("\n","")
                # 判断发布位置是否存在
                try:
                    nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='txt']/a/i[@class='wbicon']").is_displayed()
                    flag = True
                except:
                    flag = False
                # 获取微博发布位置
                try:
                    if flag:
                        pattern = nodes[i].find_elements_by_xpath(".//div[@class='content']/p[2]/a[i[@class='wbicon']]")
                        if isinstance(pattern,list):
                            text = [p.text for p in pattern]
                            FBWZ = [loc for loc in [re.findall('^2(.*$)', t) for t in text] if len(loc) > 0][0][0]
                        else:
                            text = pattern.text
                            FBWZ = re.findall('^2(.*$)',text)[0]
                    else:
                        FBWZ = ''
                except:
                    FBWZ = ''
            else:
                WBNR = nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='txt']").text.replace("\n","")
                # 判断发布位置是否存在
                try:
                    nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='txt']/a/i[@class='wbicon']").is_displayed()
                    flag = True
                except:
                    flag = False
                # 获取微博发布位置
                try:
                    if flag:
                        pattern = nodes[i].find_elements_by_xpath(".//div[@class='content']/p[@class='txt']/a[i[@class='wbicon']]")
                        if isinstance(pattern,list):
                            text = [p.text for p in pattern]
                            FBWZ = [loc for loc in [re.findall('^2(.*$)', t) for t in text] if len(loc) > 0][0][0]
                        else:
                            text = pattern.text
                            FBWZ = re.findall('^2(.*$)',text)[0]
                    else:
                        FBWZ = ''
                except:
                    FBWZ = ''
        except:
            WBNR = ''
        # print('微博内容:', WBNR)
        dic[i].append(WBNR)

        # print('发布位置:', FBWZ)
        # dic[i].append(FBWZ)

        try:
            # FBSJ = nodes[i].find_element_by_xpath(".//div[@class='feed_from W_textb']/a[@class='W_textb']").text
            FBSJ = nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='from']/a[1]").text
        except:
            FBSJ = ''
        # print('发布时间:', FBSJ)
        # dic[i].append(FBSJ)

        try:
            # WBDZ = nodes[i].find_element_by_xpath(".//div[@class='feed_from W_textb']/a[@class='W_textb']").get_attribute("href")
            WBDZ = nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='from']/a[1]").get_attribute("href")
        except:
            WBDZ = ''
        # print('微博地址:', WBDZ)
        dic[i].append(WBDZ)

        try:
            WBLY = nodes[i].find_element_by_xpath(".//div[@class='content']/p[@class='from']/a[2]").text
        except:
            WBLY = ''
        # print('微博来源:', WBLY)
        # dic[i].append(WBLY)

        try:
            ZF_TEXT = nodes[i].find_element_by_xpath(".//a[@action-type='feed_list_forward']").text
            #            ZF_TEXT = nodes[10].find_element_by_xpath(".//a[@action-type='feed_list_forward']").text
            #            ZF_TEXT.split(' ')[1]
            if ZF_TEXT == '转发':
                ZF = 0
            else:
                ZF = int(ZF_TEXT.split(' ')[1])
        except:
            ZF = 0
        # print('转发:', ZF)
        # dic[i].append(ZF)

        try:
            # PL_TEXT = nodes[i].find_element_by_xpath(".//a[@action-type='feed_list_comment']//em").text#可能没有em元素
            PL_TEXT = nodes[i].find_element_by_xpath(".//a[@action-type='feed_list_comment']").text  # 可能没有em元素
            # nodes[10].find_element_by_xpath(".//a[@action-type='feed_list_comment']").text
            if PL_TEXT == '评论':
                PL = 0
            else:
                PL = int(PL_TEXT.split(' ')[1])
        except:
            PL = 0
        # print('评论:', PL)
        # dic[i].append(PL)

        try:
            ZAN_TEXT = nodes[i].find_element_by_xpath(".//a[@action-type='feed_list_like']//em").text  # 可为空
            # ZAN_TEXT = nodes[10].find_element_by_xpath(".//a[@action-type='feed_list_like']").text #可为空
            if ZAN_TEXT == '':
                ZAN = 0
            else:
                ZAN = int(ZAN_TEXT)
        except:
            ZAN = 0
        # print('赞:', ZAN)
        # dic[i].append(ZAN)
        # print('\n')

    # 写入Excel
    writeXLS(dic)


# *******************************************************************************
#                                程序入口
# *******************************************************************************
if __name__ == '__main__':
    all_txt = [f for f in os.listdir('./') if 'txt' in f]
    for txt in all_txt:
        # 计算关键词
        keywords = []
        with open(txt,"r", encoding='utf-8') as f:
            text = ''
            lines = f.readlines()
            for line in lines:
                text = text + line
            text = re.sub(r'( \| cid \| : \| .* \| )', '', text)
            keywords = jieba.analyse.extract_tags(text, topK=5)

        # global outfile
        # outfile = xlwt.Workbook(encoding='utf-8')
        # global sheet
        # sheet = outfile.add_sheet('内容')
        global file_name
        file_name = txt.replace('txt', 'CSV')
        initCSV()

        # 定义变量
        username = '13375921262'  # 输入你的用户名
        password = 'VTA-a72-Rs0-9K3'  # 输入你的密码

        # 操作函数
        LoginWeibo(username, password)  # 登陆微博
        for key in keywords:
            GetSearchContent(key)
