#coding=utf-8

import urllib
import urllib2
import re
import os
import pdfkit
from PyPDF2 import PdfFileMerger
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#爬取页面
class searchPage:
    #初始化链接组合
    def __init__(self,baseUrl):
        self.baseUrl=baseUrl
    
    #页面标题直接匹配
    def matchTitle(self):
        try:
            url=self.baseUrl
            request=urllib2.Request(url)
            response=urllib2.urlopen(request)
            string=response.read().decode('utf-8')
            htmlTitle = re.search(r"<title>.*</title>", string)
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : user_agent }
            #匹配“xx年财政预算执行情况和xx年财政预算”
            title=u"(2018年财政预算执行情况和2019年财政预算+)"
            pattern_title = re.compile(title)
            match_title=pattern_title.findall(string) 
            #匹配数大于等于2表示匹配成功
            if len(match_title)>=2:
                return htmlTitle.group()[7:-8]
            else:
                return 0
        #连接错误
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print("连接失败",e.reason)
                return None

    #页面内容匹配
    def matchContent(self):
        try:
            url=self.baseUrl
            request=urllib2.Request(url)
            response=urllib2.urlopen(request)
            string=response.read().decode('utf-8')
            htmlTitle = re.search(r"<title>.*</title>", string)
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : user_agent }
            #匹配“xx年财政预算执行情况和xx年财政预算”
            title=u"(2018年财政预算执行情况和2019年财政预算+)"
            pattern_title = re.compile(title)
            match_title=pattern_title.findall(string)
            #页面存在一次题目
            if len(match_title)!=0:
                #匹配“xx年财政预算执行情况”大于等于2次
                param_one=u"(2018年财政预算执行情况+)"
                pattern_one = re.compile(param_one)
                match_one=pattern_one.findall(string)
                if len(match_one)>=2:
                    #匹配“xx年财政预算草案”
                    param_two=u"(2019年财政预算草案+)"
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
    
    path_wk = r'D:\wkhtmltox\bin\wkhtmltopdf.exe' #安装位置
    config = pdfkit.configuration(wkhtmltopdf = path_wk)
    pdfkit.from_url(htmls, file_name,configuration=config)

#主函数
def start(url):
    #对象实例化
    sp=searchPage(url)
    fileTitle=''
    #两个判定条件
    if sp.matchTitle()!=0:
        fileTitle=sp.matchTitle()
    elif sp.matchContent()!=0:
        fileTitle=sp.matchContent()
    else:
        pass
    if fileTitle!='':
        #由于pdfkit直接生成中文名出错，所以生产后改名字
        fileName='acs.pdf'
        save_pdf(url,fileName)
        os.rename('acs.pdf',fileTitle+'.pdf') 
    else:
        print '0'

start('http://www.quwo.gov.cn/contents/31310/553181.html')



