#coding=utf-8

import requests
import re
import checkPage
from threading import Thread
import time

from requests import ReadTimeout,ConnectionError

#时间限制
class TimeoutException(Exception):
  pass
ThreadStop = Thread._Thread__stop
def timelimited(timeout):
  def decorator(function):
    def decorator2(*args,**kwargs):
      class TimeLimited(Thread):
        def __init__(self,_error= None,):
          Thread.__init__(self)
          self._error = _error
        def run(self):
          try:
            self.result = function(*args,**kwargs)
          except Exception,e:
            self._error = str(e)
        def _stop(self):
          if self.isAlive():
            ThreadStop(self)
      t = TimeLimited()
      t.start()
      t.join(timeout)
      if isinstance(t._error,TimeoutException):
        t._stop()
        raise TimeoutException('timeout for %s' % (repr(function)))
      if t.isAlive():
        t._stop()
        raise TimeoutException('timeout for %s' % (repr(function)))
      if t._error is None:
        return t.result
    return decorator2
  return decorator

#验证输入的url是否可正常链接
def url_get(geturl):
    url=geturl
    try:
        kv={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'}
        requests.get(url,headers=kv,timeout=2)
        return url
    except:
        return 0
    

#根据传入的URL参数进行爬取，以列表形式返回
@timelimited(2)
def spiderPage(url):
    try:
        kv = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER'}
        r=requests.get(url,headers=kv,timeout=2)
        r.encoding=r.apparent_encoding
        pagetext=r.text
        pagelinks=re.findall(r'(?<=<a href=\").*?(?=\")|(?<=href=\').*?(?=\')', pagetext)
        return pagelinks
    except (ConnectionError, ReadTimeout):
        return 0

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
    pattern3=re.compile("jpg|pdf|doc|mp3|png|xls|ppt|zip|rar|xml")
    for l in pagelinks:
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
        return len(sef.unvisited)==0

class Spider():
    def __init__(self,url):
        #将队列引入本类
        self.linkQuence=linkQuence()
        #传入待爬取的url
        self.linkQuence.addunvisitedurl(url)

    #爬虫
    def crawler(self,urlcount,officialWeb):
        #子页面过多，为测试方便加入循环控制子页面数量
        x=1
        #无效网页计数
        while x<=urlcount:
            if x>1:
                print ("now from %d url  craw" % (x-1))
            #从未访问的列表中pop一个
            visitedurl=self.linkQuence.unvisitedurldequence()
            # x+=1
            #简单处理url问题
            print visitedurl
            if visitedurl is None or visitedurl =='':
                break
            if visitedurl in self.linkQuence.visited:
                continue
            if url_get(visitedurl)==0:
                continue
            #判断是否是需要的页面
            checkPage.checkMain(visitedurl)
            #爬取该url页面中所有的链接
            try:
                initial_links=spiderPage(visitedurl)
            except TimeoutException as e:
                print u"超时不要了"
                continue
            # print initial_links
            if initial_links==0:
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
    url=url_get(weburl)
    spider=Spider(url)
    urllist=spider.crawler(num,weburl)
    elapsed = (time.clock() - start)
    print("Time used:",elapsed)

startCrawer('http://spb.cq.gov.cn',1000)