#-*-  coding:utf-8 -*-
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import re,Queue,pdfkit,time
from PyPDF2 import PdfFileMerger
#多线程
from threading import Thread
import threading
#使用selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

#设置浏览器
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')
prefs = {"profile.managed_default_content_settings.images":2}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)

#链接队列
linkQuence=Queue.Queue()

#统计已访问链接数
num=0
def addnum():
  global num
  numlock.acquire()
  num+=1
  print (u"正在访问第 %d 个页面" %num)
  numlock.release()

#访问过的链接列表
visitedLink=[]
def addLinkToList(url):
  global visitedLink
  listlock.acquire()
  visitedLink.append(url)
  listlock.release()

#时间限制装饰器
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
    pattern3=re.compile("javascript|jpg|pdf|doc|mp3|png|xls|ppt|zip|rar|xml|css|js",re.I)
    #不要JavaScript字段
    pattern8=re.compile("javascript|#")
    for link in pagelinks:
      try:
        l=link.get_attribute('href')
        #只有官网加/的不要
        if l!=(officialWeb+'/') or l!=(officialWeb+'/index.html'):
          if pattern8.search(l)==None:
            if pattern3.search(l,re.I)==None:
              if pattern1.match(l,re.I)!=None:
                  link=officialWeb+l[1:]
                  same_target_url.append(link)
              elif pattern2.match(l)!=None and pattern5.match(l)==None:
                  link=officialWeb+l
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


#链接搜索
@timelimited(7)
def getPageLink(url,officialWeb):
  try:
    #隐性等待
    driver.implicitly_wait(5)
    driver.get(url)
    #获取官网页面的链接并格式化链接
    initial_links=driver.find_elements_by_tag_name("a")
    right_links = url_filtrate(initial_links,officialWeb)
    #放入队列中
    for link in right_links:
      linkQuence.put(link)
    #检查页面内容
    if checkPage(driver.page_source)==1:
      try:
        save_pdf(url,'acs.pdf')
        os.rename('acs.pdf',driver.title+'.pdf')
      except:
        os.rename('acs.pdf',driver.title+'.pdf')
        print u"pdf转换出错"
    else:
      print u"页面不符合"
  except:
    print u"获取页面失败"


#页面检查
def checkPage(pageContent):
  #匹配主要字段
  param_one=u"县.*?年.*?预算执行情况.*?预算|区.*?年.*?预算执行情况.*?预算|市.*?年.*?预算执行情况.*?预算"
  pattern_one = re.compile(param_one)
  match_one=pattern_one.findall(driver.page_source)
  #主要字段只有一次，匹配更多字段
  pattern_two=re.compile(u"一般公共预算")
  match_two=pattern_two.findall(driver.page_source)
  pattern_three=re.compile(u"预算草案")
  match_three=pattern_three.findall(driver.page_source)
  #匹配信息公开类型
  pattern_four=re.compile(u"预.*?算信息公开|预.*?算公开信息")
  match_four=pattern_four.findall(driver.page_source)
  if len(match_one)!=0:
      if len(match_one)>=2:
          return 1
      elif len(match_two)!=0 and len(match_three)!=0:
          return 1
      elif len(match_four)!=0:
          return 1
      else:
          return 0
  else:
      return 0

#pdf转换
def save_pdf(htmls, file_name):
    #添加了环境变量还是搞不成，只有代码找位置
    path_wk = r'D:\wkhtmltox\bin\wkhtmltopdf.exe' #安装位置
    config = pdfkit.configuration(wkhtmltopdf = path_wk)
    try:
      pdfkit.from_url(htmls, file_name,configuration=config)
    except:
      print u"pdf转换有问题"

#爬虫
def Spider(officialWeb):
  try:
    while linkQuence.empty!=True:
      visitUrl=linkQuence.get(block=False)
      if visitUrl in visitedLink:
        continue
      # addnum()
      else:
        addLinkToList(visitUrl)
        print visitUrl
        try:
          getPageLink(visitUrl,officialWeb)
        except:
          continue
  except:
    fo = open("url.txt", "w+")
    for link in visitedLink:
      fo.writelines(link+'/n')
    fo.close()
    print u"链接访问结束"

#多线程爬虫
def threadSpider(number,officialWeb):
  for i in range(number):
    t = Thread(target=Spider,args=(officialWeb,))
    t.start()
    t.join()

def start(url,number):
  startTime = time.clock()
  try:
    driver.implicitly_wait(5)
    driver.get(url)
  except:
    print u"获取页面失败"
  #获取官网页面的链接并格式化链接
  initial_links=driver.find_elements_by_tag_name("a")
  right_links = url_filtrate(initial_links,url)
  for link in right_links:
    linkQuence.put(link)
  #设置线程数和启动多线程
  threadSpider(number,url)
  elapsed = (time.clock() - startTime)
  print("Time used:",elapsed)
  driver.quit()

if __name__ == '__main__':
  #创建一把同步锁
  numlock = threading.Lock() 
  listlock= threading.Lock() 
  start('http://guokunjin.cn',10)


