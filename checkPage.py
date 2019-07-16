#coding=utf-8

import urllib
import urllib2
import re
import os
import time
import pdfkit
from PyPDF2 import PdfFileMerger
from threading import Thread
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

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

#爬取页面

class searchPage:
    #初始化链接组合
    def __init__(self,baseUrl):
        self.baseUrl=baseUrl
    
    #页面内容匹配
    def matchContent(self):
        try:
            url=self.baseUrl
            #爬取超时就不要了
            try:
                request=urllib2.Request(url)
                response=urllib2.urlopen(request,timeout=3)
            except Exception,e:
                return 0
            string=response.read()
            try:
              htmlTitle = re.search(r"<title>.*?</title>", string.decode('utf-8'),re.I|re.S)
            except:
              print u"标题匹配有问题,暂且叫不符合"
              return 0
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : user_agent }
            #匹配“xx年财政预算执行情况和xx年财政预算”
            title="县.*?年.*?预算执行情况|区.*?年.*?预算执行情况|市.*?年.*?预算执行情况"
            pattern_title = re.compile(title)
            match_title=pattern_title.findall(string)
            # print len(match_title)
            # 页面存在一次题目
            if len(match_title)!=0:
                if len(match_title)>=2:
                    return htmlTitle.group()[7:-8]
                #匹配预算信息公开
                param_three="预.*?算信息公开|预.*?算公开信息"
                pattern_three=re.compile(param_three)
                match_three=pattern_three.findall(string)
                if len(match_three)!=0:
                  return htmlTitle.group()[7:-8]
                #匹配“xx年财政预算执行情况”大于等于2次
                param_one=u"(预算执行情况+)"
                pattern_one = re.compile(param_one)
                match_one=pattern_one.findall(string)
                if len(match_one)>=2:
                    #匹配“xx年财政预算草案”
                    param_two=u"(预算草案+)"
                    pattern_two = re.compile(param_two)
                    match_two=pattern_two.findall(string)
                    if len(match_two)>=2:
                        return htmlTitle.group()[7:-8]
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        #连接错误
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print("连接失败",e.reason)
                return None

#html转化为pdf
def save_pdf(htmls, file_name):
    #添加了环境变量还是搞不成，只有代码找位置
    path_wk = r'D:\wkhtmltox\bin\wkhtmltopdf.exe' #安装位置
    config = pdfkit.configuration(wkhtmltopdf = path_wk)
    try:
      pdfkit.from_url(htmls, file_name,configuration=config)
    except:
      print u"pdf转换有问题"

#爬虫开始
@timelimited(10)
def start(url):
    #对象实例化
    sp=searchPage(url)
    fileTitle=sp.matchContent()
    if fileTitle!=0 and fileTitle!=None:
        #由于pdfkit直接生成中文名出错，所以生产后改名字
        fileName='acs.pdf'
        try:
          save_pdf(url,fileName)
          os.rename('acs.pdf',fileTitle+'.pdf')
        except:
          os.rename('acs.pdf',fileTitle+'.pdf')
    else:
        print u'页面不符合'
    

def checkMain(url):
    try:
        start(url)
    except TimeoutException as e:
        print u"超时不要了"

# checkMain('http://www.cqna.gov.cn/Item/89067.aspx')



