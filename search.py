#coding=utf-8

import requests
import re

from requests import ReadTimeout,ConnectionError
# from __future__ import print_function

#验证输入的url是否可正常链接
def url_get(geturl):
    url=geturl
    try:
        kv={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'}
        requests.get(url,headers=kv)
        return url
    except:
        return 0
    

#根据传入的URL参数进行爬取，以列表形式返回
def spiderPage(url):
    try:
        kv = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'}
        r=requests.get(url,headers=kv,timeout=0.1)
        r.encoding=r.apparent_encoding
        pagetext=r.text
        pagelinks=re.findall(r'(?<=<a href=\").*?(?=\")|(?<=href=\').*?(?=\')', pagetext)
        return pagelinks
    except (ConnectionError, ReadTimeout):
        return 0


#对爬取的url去重，传入的参数为列表形式的Url集合,返回的是符合条件的URL集合
def url_filtrate(pagelinks):
    # 去除不是以要爬取网站开头的url,如跳转的广告等
    same_target_url = []
    for l in pagelinks:
        if re.findall(r'blog.csdn.net/\w+/article/details/\d+', l):
            # 根据对网页的分析添加筛选条件,过滤掉系统推荐的博文链接
            if re.findall(r'blockchain_lemon', l):
                pass
            # 过滤掉广告链接
            elif re.findall(r'passport', l):
                pass
            else:
                same_target_url.append(l)
    # 去除重复url
    unrepect_url = []
    for l in same_target_url:
        if l not in unrepect_url:
            unrepect_url.append(l)
    return unrepect_url

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
        return len(sef.unvisited)==0

class Spider():
    def __init__(self,url):
        #将队列引入本类
        self.linkQuence=linkQuence()
        #传入待爬取的url
        self.linkQuence.addunvisitedurl(url)

    #爬虫
    def crawler(self,urlcount):
        #子页面过多，为测试方便加入循环控制子页面数量
        x=1
        while x<=urlcount:
            if x>1:
                print ("now from %d url  craw" % (x-1))
            #从未访问的列表中pop一个
            visitedurl=self.linkQuence.unvisitedurldequence()
            if url_get(visitedurl)==0:
                continue
            if visitedurl is None or visitedurl =='':
                continue
            print visitedurl
            #爬取该url页面中所有的链接
            initial_links=spiderPage(visitedurl)
            if initial_links==0:
                continue
            #筛选出合格的链接
            # right_links = url_filtrate(initial_links)
            #将该url放到访问过的url队列中
            self.linkQuence.addvisitedurl(visitedurl)
            
            #将筛选出的链接放到未访问队列中
            for link in initial_links:
                self.linkQuence.addunvisitedurl(link)
            x+=1
        print("over total %durls" % (x-2))
        return self.linkQuence.visited

#将爬取到的子链接全部写入本地文件
def writeinfile(list):
    #第一个不写，从[1]开始
    x=1
    for url in list[1:]:
        urlsfile=open('./urls.txt','a',encoding='utf-8')
        urlsfile.write(url+"\n")
        x+=1
    urlsfile.close()
    print("write over total %d urls" %(x-1))

#启动爬虫
url=url_get('http://www.pingshun.gov.cn/')
spider=Spider(url)
urllist=spider.crawler(10)
# writeinfile(urllist)

