#-*-  coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import pdfkit
from PyPDF2 import PdfFileMerger
from threading import Thread
#导入webdriver
from selenium import webdriver
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import os
#要想调用键盘按键操作需要引入keys包
from selenium.webdriver.common.keys import Keys


#设置浏览器
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')  
prefs = {"profile.managed_default_content_settings.images":2}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)

#页面检验爬虫
class checkSpider:
    #初始化链接
    def __init__(self,baseUrl):
        self.baseUrl=baseUrl

    #检验方法
    def check(self):
        try:
            #隐性等待
            driver.implicitly_wait(3)
            #网址
            pattern3=re.compile("java|jpg|pdf|doc|mp3|png|xls|ppt|zip|rar|xml|css|js")
            if pattern3.search(self.baseUrl,re.I)==None:
                driver.get(self.baseUrl)
            else:
                return 0
        except:
            return 0
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
                return driver.title
            elif len(match_two)!=0 and len(match_three)!=0:
                return driver.title
            elif len(match_four)!=0:
                return driver.title
            else:
                return 0
        else:
            return 0

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

#pdf转换
def save_pdf(htmls, file_name):
    #添加了环境变量还是搞不成，只有代码找位置
    path_wk = r'D:\wkhtmltox\bin\wkhtmltopdf.exe' #安装位置
    config = pdfkit.configuration(wkhtmltopdf = path_wk)
    try:
      pdfkit.from_url(htmls, file_name,configuration=config)
    except:
      print u"pdf转换有问题"

#检验爬虫开始
@timelimited(5)
def start(url):
    #对象实例化
    sp=checkSpider(url)
    fileTitle=sp.check()
    if fileTitle!=0 and fileTitle!=None:
        #由于pdfkit直接生成中文名出错，所以生产后改名字
        fileName='acs.pdf'
        save_pdf(url,fileName)
        os.rename('acs.pdf',fileTitle+'.pdf')
    else:
        print u'页面不符合'

def checkMain(url):
    try:
        start(url)
    except TimeoutException as e:
        print u"超时不要了"

# checkMain('http://www.linan.gov.cn/art/2019/3/12/art_1379508_30980916.html')