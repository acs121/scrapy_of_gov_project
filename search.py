#coding=utf-8

import requests
import re
import check
from threading import Thread
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#设置浏览器
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')
prefs = {"profile.managed_default_content_settings.images":2}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)

#队列，实现将url集合分为未访问和已访问两类，当前未访问集合为空时结束循环功能
class linkQuence:
    def __init__(self):
        #已访问集合
        self.visited=[]
        #待访问集合
        self.unvisited=[]

    #获取访问过的url队列
    def getvisitedurl(self):
        return self.visited

    #获取未访问的url队列
    def getunvisitedurl(self):
        return self.unvisited

    #添加url到访问过的队列中
    def addvisitedurl(self,url):
        return self.visited.append(url)

    #移除访问过的url
    def removevisitedurl(self,url):
        return self.visited.remove(url)

    #从未访问的url中提起一个url
    def unvisitedurldequence(self):
        try:
            return self.unvisited.pop()
        except:
            print u"队列中没有链接"
            return None
    
    #添加url到未访问队列中
    def addunvisitedurl(self,url):
        if url !="" and url not in self.visited and url not in self.unvisited:
            return self.unvisited.insert(0,url)

    #获取已访问的url数目
    def getvisitedurlcount(self):
        return len(self.visited)

    #获取未访问的url数目
    def getunvisitedurlcount(self):
        return len(self.unvisited)

    #判断未访问的url队列是否为空
    def unvisitedurlempty(self):
        if len(self.unvisited)==0:
            return 0
        else:
            return 1

#对爬取的url去重，传入的参数为列表形式的Url集合,返回的是符合条件的URL集合
def url_filtrate(pagelinks,officialWeb):
    # 设置链接匹配格式
    same_target_url = []
    # 只要官网下的网站
    #以./开头
    pattern1=re.compile("./")
    #以/开头，不要//开头
    pattern2=re.compile("/")
    pattern5=re.compile("//")
    #如果以http开头了就需要求网址包含官网
    pattern4=re.compile(officialWeb)
    #以直接字母开头，不能是http
    pattern6=re.compile('[a-z]',re.I)
    pattern7=re.compile('http',re.I)
    #不要图片、pdf、doc等链接
    pattern3=re.compile("javascript|jpg|pdf|doc|mp3|png|xls|ppt|zip|rar|xml|css|js")
    #不要JavaScript字段
    pattern8=re.compile("javascript")
    for link in pagelinks:
        try:
            l=link.get_attribute('href')
            if pattern8.search(l)==None:
                if pattern3.search(l,re.I)==None:
                    if pattern1.match(l,re.I)!=None:
                        link=officialWeb+l[1:]
                        same_target_url.append(link)
                    elif pattern2.match(l)!=None and pattern5.match(l)==None:
                        link=officialWeb+l[0:]
                        same_target_url.append(link)
                    elif pattern6.match(l)!=None and pattern7.match(l)==None:
                        link=officialWeb+'/'+l
                        same_target_url.append(link)
                    elif pattern4.search(l)!=None:
                        same_target_url.append(l)
                    else:
                        pass
                else:
                    pass
        except:
            pass
    # 去除重复url
    unrepect_url = []
    for l in same_target_url:
        if l not in unrepect_url:
            unrepect_url.append(l)
    return unrepect_url

#搜索爬虫
class searchSpider:
    def __init__(self,url):
        #将队列引入本类
        self.linkQuence=linkQuence()
        #传入待爬取的url
        self.linkQuence.addunvisitedurl(url)

    #爬取过程
    def craw(self,urlcount,officialWeb):
        #子页面过多，为测试方便加入循环控制子页面数量
        x=1
        #无效网页计数
        while self.linkQuence.unvisitedurlempty()!=0:
            if x>1:
                print ("now from %d url  craw" % (x-1))
            #从未访问的列表中pop一个
            visitedurl=self.linkQuence.unvisitedurldequence()
            #简单处理url问题
            print visitedurl
            if visitedurl is None or visitedurl =='':
                print u"网站链接已找完"
                break
            if visitedurl in self.linkQuence.visited:
                continue
            try:
                #隐性等待
                driver.implicitly_wait(5)
                #网址
                driver.get(visitedurl)
            except:
                continue
            #判断是否是需要的页面
            check.checkMain(visitedurl)
            #爬取该url页面中所有的链接
            try:
                initial_links=driver.find_elements_by_tag_name("a")
            except:
                continue
            #筛选出合格的链接
            right_links = url_filtrate(initial_links,officialWeb)
            # print right_links
            #将该url放到访问过的url队列中
            self.linkQuence.addvisitedurl(visitedurl)
            #将筛选出的链接放到未访问队列中
            for link in right_links:
                self.linkQuence.addunvisitedurl(link)
            x+=1
        print("over total %durls" % (x-2))
        return self.linkQuence.visited

#启动爬虫
def startCrawer(weburl,num):
    start = time.clock()
    spider=searchSpider(weburl)
    urllist=spider.craw(num,weburl)
    elapsed = (time.clock() - start)
    print("Time used:",elapsed)

startCrawer('http://www.linan.gov.cn',3000)
